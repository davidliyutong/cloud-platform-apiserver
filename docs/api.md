# API List

## Auth APIs

This section describes all authentication APIs.

### JWT

#### POST /v1/auth/jwt/login

Login API. Accept `username` and `password`. Returns JSON web token if username and password passes authentication

- Request Header:

    ```conf
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "username": "username",
        "password": "password"
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey",
        "refresh_token": "xxx"
    }
    ```

#### POST /v1/auth/jwt/refresh

Refresh Token API. Accept token as input and return a refreshed token as output

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "refresh_token": "xxx"
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "expire":"2023-0700-00-00",
        "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey"
    }
    ```

### Basic

Basic API is provided for Ingress authentication

#### POST /v1/auth/basic

HTTP Basic Authentication. Accept `username` and `password`.

## Admin APIs

This section describes all admin APIs.

### User Management

This section describes admin APIs that manipulate user resource.

#### GET /v1/admin/users

List all users. If `uid_start` and `uid_end` are “greater than” 0, only users with `uid` between `uid_start`
and `uid_end` are returned. If `filter` is not empty, apply filter on results. This API returns profiles of users and
total number of users. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:
    ```
    ```


- Request Query:

    ```conf
     "index_start"= -1
     "index_end"= -1,
     "filter"= ""
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "total_users": 1,
        "users": []
    }
    ```

#### POST /v1/admin/users

Create user. Payload is user profile. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "username": "",
        "password": "",
        "email": "",
        "role": "",
        "quota": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```

#### GET /v1/admin/users/:username

Get a single user's profile. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```

#### PUT /v1/admin/users/:username

Modify user. Payload is new user profile. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "username": "",
        "password": "",
        "status": "",
        "email": "",
        "role": "",
        "quota": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```

#### DELETE /v1/admin/users/:username

Delete a user. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```

### Templates Management

This section describes admin APIs that manipulate template resource.

#### GET /v1/admin/templates

List all templates. If `template_id_start` and `template_id_end` are “greater than” 0, only templates with `template_id`
between `template_id_start` and `template_id_end` are returned. If `filter` is not empty, apply filter on results. This
API returns profiles of templates and total number of templates. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:
    ```
    ```


- Request Query:

    ```conf
     "index_start"= -1
     "index_end"= -1,
     "filter"= ""
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "total_templates": 1,
        "templates": []
    }
    ```

#### POST /v1/admin/templates

Create template. Payload is a template. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "name": "",
        "description": "",
        "image_ref": "",
        "template_str": "",
        "fields": {},
        "defaults": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "template": {}
    }
    ```

#### GET /v1/admin/templates/:template_id

Get a single template. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "template": {}
    }
    ```

#### PUT /v1/admin/templates/:template_id

Modify template. Payload is new template profile. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    { 
        "template_id": "",
        "name": "",
        "image_ref": "",
        "template_str": "", 
        "fields": {},
        "defaults": {} 
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "template": {}
    }
    ```

#### DELETE /v1/admin/templates/:template_id

Delete a template. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "template": {}
    }
    ```

### Pod Management

This section describes admin APIs that manipulate pod resource.

#### GET /v1/admin/pods

List all pods. If `filter` is not empty, apply filter on results. This API returns profiles of pods and total number of
pods. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:
    ```
    ```


- Request Query:

    ```conf
     "index_start"= -1
     "index_end"= -1,
     "filter"= ""
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "total_pods": 1,
        "pods": []
    }
    ```

#### POST /v1/admin/pods

Create pod. Payload is pod profile. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "name": "",
        "description": "",
        "template_ref": "",
        "cpu_lim_m_cpu": 1000,
        "mem_lim_mb": 1024,
        "storage_lim_mb": 10240,
        "gpu": 0,
        "username": "",
        "timeout_s": 3600,
        "values": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

#### GET /v1/admin/pods/:pod_id

Get a single pod's status. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

#### PUT /v1/admin/pods/:pod_id

Modify a single pod. Same field semantics as `PUT /v1/pods/:pod_id`.

Spec edits (`cpu_lim_m_cpu`, `mem_lim_mb`, `storage_lim_mb`, `gpu`) are only
accepted when the pod's `current_status` is `stopped`. **This guard applies
to admins too** — editing the spec of a running pod would race against the
live k8s deployment, so the API returns `400 pod must be stopped to edit
its specs` regardless of role. Stop the pod first
(`{"target_status": "stopped"}`), then resize.

All payload fields are optional; omitted fields are left unchanged. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "name": "",
        "description": "",
        "cpu_lim_m_cpu": 1000,
        "mem_lim_mb": 1024,
        "storage_lim_mb": 10240,
        "gpu": 0,
        "username": "",
        "timeout_s": 3600,
        "target_status": "running"
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

