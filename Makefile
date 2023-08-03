GIT_VERSION := $(shell git describe --tags --always)
MACHINE := $(shell uname -m)

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

task.generate_client:
	openapi-generator-cli generate -g python -i http://127.0.0.1:8080/docs/openapi.json --skip-validate-spec -o python-client
	# openapi-python-generator http://127.0.0.1:8080/docs/openapi.json src/client
	# openapi-python-client generate --url http://127.0.0.1:8080/docs/openapi.json