# Cloud Platform API Server

This project is the API server progream of a cloud native coding platform. It is a RESTful server built with Sanic that enables creation of WebIDE in a K8S cluster (e.g. [code-server](https://github.com/coder/code-server))

The api server is designed to be deployed on a K8S cluster but can also be run locally.

The frontend project is [here](https://github.com/davidliyutong/cloud-platform-frontend)

## Introduction

### Features

The api server provides the following features:

- User management, including adding, deleting, and updating users. Users are divided into two groups: admin and normal users. Admin users can manage other users, templates and pods. Normal user can only manage their own pods.
- Template can be added and deleted by admin users and are shared within all users. Templates are used to create pods.
- Pod can be created, deleted, updated and listed by admin users and normal users. Pods are created from templates and are used to run WebIDE.
- Support two types of interaction: WebIDE and noVNC

## Get Started

### Requirements

This project is written in Python, with minimum version of 3.9 required. It also requires:

- Access to MongoDB instance
- Access to Kubernetes cluster

### Deploy locally

To run the api server locally, you need to install the dependencies first:

```shell
pip install -r requirements.txt
```

Then, you can run the api server with the following command:

```shell
python -m src serve
```

> You might need to set the environment variable `PYTHONPATH` to the directory of this project.

To apply custom configuration, see the `Configuration` section below.

### Deploy with Docker

To deploy the api server with Docker, you need to build the Docker image first:

```shell
docker build -t davidliyutong/clpl-apiserver:$(shell uname -m)-latest -f manifests/docker/Dockerfile .

```

Then, you can run the Docker image with the following command:

```shell
docker run -it --rm -p 8080:8080 davidliyutong/clpl-apiserver:$(shell uname -m)-latest
```

To apply custom configuration, see the `Configuration` section below.

### Deploy with Docker Compose

Modify the `manifests/docker/docker-compose.yml` file according to your configuration, then run the following command

```shell
cd manifests/docker
docker-compose up -d
```

To apply custom configuration, see the `Configuration` section below.

### Deploy with Kubernetes

First, create the `clpl` namespace:

```shell
kubectl create namespace clpl
```

Then, apply the `manifests/k8s/rbac.yaml` file:

```shell
kubectl apply -f manifests/k8s/rbac.yaml
```

You need to create 4 TLS certificate:

- TLS certificate for the api server
- TLS certificate for the frontend
- TLS certificate for the noVNC endpoint
- TLS certificate for the WebIDE endpoint

You can use `manifests/k8s/clusterissure.yaml` to create a cert-manager cluster issuer. Then, create the certificates with the help of `manifests/k8s/certificates.yaml`

Finally, modify the `manifests/k8s/deployment.yaml` according to your configuration and apply it:

```shell
kubectl apply -f manifests/k8s/deployment.yaml
```

## Configuration

The apiserver can be configured with environment variables, command line arguments or configuration files. The following
table lists all the parameters.

| Name                                | CLI                         | ENV                            | Description                                          | Default                                                | 
|-------------------------------------|-----------------------------|--------------------------------|------------------------------------------------------|--------------------------------------------------------|
| Number of Workers                   | `--api.numWorkers`          | `CLPL_API_NUMWORKERS`          | Number of workers to launch                          | `4`                                                    |
| API Host                            | `--api.host`                | `CLPL_API_HOST`                | API Hostname                                         | `0.0.0.0`                                              |
| API Port                            | `--api.port`                | `CLPL_API_PORT`                | Port for the API server, default                     | `8080`                                                 |
| API Access Log                      | `--api.accessLog`           | `CLPL_API_ACCESSLOG`           | Boolean flag for logging API access, might slow down | `false`                                                |
| Database Host                       | `--db.host`                 | `CLPL_DB_HOST`                 | Hostname of the mongodb server                       | `127.0.0.1`                                            |
| Database Port                       | `--db.port`                 | `CLPL_DB_PORT`                 | Port of the mongodb server                           | `27017`                                                |
| Database Username                   | `--db.username`             | `CLPL_DB_USERNAME`             | Username for the database                            | `clpl`                                                 |
| Database Password                   | `--db.password`             | `CLPL_DB_PASSWORD`             | Password for the database                            | `clpl`                                                 |
| Database Name                       | `--db.database`             | `CLPL_DB_DATABASE`             | Name of the database                                 | `clpl`                                                 |
| MQ Host                             | `--mq.host`                 | `CLPL_MQ_HOST`                 | Hostname of the MQ server (not used)                 | `127.0.0.1`                                            |
| MQ Port                             | `--mq.port`                 | `CLPL_MQ_PORT`                 | Port of the MQ server (not used)                     | `5672`                                                 |
| MQ Username                         | `--mq.username`             | `CLPL_MQ_USERNAME`             | Username for the MQ server (not used)                | `clpl`                                                 |
| MQ Password                         | `--mq.password`             | `CLPL_MQ_PASSWORD`             | Password for the MQ server (not used)                | `clpl`                                                 |
| MQ Exchange                         | `--mq.exchange`             | `CLPL_MQ_EXCHANGE`             | Name of the MQ exchange (not used)                   | ``                                                     |
| Kubernetes Host                     | `--k8s.host`                | `CLPL_K8S_HOST`                | Kubernetes Hostname                                  | `10.96.0.1`                                            |
| Kubernetes Port                     | `--k8s.port`                | `CLPL_K8S_PORT`                | Kubernetes Port                                      | `6443`                                                 |
| Kubernetes CA certificate path      | `--k8s.caCert`              | `CLPL_K8S_CACERT`              | Path of Kubernetes CA certificate                    | `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt` |
| Kubernetes Token                    | `--k8s.token`               | `CLPL_K8S_TOKEN`               | Kubernetes token                                     | `/var/run/secrets/kubernetes.io/serviceaccount/token`  |
| Kubernetes SSL Verification         | `--k8s.verifySSL`           | `CLPL_K8S_VERIFYSSL`           | Boolean flag for Kubernetes SSL verification         | `false`                                                |
| Kubernetes Namespace                | `--k8s.namespace`           | `CLPL_K8S_NAMESPACE`           | Kubernetes namespace                                 | `clpl`                                                 |
| Bootstrap Admin Username            | `--bootstrap.adminUsername` | `CLPL_BOOTSTRAP_ADMINUSERNAME` | Default admin username                               | `admin`                                                |
| Bootstrap Admin Password            | `--bootstrap.adminPassword` | `CLPL_BOOTSTRAP_ADMINPASSWORD` | Default admin password                               | `admin`                                                |
| Configuration Token Secret          | `--config.tokenSecret`      | `CLPL_CONFIG_TOKENSECRET`      | Secret key for sign long-term token, must be strong  | `null`                                                 |
| Configuration Token Expiration Time | `--config.tokenExpireS`     | `CLPL_CONFIG_TOKENEXPIRES`     | Expiration time for jwt token                        | `3600`                                                 |
| Configuration Coder Hostname        | `--config.coderHostname`    | `CLPL_CONFIG_CODERHOSTNAME`    | Hostname for the code ingress                        | `null`                                                 |
| Configuration Coder TLS Secret      | `--config.coderTLSSecret`   | `CLPL_CONFIG_CODERTLSSECRET`   | Secret name for the code ingress tls                 | `null`                                                 |
| Configuration VNC Hostname          | `--config.vncHostname`      | `CLPL_CONFIG_VNCHOSTNAME`      | Hostname for the vnc ingress                         | `null`                                                 |
| Configuration VNC TLS Secret        | `--config.vncTLSSecret`     | `CLPL_CONFIG_VNCTLSECRET`      | Secret key for the vnc ingress tls                   | `null`                                                 |
| Configuration USE OIDC              | `--config.useOIDC`          | `CLPL_CONFIG_USEOIDC`          | Use OIDC or not                                      | `false`                                                |

The platform supports login via OpenID Connect. It is tested with [Authentik](https://goauthentik.io/) identity provider. Here are OIDC configurations if you want to use OIDC:

| Name                    | CLI                       | ENV                          | Description                                                                                                  | Default                         | 
|-------------------------|---------------------------|------------------------------|--------------------------------------------------------------------------------------------------------------|---------------------------------|
| OIDC Name               | `--oidc.name`             | `CLPL_OIDC_NAME`             | Name of the OIDC provider, usually the application name                                                      | `clpl`                          |
| OIDC Base URL           | `--oidc.baseURL`          | `CLPL_OIDC_BASEURL`          | Base URL of the OIDC provider                                                                                | `https://authentik.example.com` |
| OIDC Authorization URL  | `--oidc.authorizationURL` | `CLPL_OIDC_AUTHORIZATIONURL` | Authorization URL of the OIDC provider, defaults to `$CLPL_OIDC_BASEURL/authorize/`                          | `null`                          |
| OIDC Token URL          | `--oidc.tokenURL`         | `CLPL_OIDC_TOKENURL`         | Token URL of the OIDC provider, defaults to `$CLPL_OIDC_BASEURL/token/`                                      | `null`                          |
| OIDC User Info URL      | `--oidc.userInfoURL`      | `CLPL_OIDC_USERINFOURL`      | User Info URL of the OIDC provider, defaults to `$CLPL_OIDC_BASEURL/userinfo/`                               | `null`                          |
| OIDC Logout URL         | `--oidc.logoutURL`        | `CLPL_OIDC_LOGOUTURL`        | Logout URL of the OIDC provider defaults to `$CLPL_OIDC_BASEURL/$CLPL_OIDC_NAME/end-session/` (not used)     | `null`                          |
| OIDC JWKS URL           | `--oidc.jwksURL`          | `CLPL_OIDC_JWKSURL`          | JWKS URL of the OIDC provider, defaults to `$CLPL_OIDC_BASEURL/$CLPL_OIDC_NAME/jwks/` (not used)             | `null`                          |
| OIDC Frontend Login URL | `--oidc.frontendLoginURL` | `CLPL_OIDC_FRONTENDLOGINURL` | Frontend URL of the Application, used to pass `token` and `refresh_token` as URL params to frontend          | `null`                          |
| OIDC Client ID          | `--oidc.clientID`         | `CLPL_OIDC_CLIENTID`         | Client ID of the Application                                                                                 | `null`                          |
| OIDC Client Secret      | `--oidc.clientSecret`     | `CLPL_OIDC_CLIENTSECRET`     | Client Secret of the Application                                                                             | `null`                          |
| OIDC Redirect URL       | `--oidc.redirectURL`      | `CLPL_OIDC_REDIRECTURL`      | Redirect URL of the Application, where the authorization happens e.g. `$HOST/v1/auth/oidc/authorize`         | `null`                          |
| OIDC Scope              | `--oidc.scope`            | `CLPL_OIDC_SCOPE`            | Scopes of the OIDC provider, seperated by delimiter                                                          | `openid`                        |
| OIDC Scope Delimiter    | `--oidc.scopeDelimiter`   | `CLPL_OIDC_SCOPEDELIMITER`   | Scope Delimiter of the OIDC provider                                                                         | `+`                             |
| OIDC Response Type      | `--oidc.responseType`     | `CLPL_OIDC_RESPONSETYPE`     | Response Type of the OIDC provider                                                                           | `code`                          |
| OIDC Grant Type         | `--oidc.grantType`        | `CLPL_OIDC_GRANTTYPE`        | Grant Type of the OIDC provider                                                                              | `authorization_code`            |
| OIDC User Filter        | `--oidc.userFilter`       | `CLPL_OIDC_USERFILTER`       | User Filter of the OIDC provider, should be mongodb-like query, e.g. `{"$and": [{"organize.id": "26000"}]}`  | `{}`                            |
| OIDC User Info Path     | `--oidc.userInfoPath`     | `CLPL_OIDC_USERINFOPATH`     | User Info Path of the OIDC provider, should be jsonpath of user information in the response of User Info URL | `$`                             |
| OIDC Username Path      | `--oidc.usernamePath`     | `CLPL_OIDC_USERNAMEPATH`     | Username Path of the OIDC provider, should be jsonpath of username string in user information                | `preferred_username`            |
| OIDC Email Path         | `--oidc.emailPath`        | `CLPL_OIDC_EMAILPATH`        | Email Path of the OIDC provider, should be jsonpath of email string in user information                      | `email`                         |

# TODO

- migration mechanism
- Audit
- LDAP
- ~~OIDC~~
- ~~Find Out why shutdown print error message~~
- ~~Frontend~~
- ~~CLI client~~
- ~~Quota~~
- ~~Pod AutoStop (Timers)~~
- ~~Error Recovery~~
- ~~Graceful Shutdown~~
- ~~Client library~~
- ~~Comments~~
- ~~Documentation about deploy~~
- ~~K8S manifests~~
- ~~LogLevel~~
- ~~Pod / User Handlers (CheckLogic)~~
- ~~Pod KeepAlive~~
- ~~Basic Auth~~
- ~~Check Logic~~
- ~~Pod Management~~