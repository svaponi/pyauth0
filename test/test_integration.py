import pytest

from pyauth0 import TokenVerifier, TokenProvider
from pyauth0.token_creator import TokenCreator


@pytest.mark.asyncio
async def test_validate_token_integration(mock_server):
    expires_in = 10
    audience = "https://api.your-domain.com"

    token_creator = TokenCreator()

    mock_server.respond_with_json(
        r"/.well-known/jwks.json",
        {
            "keys": [
                token_creator.jwk(),
            ]
        },
    )
    mock_server.respond_with_json(
        r"/oauth/token",
        {
            "access_token": token_creator.create_token(
                mock_server.server_url,
                subject="nobody",
                audience=audience,
                expires_in=expires_in,
            ),
            "scope": "",
            "expires_in": expires_in,
            "token_type": "bearer",
        },
    )

    token_verifier = TokenVerifier(
        issuer=mock_server.server_url,
        audience=audience,
        jwks_cache_ttl=60,
    )

    token_provider = TokenProvider(
        issuer=mock_server.server_url,
        audience=audience,
        client_id="foo",
        client_secret="bar",
    )

    access_token = await token_provider.get_access_token()
    assert access_token
    decoded_token = await token_verifier.verify(access_token)
    assert decoded_token.header
    assert decoded_token.payload
