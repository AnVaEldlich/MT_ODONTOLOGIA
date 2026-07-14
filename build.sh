#!/usr/bin/env bash
# Build script for Render (and local production checks).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
