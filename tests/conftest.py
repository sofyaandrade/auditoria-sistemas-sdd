import os

os.environ["DATABASE_PATH"] = "/tmp/task_api_test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    db_path = os.environ["DATABASE_PATH"]
    if os.path.exists(db_path):
        os.remove(db_path)
    with TestClient(app) as test_client:
        yield test_client
    if os.path.exists(db_path):
        os.remove(db_path)
