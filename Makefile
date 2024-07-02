GIT_VERSION := $(shell git describe --tags --abbrev=0 --always)
AUTHOR="davidliyutong"
PROJECT_NAME="clpl"

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

# npm install -g @openapitools/openapi-generator-cli
# java is required
task.api.generate_apiserver_client:
	@mkdir -p src/clients/api_client
	@rm -rf src/clients/api_client/*
	openapi-generator-cli generate -g python -i http://127.0.0.1:8080/docs/openapi.json --skip-validate-spec -o src/clients/api_client --package-name ${PROJECT_NAME}_apiserver_client --library asyncio
	@touch src/clients/api_client/__init__.py

task.api.generate_rbacserver_client:
	@mkdir -p src/clients/rbac_client
	@rm -rf src/clients/rbac_client/*
	openapi-generator-cli generate -g python -i http://127.0.0.1:8081/docs/openapi.json --skip-validate-spec -o src/clients/rbac_client --package-name ${PROJECT_NAME}_apiserver_client --library asyncio
	@touch src/clients/rbac_client/__init__.py

task.api.generate_client: task.api.generate_apiserver_client task.api.generate_rbacserver_client

backup:
	tar -zvcf ~/fileExchange/cloud-platform-apiserver.tar.gz ./