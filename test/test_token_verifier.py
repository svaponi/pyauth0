import pytest

from pyauth0 import Auth0Error, TokenVerifier
from test.const import JWT_IO_TOKEN


@pytest.fixture
def token_verifier():
    return TokenVerifier(
        issuer="your-domain.auth0.com",
        audience="https://api.your-domain.com",
        jwks_cache_ttl=60,
    )


@pytest.mark.asyncio
async def test_invalid_token(token_verifier):
    with pytest.raises(Auth0Error) as info:
        await token_verifier.verify(JWT_IO_TOKEN)
    assert info.value.code == "invalid_token"
    assert "Invalid token" in info.value.description


@pytest.mark.asyncio
async def test_missing_token(token_verifier):
    with pytest.raises(Auth0Error) as info:
        await token_verifier.verify(None)
    assert info.value.code == "invalid_token"
    assert "Token is missing" in info.value.description


@pytest.mark.asyncio
async def test_malformed_token(token_verifier):
    with pytest.raises(Auth0Error) as info:
        await token_verifier.verify("gibberish")
    assert info.value.code == "invalid_token"
    assert "Malformed token" in info.value.description
