#!/bin/sh
source .venv/bin/activate
python -u -m flask --app main run --debug --port 5001 --host=0.0.0.0
