.PHONY: install test lint check run 

ROUTE_FILE ?=

define REQUIRE
  $(if $(value $(1)),,$(error $(1) is required))
endef

help:
	@echo "install - install dependencies with poetry"
	@echo "lint - run linter and checks"
	@echo "run - run routes"


lint:
	./linter.sh
	
install:
	poetry install --no-root
	poetry shell

run:
	$(call REQUIRE,ROUTE_FILE)
	poetry run python -m src.route $(ROUTE_FILE)