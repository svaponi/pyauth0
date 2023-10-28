import time

import pytest

from pyauth0 import TokenVerifier, TokenProvider
from pyauth0.server.server import start_server_in_thread


@pytest.fixture(scope="session")
def server_baseurl():
    baseurl = start_server_in_thread()
    time.sleep(1)
    print(f"Testing against {baseurl}")
    return baseurl


def test_validate_token_with_local_server(server_baseurl):
    token_provider = TokenProvider(
        issuer=server_baseurl,
        audience="whatever",
        client_id="foo",
        client_secret="bar",
    )
    token_verifier = TokenVerifier(
        issuer=server_baseurl,
        audience="whatever",
        jwks_cache_ttl=60,
    )

    token = token_provider.get_token().access_token
    assert token
    decoded_token = token_verifier.verify(token)
    assert decoded_token.header
    assert decoded_token.payload
