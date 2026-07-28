#!/bin/bash
# Vercel build script: collect static files for WhiteNoise serving
python manage.py collectstatic --noinput
