GIT_VERSION := $(shell git describe --tags --abbrev=0 --always)
AUTHOR="davidliyutong"
DEV_AUTHOR="davidliyutong"

build.docker.native:
	docker build --build-arg GIT_VERSION=${GIT_VERSION} -t ${AUTHOR}/clpl-apiserver:${GIT_VERSION} -f manifests/docker/Dockerfile .
	docker tag ${AUTHOR}/clpl-apiserver:${GIT_VERSION} davidliyutong/clpl-apiserver:latest

build.docker.buildx:
	docker buildx build --build-arg GIT_VERSION=${GIT_VERSION} --platform=linux/amd64,linux/arm64 -t ${AUTHOR}/clpl-apiserver:${GIT_VERSION} -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .
	docker buildx build --build-arg GIT_VERSION=${GIT_VERSION} --load -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .

push.docker.buildx:
	docker buildx build --build-arg GIT_VERSION=${GIT_VERSION} --push --platform=linux/amd64,linux/arm64 -t ${AUTHOR}/clpl-apiserver:${GIT_VERSION} -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .

test.docker:
	docker run --rm -it --net=host -p 8080:8080 ${AUTHOR}/clpl-apiserver:latest

task.generate_client:
	openapi-generator-cli generate -g python -i http://127.0.0.1:8080/docs/openapi.json --skip-validate-spec -o python-client

dev.push:
	docker buildx build --build-arg GIT_VERSION=${GIT_VERSION} --push --platform=linux/amd64,linux/arm64 -t ${DEV_AUTHOR}/clpl-apiserver:latest-dev -f manifests/docker/Dockerfile .
