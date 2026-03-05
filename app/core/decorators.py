PUBLIC_ROUTE_KEY = "is_public_route"


def public(func):  # type: ignore[no-untyped-def]
    """Mark a route as public (no authentication required)."""
    setattr(func, PUBLIC_ROUTE_KEY, True)
    return func
