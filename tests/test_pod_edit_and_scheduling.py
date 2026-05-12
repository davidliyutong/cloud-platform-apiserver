"""
Tests for: editing stopped-pod specs, quota enforcement on edits, and the
scheduling-failure reason extraction.
"""
import uuid
from types import SimpleNamespace

from src.apiserver.controller.types import PodUpdateRequest
from src.apiserver.service.operator import K8SOperatorService
from src.apiserver.service.pod import PodService, ModeEnum
from src.components import datamodels


def _new_user(
        cpu_m: int = 8000,
        memory_mb: int = 16384,
        storage_mb: int = 51200,
        gpu: int = 0,
        pod_n: int = 10,
) -> datamodels.UserModel:
    return datamodels.UserModel.new(
        uid=1,
        username="user1",
        password="pass",
        role=datamodels.UserRoleEnum.user,
        quota={
            "cpu_m": cpu_m,
            "memory_mb": memory_mb,
            "storage_mb": storage_mb,
            "gpu": gpu,
            "network_mb": 0,
            "pod_n": pod_n,
        },
    )


def _new_pod(
        cpu: int = 1000,
        mem: int = 1024,
        storage: int = 10240,
        gpu: int = 0,
        status: datamodels.PodStatusEnum = datamodels.PodStatusEnum.stopped,
        pod_id: str = None,
) -> datamodels.PodModel:
    pod = datamodels.PodModel.new(
        template_ref=str(uuid.uuid4()),
        username="user1",
        user_uuid=str(uuid.uuid4()),
        cpu_lim_m_cpu=cpu,
        mem_lim_mb=mem,
        storage_lim_mb=storage,
        gpu=gpu,
    )
    pod.current_status = status
    if pod_id is not None:
        pod.pod_id = pod_id
    return pod


def _update_req(
        pod_id: str,
        target_status: datamodels.PodStatusEnum = None,
        cpu: int = None,
        mem: int = None,
        storage: int = None,
        gpu: int = None,
) -> PodUpdateRequest:
    return PodUpdateRequest(
        pod_id=pod_id,
        cpu_lim_m_cpu=cpu,
        mem_lim_mb=mem,
        storage_lim_mb=storage,
        gpu=gpu,
        target_status=target_status,
    )


def test_check_quota_update_storage_exceeded_even_when_not_starting():
    """Storage is charged regardless of running state — editing a stopped pod's
    storage must respect the storage quota."""
    user = _new_user(storage_mb=20480)
    pod = _new_pod(storage=10240, status=datamodels.PodStatusEnum.stopped, pod_id="a")
    other = _new_pod(storage=10240, status=datamodels.PodStatusEnum.stopped, pod_id="b")
    req = _update_req("a", storage=20480)  # 20G + 10G > 20G quota

    assert PodService.check_quota(user, [pod, other], req, mode=ModeEnum.update) is False


def test_check_quota_update_storage_ok_when_within_limit():
    user = _new_user(storage_mb=20480)
    pod = _new_pod(storage=10240, status=datamodels.PodStatusEnum.stopped, pod_id="a")
    req = _update_req("a", storage=15360)

    assert PodService.check_quota(user, [pod], req, mode=ModeEnum.update) is True


def test_check_quota_update_running_counts_other_running_pods_only():
    """When the user starts a pod, the requested cpu/mem must fit alongside
    pods that are already running — not stopped ones."""
    user = _new_user(cpu_m=4000, memory_mb=8192)
    running = _new_pod(cpu=2000, mem=4096, status=datamodels.PodStatusEnum.running, pod_id="r")
    stopped = _new_pod(cpu=3000, mem=4096, status=datamodels.PodStatusEnum.stopped, pod_id="s")
    target = _new_pod(cpu=1000, mem=1024, status=datamodels.PodStatusEnum.stopped, pod_id="t")
    # starting 't' with 2000m / 4096Mi -> total running becomes 4000m / 8192Mi (== quota, allowed)
    req = _update_req("t", cpu=2000, mem=4096, target_status=datamodels.PodStatusEnum.running)

    assert PodService.check_quota(user, [running, stopped, target], req, mode=ModeEnum.update) is True


