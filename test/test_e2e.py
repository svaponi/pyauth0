import os

import dotenv
import pytest

from pyauth0 import TokenVerifier, TokenProvider


@pytest.mark.asyncio
async def test_validate_token_e2e():
    dotenv.load_dotenv()

    issuer = os.getenv("AUTH0_ISSUER")
    audience = os.getenv("AUTH0_AUDIENCE")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")

    if None in (issuer, audience, client_secret, client_id):
        pytest.skip("missing env vars")

    token_verifier = TokenVerifier(
        issuer=issuer,
        audience=audience,
        jwks_cache_ttl=60,
    )

    token_provider = TokenProvider(
        issuer=issuer,
        audience=audience,
        client_id=client_id,
        client_secret=client_secret,
    )

    access_token = await token_provider.get_access_token()
    assert access_token
    decoded_token = await token_verifier.verify(access_token)
    assert decoded_token.header
    assert decoded_token.payload
