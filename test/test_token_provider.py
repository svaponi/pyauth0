import time

from pyauth0 import TokenProvider
from test.testutils.mock_server import MockServer


def test_get_token_multiple_times_should_reuse_token_if_valid(mock_server: MockServer):
    expected = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
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
    get_token_response = token_provider.get_token()
    assert get_token_response.access_token == expected
    assert len(mock_server.received_requests) == 1

    # second get, the token is still valid, no further requests to server
    get_token_response = token_provider.get_token()
    assert get_token_response.access_token == expected
    assert len(mock_server.received_requests) == 1

    # wait for the token to expire
    time.sleep(1)

    # third get after the token expired, expect a new request to server
    get_token_response = token_provider.get_token()
    assert get_token_response.access_token == expected
    assert len(mock_server.received_requests) == 2
