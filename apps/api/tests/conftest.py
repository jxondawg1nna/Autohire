from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_DEFAULT_ENV = {
    "DATABASE_URL": "postgresql://localhost/test",
    "REDIS_URL": "redis://localhost:6379/0",
    "MINIO_ENDPOINT": "http://minio:9000",
    "MINIO_ACCESS_KEY": "minio",
    "MINIO_SECRET_KEY": "minio123",
    "MEILISEARCH_URL": "http://meilisearch:7700",
    "MEILISEARCH_API_KEY": "test",
    "QDRANT_URL": "http://qdrant:6333",
    "KEYCLOAK_URL": "http://keycloak:8080",
    "KEYCLOAK_REALM": "autohire",
    "KEYCLOAK_CLIENT_ID": "autohire",
    "KEYCLOAK_CLIENT_SECRET": "secret",
}

for env_key, env_value in _DEFAULT_ENV.items():
    os.environ.setdefault(env_key, env_value)

