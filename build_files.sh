#!/bin/bash
# Create a temporary virtual environment
python3 -m venv venv
# Activate the virtual environment
source venv/bin/activate
# Install requirements in the virtual environment
pip install -r requirements.txt
# Run collectstatic
python manage.py collectstatic --noinput --clear
