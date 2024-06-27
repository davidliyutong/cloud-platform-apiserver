GIT_VERSION := $(shell git describe --tags --abbrev=0 --always)
AUTHOR="davidliyutong"
DEV_AUTHOR="core.harbor.speit.site/clpl"

docker.build.dev:
	docker build -t ${DEV_AUTHOR}/clpl-apiserver:${GIT_VERSION}-dev -f manifests/docker/Dockerfile .
	docker tag ${DEV_AUTHOR}/clpl-apiserver:${GIT_VERSION}-dev ${AUTHOR}/clpl-apiserver:latest-dev

docker.push.dev:
	docker push ${DEV_AUTHOR}/clpl-apiserver:${GIT_VERSION}-dev ${DEV_AUTHOR}/clpl-apiserver:latest-dev

docker.build.prod:
	docker buildx build --platform=linux/amd64,linux/arm64 -t ${AUTHOR}/clpl-apiserver:${GIT_VERSION} -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .
	docker buildx build --load -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .

docker.push.prod:
	docker buildx build --push --platform=linux/amd64,linux/arm64 -t ${AUTHOR}/clpl-apiserver:${GIT_VERSION} -t ${AUTHOR}/clpl-apiserver:latest -f manifests/docker/Dockerfile .

docker.run:
	docker run --rm -it --net=host -p 8080:8080 ${AUTHOR}/clpl-apiserver:latest

task.api.generate_client:
	openapi-generator-cli generate -g python -i http://127.0.0.1:8080/docs/openapi.json --skip-validate-spec -o python-client