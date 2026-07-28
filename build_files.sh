#!/bin/bash
# Install Python dependencies first
pip install -r requirements.txt

# Collect static files for WhiteNoise
python manage.py collectstatic --noinput
