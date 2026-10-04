#!/usr/bin/env bash
# Build script for Render (and local production checks).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
# En Render la migración va en preDeployCommand: el build no ve un MySQL privado.
if [ "${SKIP_MIGRATE_ON_BUILD:-}" != "True" ]; then
  python manage.py migrate --noinput
fi
