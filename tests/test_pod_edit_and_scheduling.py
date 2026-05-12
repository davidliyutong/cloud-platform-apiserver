"""
Tests for: editing stopped-pod specs, quota enforcement on edits, and the
scheduling-failure reason extraction.
"""
import asyncio
import uuid
from types import SimpleNamespace

from src.apiserver.controller.types import PodUpdateRequest
from src.apiserver.service.operator import K8SOperatorService
from src.apiserver.service.pod import PodService, ModeEnum
from src.components import datamodels, errors


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
        gpu: int = None,
) -> PodUpdateRequest:
    return PodUpdateRequest(
        pod_id=pod_id,
        cpu_lim_m_cpu=cpu,
        mem_lim_mb=mem,
        gpu=gpu,
        target_status=target_status,
    )


def test_update_request_rejects_storage_change():
    """Storage is immutable after pod creation; the request validator must reject it."""
    import pytest
    with pytest.raises(Exception):
        PodUpdateRequest(pod_id="a", storage_lim_mb=20480)


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


# --- spec-edit guard ----------------------------------------------------------


class _FakePodRepo:
    def __init__(self, pod):
        self._pod = pod

    async def get(self, pod_id):
        return self._pod, None

    async def list(self, extra_query_filter=None):
        return 1, [self._pod], None

    async def update(self, **kwargs):  # pragma: no cover - shouldn't be reached on guarded paths
        raise AssertionError("repo.update must not be called when the guard rejects the request")


class _FakeUserRepo:
    def __init__(self, user):
        self._user = user

    async def get(self, username):
        return self._user, None


class _FakeApp:
    async def add_task(self, *_a, **_kw):  # pragma: no cover
        pass


def _make_service(user, pod):
    service = PodService.__new__(PodService)
    service.repo = _FakePodRepo(pod)
    service.parent = SimpleNamespace(
        user_service=SimpleNamespace(repo=_FakeUserRepo(user)),
        pod_service=SimpleNamespace(repo=service.repo),
    )
    return service


def _spec_update_req(pod_id, force=False):
    return PodUpdateRequest(
        pod_id=pod_id,
        cpu_lim_m_cpu=2000,
        mem_lim_mb=2048,
        force=force,
    )


def test_spec_edit_rejected_on_running_pod_even_with_force():
    """Force (admin) does not bypass the stopped-only guard — editing a
    running pod's spec is ambiguous against the live deployment."""
    user = _new_user()
    pod = _new_pod(status=datamodels.PodStatusEnum.running, pod_id="p1")
    service = _make_service(user, pod)

    req = _spec_update_req("p1", force=True)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )
    assert result is None
    assert err is errors.pod_not_stopped


def test_spec_edit_rejected_on_running_pod_for_user():
    user = _new_user()
    pod = _new_pod(status=datamodels.PodStatusEnum.running, pod_id="p1")
    service = _make_service(user, pod)

    req = _spec_update_req("p1", force=False)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )
    assert result is None
    assert err is errors.pod_not_stopped


# --- template_ref switch -------------------------------------------------------


class _RecordingPodRepo:
    """Like _FakePodRepo but records update kwargs and actually returns the updated pod."""

    def __init__(self, pod):
        self._pod = pod
        self.last_update_kwargs = None

    async def get(self, pod_id):
        return self._pod, None

    async def list(self, extra_query_filter=None):
        return 1, [self._pod], None

    async def update(self, **kwargs):
        self.last_update_kwargs = kwargs
        # Build updated pod reflecting the new values.
        pod_dict = self._pod.model_dump(mode='python')
        for key, value in kwargs.items():
            if value is not None and key not in ('clear_status_reason',):
                pod_dict[key] = value
        if kwargs.get('clear_status_reason'):
            pod_dict['current_status_reason'] = None
        pod_dict.setdefault('resource_status', 'pending')
        pod_dict['resource_status'] = 'pending'
        updated = datamodels.PodModel(**pod_dict)
        return updated, None


class _FakeTemplateRepo:
    def __init__(self, template_id, committed=True):
        self._template_id = template_id
        self._status = (datamodels.ResourceStatusEnum.committed
                        if committed else datamodels.ResourceStatusEnum.pending)

    async def get(self, template_id):
        if template_id == self._template_id:
            from types import SimpleNamespace as _SN
            return _SN(resource_status=self._status), None
        from src.components import errors as _errors
        return None, _errors.template_not_found


def _make_service_with_template(user, pod, new_template_id, committed=True):
    service = PodService.__new__(PodService)
    pod_repo = _RecordingPodRepo(pod)
    service.repo = pod_repo
    service.parent = SimpleNamespace(
        user_service=SimpleNamespace(repo=_FakeUserRepo(user)),
        pod_service=SimpleNamespace(repo=pod_repo),
        template_service=SimpleNamespace(repo=_FakeTemplateRepo(new_template_id, committed)),
    )
    return service


