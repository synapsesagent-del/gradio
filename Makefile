# DevOps Makefile for Sample Application

# Variables
IMAGE_NAME = devops-sample-app
CONTAINER_NAME = devops-app-container
PORT = 3000

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install application dependencies"
	@echo "  start       - Start the application locally"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run application in Docker"
	@echo "  docker-stop - Stop Docker container"
	@echo "  test        - Run tests"
	@echo "  clean       - Remove Docker container and image"

install:
	npm install

start:
	npm start

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run: docker-build
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):3000 $(IMAGE_NAME)

docker-stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

test:
	npm test

clean: docker-stop
	docker rmi $(IMAGE_NAME) || true

.PHONY: help install start docker-build docker-run docker-stop test clean