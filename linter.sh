#!/usr/bin/env bash

set -o verbose

isort .
black .
flake8 .