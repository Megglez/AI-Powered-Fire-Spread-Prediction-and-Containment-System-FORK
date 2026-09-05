# Wraps the container for frontend test
# Assume maim dev stack alreay running (docker compose up -d)
#Run from app/frontend/ 

ROOT := $(CURDIR)/../..
COMPOSE := docker compose -f $(ROOT)/docker-compose.yml

.PHONY: help up install test test-headed test-report lint format-check

help:
	@echo "Frontend test targets:"
	@echo " make up				- start dev stack (frontend + deps) if not already running"
	@echo " make install		- install Playwright browser binaries (first run only)"
	@echo " make test			- run the Playwright suite headlessly"
	@echo " make test-headed	- run the Playwright suite headed"
	@echo " make test-report	- open the last test report"
	@echo " make lint			- run eslint (next lint)"
	@echo " make format-check	- run prettier --check"


up:
	$(COMPOSE) up -d frontend

install: up
	$(COMPOSE) exec frontend yarn test:install

test: up
	$(COMPOSE) exec frontend yarn test

test-headed: up
	$(COMPOSE) exec frontend yarn test:headed

test-report: up
	$(COMPOSE) exec frontend yarn test:report

lint: up
	$(COMPOSE) exec frontend yarn lint

fromat-check: up
	$(COMPOSE) exec frontend yanr format:check