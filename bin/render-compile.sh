#!/usr/bin/env bash
# exit on error
set -o errexit

echo "-----> Install Python dependencies"
python -m pip install --upgrade pip
python -m pip install pipenv
pipenv install --system --deploy

echo "-----> Running post-compile tasks"
cd ./tabbycat/

echo "-----> Running database migration"
python manage.py migrate --noinput

echo "-----> Running dynamic preferences checks"
python manage.py checkpreferences

echo "-----> Installing Node.js dependencies"
cd ..
npm ci --production=false

echo "-----> Running static asset compilation"
npm run build

echo "-----> Running static files compilation"
cd ./tabbycat/
python manage.py collectstatic --noinput

echo "-----> Post-compile done"