def test_template_ref_switch_updates_db_field():
    """Switching template_ref on a stopped pod must persist the new UUID."""
    user = _new_user()
    old_template_id = str(uuid.uuid4())
    new_template_id = str(uuid.uuid4())
    pod = _new_pod(pod_id="p1")
    pod.template_ref = uuid.UUID(old_template_id)
    pod.current_status = datamodels.PodStatusEnum.stopped

    service = _make_service_with_template(user, pod, new_template_id, committed=True)

    req = PodUpdateRequest(pod_id="p1", template_ref=new_template_id)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )

    assert err is None, f"unexpected error: {err}"
    assert result is not None
    # The new template_ref must be reflected on the returned pod.
    assert str(result.template_ref) == new_template_id
    # repo.update must have received the new template_ref string, not None.
    assert service.repo.last_update_kwargs is not None
    assert service.repo.last_update_kwargs.get('template_ref') == new_template_id


def test_template_ref_switch_rejected_on_running_pod():
    """Switching template_ref on a running pod must be rejected."""
    user = _new_user()
    new_template_id = str(uuid.uuid4())
    pod = _new_pod(pod_id="p1", status=datamodels.PodStatusEnum.running)

    service = _make_service_with_template(user, pod, new_template_id, committed=True)

    req = PodUpdateRequest(pod_id="p1", template_ref=new_template_id)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )

    assert result is None
    assert err is errors.pod_not_stopped


def test_template_ref_switch_rejected_when_template_not_committed():
    """Switching to a non-committed template must be rejected."""
    user = _new_user()
    new_template_id = str(uuid.uuid4())
    pod = _new_pod(pod_id="p1")
    pod.current_status = datamodels.PodStatusEnum.stopped

    service = _make_service_with_template(user, pod, new_template_id, committed=False)

    req = PodUpdateRequest(pod_id="p1", template_ref=new_template_id)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )

    assert result is None
    assert err is errors.template_not_committed


def test_template_ref_switch_rejected_when_template_not_found():
    """Requesting a non-existent template_ref must be rejected."""
    user = _new_user()
    new_template_id = str(uuid.uuid4())
    wrong_template_id = str(uuid.uuid4())
    pod = _new_pod(pod_id="p1")
    pod.current_status = datamodels.PodStatusEnum.stopped

    # fake repo only knows about wrong_template_id, not new_template_id
    service = _make_service_with_template(user, pod, wrong_template_id, committed=True)

    req = PodUpdateRequest(pod_id="p1", template_ref=new_template_id)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )

    assert result is None
    assert err is errors.template_not_found


def test_template_ref_same_value_is_noop():
    """Sending the same template_ref that is already set should not trigger an update."""
    user = _new_user()
    existing_template_id = str(uuid.uuid4())
    pod = _new_pod(pod_id="p1")
    pod.template_ref = uuid.UUID(existing_template_id)
    pod.current_status = datamodels.PodStatusEnum.stopped

    service = _make_service_with_template(user, pod, existing_template_id, committed=True)

    req = PodUpdateRequest(pod_id="p1", template_ref=existing_template_id)
    result, err = asyncio.get_event_loop().run_until_complete(
        service.update(_FakeApp(), req)
    )

    assert err is None
    # repo.update must have received template_ref=None (no-op — same value)
    assert service.repo.last_update_kwargs.get('template_ref') is None


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


# --- wait_pod error-type distinction -----------------------------------------


def _wait_pod_op_stub(deployment_status, pods):
    op = K8SOperatorService.__new__(K8SOperatorService)
    op.namespace = "test-ns"
    op.app_v1 = SimpleNamespace(
        read_namespaced_deployment_status=lambda *_a, **_kw: SimpleNamespace(
            status=deployment_status
        )
    )
    op.v1 = SimpleNamespace(
        list_namespaced_pod=lambda namespace, label_selector: SimpleNamespace(items=pods)
    )
    return op


def test_wait_pod_returns_k8s_pod_failed_on_terminal_failure():
    """Unschedulable -> early exit with k8s_pod_failed (not k8s_timeout)."""
    op = _wait_pod_op_stub(
        deployment_status=SimpleNamespace(replicas=1, ready_replicas=None),
        pods=[_pod_with_unschedulable("Insufficient memory")],
    )
    reason, err = asyncio.get_event_loop().run_until_complete(
        op.wait_pod("pid", datamodels.PodStatusEnum.running, timeout_s=5)
    )
    assert err is errors.k8s_pod_failed
    assert reason is not None
    assert "Insufficient memory" in reason


def test_wait_pod_returns_k8s_timeout_when_no_terminal_reason():
    """No terminal reason + deadline elapsed -> k8s_timeout with reason None."""
    op = _wait_pod_op_stub(
        deployment_status=SimpleNamespace(replicas=1, ready_replicas=None),
        pods=[],  # no pods visible, no reason to surface
    )
    reason, err = asyncio.get_event_loop().run_until_complete(
        op.wait_pod("pid", datamodels.PodStatusEnum.running, timeout_s=0)
    )
    assert err is errors.k8s_timeout
    assert reason is None


# --- error -> HTTP status mapping --------------------------------------------


def test_http_status_for_user_errors():
    import http as _http
    assert errors.http_status_for(errors.pod_not_stopped) == _http.HTTPStatus.BAD_REQUEST
    assert errors.http_status_for(errors.quota_exceeded) == _http.HTTPStatus.BAD_REQUEST
    assert errors.http_status_for(errors.pod_not_found) == _http.HTTPStatus.NOT_FOUND


def test_http_status_for_unknown_falls_back_to_500():
    import http as _http
    assert errors.http_status_for(Exception("totally unexpected")) == _http.HTTPStatus.INTERNAL_SERVER_ERROR
