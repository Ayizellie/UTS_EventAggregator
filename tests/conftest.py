import pytest
from fastapi.testclient import TestClient
from src.main import app, dedup

@pytest.fixture(autouse=True)
def reset_db(tmp_path):
    """Gunakan database sementara sebelum setiap test berjalan."""
    test_db = tmp_path / "test_dedup_store.db"
    dedup.set_db_path(str(test_db))   
    dedup._ensure_db_exists()         
    yield

@pytest.fixture
def client():
    """Fixture untuk test client FastAPI."""
    with TestClient(app) as c:
        yield c
