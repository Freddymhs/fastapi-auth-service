from httpx import AsyncClient


async def test_security_headers_present(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "strict-transport-security" in response.headers
