.PHONY: install test lint check run 

ROUTE_FILE ?=
OUTPUT_FILE ?=

define REQUIRE
  $(if $(value $(1)),,$(error $(1) is required))
endef

help:
	@echo "install - install dependencies with poetry"
	@echo "lint - run linter and checks"
	@echo "run - run routes"


install:
	poetry install --no-root
	poetry shell

run:
	$(call REQUIRE,ROUTE_FILE)
	$(call REQUIRE,OUTPUT_FILE)
	poetry run python -m src.route $(ROUTE_FILE) $(OUTPUT_FILE)

run_intersection_based:
	$(call REQUIRE,ROUTE_FILE)
	$(call REQUIRE,OUTPUT_FILE)
	poetry run python -m src.route_intersection_based $(ROUTE_FILE) $(OUTPUT_FILE)