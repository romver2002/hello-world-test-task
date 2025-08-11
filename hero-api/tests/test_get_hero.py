import pytest

@pytest.mark.asyncio
async def test_filters_exact_and_range(client):
    await client.post("/hero/", json={"name": "Batman"})

    # точное имя
    r = await client.get("/hero/", params={"name": "Batman"})
    assert r.status_code == 200 and len(r.json()) == 1

    # strength >= 20
    r = await client.get("/hero/", params={"strength": ">=20"})
    assert r.status_code == 200 and len(r.json()) >= 1

    # strength <= 10 -> ожидаемо нет результатов
    r = await client.get("/hero/", params={"strength": "<=10"})
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_intellegence_alias(client):
    await client.post("/hero/", json={"name": "Batman"})
    # опечатка из ТЗ поддержана alias
    r = await client.get("/hero/", params={"intellegence": ">=100"})
    assert r.status_code == 200 and len(r.json()) >= 1


