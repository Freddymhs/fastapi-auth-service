from httpx import AsyncClient


async def test_health_returns_uniform_contract(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "statusCode" in body
    assert "data" in body
    assert "meta" in body
    assert body["data"]["status"] == "ok"
    assert "db" in body["data"]
    assert "timestamp" in body["meta"]
    assert "path" in body["meta"]


async def test_health_has_request_id_header(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert "x-request-id" in response.headers
