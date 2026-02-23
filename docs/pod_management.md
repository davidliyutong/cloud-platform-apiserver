# Pod Management

This article describes how pods are managed by the controller

## Template Parameters

A template has the `template_str` attribute which is a template to be filled with parameters:

- `POD_POD_ID`: the ID of the pod
- `POD_CPU_LIM`: the cpu of the pod, e.g. 2
- `POD_MEM_LIM`: the memory of the pod, e.g. 2000MiB
- `POD_STORAGE_LIM`: the storage of the pod, e.g. 10000MiB
- `POD_AUTH`: the authentication secret of the pod, e.g. user-basic-auth
- `TEMPLATE_IMAGE_REF`: image reference
- `CONFIG_WORKSPACE_HOSTNAME`: a host name for workspace
- `CONFIG_WORKSPACE_TLS_SECRET`: a tls secret for workspace hostname

For example:

```json
{
        "POD_ID": "test_id",
        "POD_CPU_LIM": "2000m",
        "POD_MEM_LIM": "4096Mi",
        "POD_STORAGE_LIM": "10Mi",
        "POD_AUTH": "833c2ccc-afb6-4093-8f2c-ec1087c67d47-basic-auth",
        "TEMPLATE_IMAGE_REF": "davidliyutong/code-server-speit:latest",
        "CONFIG_WORKSPACE_HOSTNAME": "workspace.example.org",
        "CONFIG_WORKSPACE_TLS_SECRET": "workspace-tls-secret",
}

```

### What is happening

When a pod is created, the controller retrieve the template from database according to pod.template_ref. It then renders this template using pod values and server config values. Finally, it creates the pod using the rendered template.
