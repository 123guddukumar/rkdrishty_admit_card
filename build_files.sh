#!/bin/bash
# Install Django and dependencies inside the static build container
python3 -m pip install -r requirements.txt

# Run collectstatic with python3
python3 manage.py collectstatic --noinput --clear
