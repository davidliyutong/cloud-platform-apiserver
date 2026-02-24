import uuid

from src.apiserver.controller.types import PodCreateRequest
from src.apiserver.service.pod import PodService, ModeEnum
from src.components import datamodels


def _new_user_with_gpu_quota(gpu_quota: int) -> datamodels.UserModel:
    return datamodels.UserModel.new(
        uid=1,
        username="user1",
        password="pass",
        role=datamodels.UserRoleEnum.user,
        quota={
            "cpu_m": 8000,
            "memory_mb": 16384,
            "storage_mb": 51200,
            "gpu": gpu_quota,
            "network_mb": 0,
            "pod_n": 10,
        },
    )


def _new_pod(gpu: int, status: datamodels.PodStatusEnum) -> datamodels.PodModel:
    pod = datamodels.PodModel.new(
        template_ref=str(uuid.uuid4()),
        username="user1",
        user_uuid=str(uuid.uuid4()),
        cpu_lim_m_cpu=1000,
        mem_lim_mb=1024,
        storage_lim_mb=10240,
        gpu=gpu,
    )
    pod.current_status = status
    return pod


def _new_create_request(gpu: int) -> PodCreateRequest:
    return PodCreateRequest(
        name="pod-new",
        description="",
        template_ref=str(uuid.uuid4()),
        cpu_lim_m_cpu=1000,
        mem_lim_mb=1024,
        storage_lim_mb=10240,
        gpu=gpu,
        username="user1",
    )


def test_gpu_quota_counts_running_pods_only():
    user = _new_user_with_gpu_quota(gpu_quota=3)
    pods = [
        _new_pod(gpu=2, status=datamodels.PodStatusEnum.running),
        _new_pod(gpu=4, status=datamodels.PodStatusEnum.stopped),
    ]
    req = _new_create_request(gpu=1)

    assert PodService.check_quota(user, pods, req, mode=ModeEnum.create) is True


def test_gpu_quota_exceeded_with_running_pods():
    user = _new_user_with_gpu_quota(gpu_quota=3)
    pods = [_new_pod(gpu=2, status=datamodels.PodStatusEnum.running)]
    req = _new_create_request(gpu=2)

    assert PodService.check_quota(user, pods, req, mode=ModeEnum.create) is False


def test_template_verify_allows_optional_pod_gpu_lim():
    template = datamodels.TemplateModel.new(
        name="t1",
        description="d",
        image_ref="nginx:latest",
        template_str=(
            "${{ POD_LABEL }} ${{ POD_ID }} ${{ POD_CPU_LIM }} "
            "${{ POD_MEM_LIM }} ${{ POD_STORAGE_LIM }} ${{ POD_REPLICAS }} ${{ TEMPLATE_IMAGE_REF }}"
        ),
        fields=None,
        defaults=None,
    )

    assert template.verify() is True
