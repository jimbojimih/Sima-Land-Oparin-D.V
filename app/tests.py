import aiohttp
import asyncio
import pytest

from views import app

@pytest.fixture
def client(event_loop, aiohttp_client):
    return event_loop.run_until_complete(aiohttp_client(app))

@pytest.mark.asyncio
async def test_create_user(client):
    user_data = {
        "name": "testy",
        "last_name": "Swanson",
        "password": "123456",
        "birthdate": "10102012",
        "role_id": 2
    }
    resp = await client.post('/users', json=user_data)
    assert resp.status == 201