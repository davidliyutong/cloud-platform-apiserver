.PHONY: build.docker.x86

build.docker.native:
	docker build -t davidliyutong/clpl-backend:$(shell uname -m)-latest -f manifests/docker/Dockerfile .

build.docker.buildx-amd64:
	docker buildx build --platform=linux/amd64 -t davidliyutong/clpl-backend:latest -f manifests/docker/Dockerfile .

push.docker.buildx-amd64:
	docker buildx build --push --platform=linux/amd64 -t davidliyutong/clpl-backend:latest -f manifests/docker/Dockerfile .

test.docker:
	docker run --rm -it --net=host -p 8080:8080 davidliyutong/clpl-backend:$(shell uname -m)-latest