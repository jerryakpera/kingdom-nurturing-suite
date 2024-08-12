#!/usr/bin/env bash

set -o errexit  # exit on error

python manage.py migrate

# Create superuser
python manage.py createsu

# Initialize settings
# python manage.py createsettings

# Generate data
# python manage.py generatedata
