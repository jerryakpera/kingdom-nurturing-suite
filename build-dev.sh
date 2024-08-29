#!/usr/bin/env bash

set -o errexit  # exit on error

python manage.py migrate

# Create superuser
python manage.py createsu

# Initialize settings
python manage.py createsettings

# Populate database
python manage.py populate_db