def test_check_quota_update_running_rejects_over_cpu():
    user = _new_user(cpu_m=4000)
    running = _new_pod(cpu=3000, status=datamodels.PodStatusEnum.running, pod_id="r")
    target = _new_pod(cpu=1000, status=datamodels.PodStatusEnum.stopped, pod_id="t")
    req = _update_req("t", cpu=2000, target_status=datamodels.PodStatusEnum.running)

    assert PodService.check_quota(user, [running, target], req, mode=ModeEnum.update) is False


def test_check_quota_update_running_excludes_self_from_running_total():
    """When a pod is already running and gets re-applied, it should not be
    double-counted against the quota."""
    user = _new_user(cpu_m=4000)
    target = _new_pod(cpu=2000, status=datamodels.PodStatusEnum.running, pod_id="t")
    other_running = _new_pod(cpu=2000, status=datamodels.PodStatusEnum.running, pod_id="o")
    req = _update_req("t", cpu=2000, target_status=datamodels.PodStatusEnum.running)

    # other (2000) + req (2000) == 4000 quota, allowed
    assert PodService.check_quota(user, [target, other_running], req, mode=ModeEnum.update) is True


def test_pod_model_current_status_reason_default_is_none():
    pod = _new_pod()
    assert pod.current_status_reason is None


def test_pod_model_upgrade_backfills_status_reason():
    """Existing rows that don't have the new field should not blow up."""
    user = _new_user()
    legacy = datamodels.PodModel.new(
        template_ref=str(uuid.uuid4()),
        username="user1",
        user_uuid=str(user.uuid),
        cpu_lim_m_cpu=1000,
        mem_lim_mb=1024,
        storage_lim_mb=10240,
    ).model_dump()
    legacy.pop("current_status_reason", None)

    pod = datamodels.PodModel.upgrade(legacy)
    assert pod.current_status_reason is None


# --- scheduling failure reason extraction -------------------------------------


def _make_operator_stub(items):
    """Build a K8SOperatorService instance without going through __init__."""
    op = K8SOperatorService.__new__(K8SOperatorService)
    op.namespace = "test-ns"
    op.v1 = SimpleNamespace(
        list_namespaced_pod=lambda namespace, label_selector: SimpleNamespace(items=items)
    )
    return op


def _pod_with_unschedulable(message: str):
    return SimpleNamespace(
        status=SimpleNamespace(
            conditions=[SimpleNamespace(type="PodScheduled", status="False",
                                        reason="Unschedulable", message=message)],
            container_statuses=None,
        )
    )


def _pod_with_image_pull_error(message: str):
    waiting = SimpleNamespace(reason="ImagePullBackOff", message=message)
    state = SimpleNamespace(waiting=waiting)
    return SimpleNamespace(
        status=SimpleNamespace(
            conditions=[],
            container_statuses=[SimpleNamespace(state=state)],
        )
    )


def test_get_pod_failure_reason_reports_insufficient_memory():
    import asyncio

    op = _make_operator_stub([
        _pod_with_unschedulable("0/3 nodes are available: 3 Insufficient memory.")
    ])

    reason = asyncio.get_event_loop().run_until_complete(op.get_pod_failure_reason("pid"))
    assert reason is not None
    assert "Unschedulable" in reason
    assert "Insufficient memory" in reason


def test_get_pod_failure_reason_reports_image_pull():
    import asyncio

    op = _make_operator_stub([
        _pod_with_image_pull_error("Back-off pulling image \"nope:latest\"")
    ])

    reason = asyncio.get_event_loop().run_until_complete(op.get_pod_failure_reason("pid"))
    assert reason is not None
    assert "ImagePullBackOff" in reason


def test_get_pod_failure_reason_none_when_healthy():
    import asyncio

    healthy = SimpleNamespace(
        status=SimpleNamespace(
            conditions=[SimpleNamespace(type="PodScheduled", status="True",
                                        reason=None, message=None)],
            container_statuses=None,
        )
    )
    op = _make_operator_stub([healthy])

    reason = asyncio.get_event_loop().run_until_complete(op.get_pod_failure_reason("pid"))
    assert reason is None
