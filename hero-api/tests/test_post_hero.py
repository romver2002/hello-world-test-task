import pytest

@pytest.mark.asyncio
async def test_create_hero_ok(client):
    r = await client.post("/hero/", json={"name": "Batman"})
    assert r.status_code in (200, 201)
    body = r.json()
    assert body["name"] == "Batman"
    assert body["intelligence"] == 100

@pytest.mark.asyncio
async def test_create_hero_not_found(client):
    r = await client.post("/hero/", json={"name": "UnknownName"})
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


