#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
  TIMEOUT=$((TIMEOUT+1))
  if [ $TIMEOUT -gt 60 ]; then
    echo "Timeout reached waiting for PostgreSQL"
    exit 1
  fi
done

echo "PostgreSQL started"


exec "$@"