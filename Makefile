GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
CYAN   := $(shell tput -Txterm setaf 6)
RESET  := $(shell tput -Txterm sgr0)

EXISTS_POETRY := $(shell command -v poetry 2> /dev/null)
EXISTS_FLASK := $(shell command -v uvicorn 2> /dev/null)

export BERLIN_API_PORT ?= 28900
export BERLIN_API_HOST ?= 0.0.0.0
export FLASK_APP ?= app/main.py

export BERLIN_API_GIT_COMMIT=$(shell git rev-parse HEAD)
export BERLIN_API_VERSION ?= 0.1.0
export BERLIN_API_BUILD_TIME=$(shell date +%s)

.PHONY: all audit build build-bin deps help lint debug debug-container test test-component test-unit fmt

all: audit lint fmt

audit: deps ## audits code for vulnerable dependencies
	poetry run safety check

build: ## Builds a docker image berlin_api
	docker build --build-arg build_time="${BERLIN_API_BUILD_TIME}" --build-arg commit="${BERLIN_API_GIT_COMMIT}" --build-arg version="${BERLIN_API_VERSION}" -t berlin_api .

build-bin: deps ## Builds a python wheel
	poetry build

deps: ## Installs dependencies
	bash ./ci/scripts/deps.sh

fmt: ## Formats your code automatically.
	poetry run isort .
	poetry run black .

lint: deps ## Lints code 
	poetry run ruff .

debug: deps ## Start the api locally on port 28900.
	@FLASK_APP=${FLASK_APP} poetry run gunicorn "app.main:create_app()" -b 0.0.0.0:${BERLIN_API_PORT} -c gunicorn_config.py

debug-container: build ## Runs a container from the pre-build image 
	docker run -p 28900:28900 --env BERLIN_API_BUILD_TIME='${BERLIN_API_BUILD_TIME}' -e BERLIN_API_BUILD_TIME="${BERLIN_API_BUILD_TIME}" -e BERLIN_API_VERSION="${BERLIN_API_VERSION}" -ti berlin_api

test: deps ## runs all tests
	poetry run pytest -v tests/

test-component: deps ## runs component tests
	poetry run pytest -v tests/api

test-unit: deps ## runs unit tests
	poetry run pytest -v tests/unit

help: ## Show this help.
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "  ${CYAN}%s${RESET}\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)
