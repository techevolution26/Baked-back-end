#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    async with engine.connect():
        pass
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; do
  sleep 1
done
echo "Database is up."

echo "Running migrations..."
alembic upgrade head

exec "$@"
