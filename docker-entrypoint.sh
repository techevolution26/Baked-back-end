#!/bin/sh
set -e

echo "🚀 Booting development stack..."

# Run migrations safely on boot
echo "Applying database migrations..."
alembic upgrade head

#  Populating foundational development database datasets
echo "Running database seeder script..."
python seed.py

echo "Starting server process..."
# Executing whatever CMD was passed from the Dockerfile
exec "$@"
