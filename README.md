# Cloud Platform API Server

This project is the API server progream of a cloud native coding platform. It is a RESTful server built with Sanic that
enables creation of WebIDE in a K8S cluster (e.g. [code-server](https://github.com/coder/code-server))

The api server is designed to be deployed on a K8S cluster but can also be run locally.

## Introduction

### Features

The api server provides the following features:

- User management, including adding, deleting, and updating users. Users are divided into two groups: admin and normal
  users. Admin users can manage other users, templates and pods. Normal user can only manage their own pods.
- Template can be added and deleted by admin users and are shared within all users. Templates are used to create pods.
- Pod can be created, deleted, updated and listed by admin users and normal users. Pods are created from templates and
  are used to run WebIDE.
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

TBD.

### Deploy with Kubernetes

TBD.


## Configuration

The apiserver can be configured with environment variables, command line arguments or configuration files. The following table lists all the parameters.

TBD.