#### DELETE /v1/admin/pods/:pod_id

Delete a single pod. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

## Non-Admin APIS

This section describes Non-Admin APIs. They are not limited to admins.

### User Self Management

This section describes user management APIs. Users can manage their profile

#### GET /v1/users/:username

Get a single user's profile. Similar to /v1/admin/user/:username. User can only manage their own profile.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```

#### PUT /v1/users/:username

Modify user. Payload is new user profile. Similar to /v1/admin/user/:username. User can only manage their own profile.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "username": "",
        "password": "",
        "status": "",
        "role": "",
        "email": "",
        "quota": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "user": {}
    }
    ```
### Templates Management

This section describes user APIs that read template resource.

#### GET /v1/admin/templates

List all templates. If `template_id_start` and `template_id_end` are “greater than” 0, only templates with `template_id`
between `template_id_start` and `template_id_end` are returned. If `filter` is not empty, apply filter on results. This
API returns profiles of templates and total number of templates.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:
    ```
    ```


- Request Query:

    ```conf
     "index_start"= -1
     "index_end"= -1,
     "filter"= ""
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "total_templates": 1,
        "templates": []
    }
    ```
  

#### GET /v1/admin/templates/:template_id

Get a single template. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "template": {}
    }
    ```

### Pod Management

This section describes pod management apis.

#### GET /v1/pods

List all pods owned by current user. If `filter` is not empty, apply filter on results. This API returns profiles of
pods and total number of pods.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```
    ```


- Request Query:

    ```conf
     "index_start"= -1
     "index_end"= -1,
     "filter"= ""
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "total_pods": 1,
        "pods": []
    }
    ```

#### POST /v1/pods

Create pod. Payload is pod profile. The user's quota is enforced on
`storage_lim_mb` and the total number of pods at create time;
`cpu_lim_m_cpu`, `mem_lim_mb` and `gpu` are charged against the quota
only when the pod is started (see `PUT /v1/pods/:pod_id`).

`cpu_lim_m_cpu` must be ≥ 500, `mem_lim_mb` ≥ 512, `storage_lim_mb` ≥ 10240,
`gpu` ≥ 0, `timeout_s` between 0 and 86400.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "name": "",
        "description": "",
        "template_ref": "",
        "cpu_lim_m_cpu": 1000,
        "mem_lim_mb": 1024,
        "storage_lim_mb": 10240,
        "gpu": 0,
        "timeout_s": 3600,
        "values": {}
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

#### GET /v1/pods/:pod_id

Get a single pod owned by current user. The returned `pod.current_status_reason`
carries a short human-readable explanation when `current_status` is `failed`
(e.g. `Unschedulable: 0/3 nodes available: 3 Insufficient memory`,
`ImagePullBackOff: ...`). It is `null` while the pod is healthy.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

#### PUT /v1/pods/:pod_id

Modify a single pod owned by current user. All payload fields are optional;
omitted fields are left unchanged.

Spec edits (`cpu_lim_m_cpu`, `mem_lim_mb`, `storage_lim_mb`, `gpu`) are only
accepted when the pod's `current_status` is `stopped` — attempts to resize a
running or pending pod return `400 pod must be stopped to edit its specs`.
The same guard applies to the admin endpoint (`PUT /v1/admin/pods/:pod_id`),
so a pod must always be stopped before its spec can be changed. This lets a
user shrink a pod whose original spec no longer fits the cluster's available
resources, then start it.

Every request — whether it changes specs, just sets `target_status: running`,
or both — is validated against the user's quota using the *effective* spec
(request value falling back to the pod's stored value), so a user can never
exceed their allowance. If the check fails the API returns `400 quota exceeded`.

If the cluster cannot fit the pod (insufficient cpu/memory/gpu, unschedulable,
image pull failure, etc.) the pod transitions to `current_status: failed`
and a short reason is written to `current_status_reason`; the user can then
edit the spec and retry.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "name": "",
        "description": "",
        "cpu_lim_m_cpu": 1000,
        "mem_lim_mb": 1024,
        "storage_lim_mb": 10240,
        "gpu": 0,
        "timeout_s": 3600,
        "target_status": "running"
    }
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```

- Error responses:

    ```json
    {"status": 400, "message": "pod must be stopped to edit its specs"}
    {"status": 400, "message": "quota exceeded"}
    ```

#### DELETE /v1/pods/:pod_id

Delete a single pod. User can only delete their own pod. Admins can delete any.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    ```

- Response:

    ```json
    {
        "description": "",
        "status":200,
        "message":"",
        "pod": {}
    }
    ```
