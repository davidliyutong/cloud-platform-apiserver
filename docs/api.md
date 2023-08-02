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
        "uid": "",
        "timeout_s": 1,
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

Modify a single pod's status. Limited to admins.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "pod_id": "",
        "name": "",
        "description": "",
        "template_ref": "",
        "uid": "",
        "timeout_s": "",
        "target_status": ""
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

Create pod. Payload is pod profile. Users will be limited on their quota. Admins are not limited by default.

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
        "uid": "",
        "timeout_s": 1,
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

Get a single pod's status owned by current user.

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

Modify a single pod's status. User can only modify their own pod. Admins can modify any.

- Request Header:

    ```conf
    Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey
    Content-Type=application/json
    ```

- Request Payload:

    ```json
    {
        "pod_id": "",
        "name": "",
        "description": "",
        "template_ref": "",
        "uid": "",
        "timeout_s": "",
        "target_status": ""
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
