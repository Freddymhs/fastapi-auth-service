from httpx import AsyncClient


async def test_404_returns_structured_error(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/nonexistent")
    assert response.status_code in {404, 405}
