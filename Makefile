GIT_VERSION := $(shell git describe --tags --always)
MACHINE := $(shell uname -m)
.PHONY: build.docker.x86

build.docker.native:
	docker build -t davidliyutong/clpl-apiserver:${GIT_VERSION} -f manifests/docker/Dockerfile .
	docker tag davidliyutong/clpl-apiserver:${GIT_VERSION} davidliyutong/clpl-apiserver:latest

build.docker.buildx:
	docker buildx build --platform=linux/amd64,linux/arm64 -t davidliyutong/clpl-apiserver:${GIT_VERSION} -f manifests/docker/Dockerfile .
	docker buildx build --platform=linux/amd64,linux/arm64 -t davidliyutong/clpl-apiserver:latest -f manifests/docker/Dockerfile .
	docker buildx build --load -t davidliyutong/clpl-apiserver:latest -f manifests/docker/Dockerfile .

push.docker.buildx:
	docker buildx build --push --platform=linux/amd64,linux/arm64 -t davidliyutong/clpl-apiserver:${GIT_VERSION} -f manifests/docker/Dockerfile .
	docker buildx build --push --platform=linux/amd64,linux/arm64 -t davidliyutong/clpl-apiserver:latest -f manifests/docker/Dockerfile .

test.docker:
	docker run --rm -it --net=host -p 8080:8080 davidliyutong/clpl-apiserver:latest