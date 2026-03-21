"""Shared infrastructure handles for API routes."""

from __future__ import annotations

import os
from typing import Optional

import redis

try:
	from psycopg2.pool import SimpleConnectionPool
except Exception:  # pragma: no cover - psycopg2 may be unavailable in some local test contexts
	SimpleConnectionPool = None  # type: ignore[assignment]


_redis_client: Optional[redis.Redis] = None
_db_pool = None


def get_redis_client() -> redis.Redis:
	"""Return a singleton Redis client configured from REDIS_URL."""
	global _redis_client
	if _redis_client is None:
		redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
		_redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
	return _redis_client


def get_db_pool():
	"""Return a singleton PostgreSQL connection pool when configured."""
	global _db_pool
	if _db_pool is not None:
		return _db_pool

	if SimpleConnectionPool is None:
		return None

	db_url = os.getenv("DATABASE_URL")
	if not db_url:
		return None

	try:
		_db_pool = SimpleConnectionPool(minconn=1, maxconn=5, dsn=db_url)
	except Exception:
		_db_pool = None
	return _db_pool
