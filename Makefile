.PHONY: install test lint check run 

ROUTE_FILE ?=

define REQUIRE
  $(if $(value $(1)),,$(error $(1) is required))
endef

help:
	@echo "install - install dependencies with poetry"
	@echo "test - run unit tests"
	@echo "lint - run linter and checks"
	@echo "check - run static checks"
	@echo "run - run routes"

test:
	poetry run pytest -vv test

check:
	./static_checks.sh

lint:
	./linter.sh
	
install:
	poetry install --no-root
	poetry shell

run:
	$(call REQUIRE,ROUTE_FILE)
	poetry run python -m src.route $(ROUTE_FILE)