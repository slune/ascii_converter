NAME = asciiserver
VERSION = "1.0.0"
REPO = "localhost"

test:
	podman stop asciiserver | true
	podman rm asciiserver | true
	docker run -d --name $(NAME) -p 8080:8080 $(REPO)/$(NAME):$(VERSION)
	python tests/test_convert.py
	python tests/integration_server_test.py

build:
	docker build -t $(REPO)/$(NAME):$(VERSION) -f Dockerfile .

service:
	podman stop asciiserver | true
	podman rm asciiserver | true
	docker run -d --name $(NAME) -p 8080:8080 $(REPO)/$(NAME):$(VERSION)

