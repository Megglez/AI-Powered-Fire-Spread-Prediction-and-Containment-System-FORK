# Wrappers for container backend tests
# Run from app/backend/

ROOT := $(CURDIR)/../..
COMPOSE_TEST := docker compose -f $(ROOT)/docker-compose.tet.yml

.PHONY: help test-up test-down test lint shell logs clean

help:
	@echo "Backend test targets:"
	@echo " make test-up	- start test-db, test-minio"
	@echo " make test		- run the pytest suite in a container"
	@echo " make lint		- run pylint in a container"
	@echo " make shell		- open a shell in the backend-test container"
	@echo " make logs		- tail logs for the test infra"
	@echo " make test-down	- stop and remove test containers"
	@echo " make clean		- test-down plus remove test volumes"

test-up:
	$(COMPOSE_TEST) up -d test-db test-minio

test: test-up
	$(COMPOSE_TEST) run --rm backend-test

lint: test-up
	$(COMPOSE_TEST) run --rm backend-test pylint --recursive=y .

shell: test-up
	$(COMPOSE_TEST) run --rm backend-test bash

logs: 
	$(COMPOSE_TEST) logs -f test-db test-minio

test-down:
	$(COMPOSE_TEST) down

clean:
	$(COMPOSE_TEST) down -v