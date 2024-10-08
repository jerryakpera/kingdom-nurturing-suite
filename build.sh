#!/usr/bin/env bash

set -o errexit  # exit on error

pip install -r requirements.txt

python manage.py collectstatic

python manage.py migrate

# Create superuser
python manage.py createsu

# Initialize settings
python manage.py createsettings

# Populate database
python manage.py populate_db
