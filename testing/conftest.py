"""
Configuration globale pour les tests pytest du projet EIR
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import de l'application principale
try:
    from backend.app.main import app
except ImportError:
    app = None

@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour l'event loop asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Client de test FastAPI synchrone"""
    if app is None:
        pytest.skip("Application backend non disponible")
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Client de test FastAPI asynchrone"""
    if app is None:
        pytest.skip("Application backend non disponible")
    
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client

@pytest.fixture
def auth_headers():
    """Headers d'authentification pour les tests"""
    return {
        "Authorization": "Bearer test-token-for-testing",
        "Content-Type": "application/json"
    }

@pytest.fixture
def test_user_data():
    """Données utilisateur de test"""
    return {
        "email": "test@example.com",
        "nom": "Test User",
        "mot_de_passe": "testpassword123"
    }

@pytest.fixture
def test_imei_data():
    """Données IMEI de test"""
    return {
        "valid_imei": "123456789012345",
        "invalid_imei": "invalid_imei",
        "test_tac": "12345678"
    }

# Configuration pytest
def pytest_configure(config):
    """Configuration globale pytest"""
    config.addinivalue_line(
        "markers", "slow: marque les tests lents"
    )
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "api: marque les tests API"
    )
