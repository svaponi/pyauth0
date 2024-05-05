import time

import pytest

from pyauth0 import TokenProvider
from test.const import JWT_IO_TOKEN
from test.testutils.mock_server import MockServer


@pytest.mark.asyncio
async def test_get_token_multiple_times_should_reuse_token_if_valid(
    mock_server: MockServer,
):
    expected = JWT_IO_TOKEN
    response_data = {
        "access_token": expected,
        "scope": "read write",
        "expires_in": 1,
        "token_type": "bearer",
    }
    mock_server.respond_with_json(r".*", response_data)

    token_provider = TokenProvider(
        issuer=mock_server.server_url,
        audience="AUDIENCE",
        client_id="CLIENT_ID",
        client_secret="CLIENT_SECRET",
    )

    # first get, expect one request to server
    access_token = await token_provider.get_access_token()
    assert access_token == expected
    assert len(mock_server.received_requests) == 1

    # second get, the token is still valid, no further requests to server
    access_token = await token_provider.get_access_token()
    assert access_token == expected
    assert len(mock_server.received_requests) == 1

    # wait for the token to expire
    time.sleep(1)

    # third get after the token expired, expect a new request to server
    access_token = await token_provider.get_access_token()
    assert access_token == expected
    assert len(mock_server.received_requests) == 2
