#!/bin/bash

export PYTHONPATH=$(pwd)
sphinx-build sphinx docs

poetry run pyinstaller --onefile --distpath bin cmg/cli.py
