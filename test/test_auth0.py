import json

import pytest

from auth0.auth0 import TokenPayload, Auth0

AUTH0_DOMAIN = "your-tenant.us.auth0.com"
API_AUDIENCE = "https://api.your-tenant.com"
CLIENT_ID = "9H1uYwvag..."
TEST_USER = "test user email"
TEST_PASSWORD = "test user password"


@pytest.fixture
def get_token():
    def _get_token(
            auth0_domain=AUTH0_DOMAIN,
            api_audience=API_AUDIENCE,
            user=TEST_USER,
            password=TEST_PASSWORD,
            client_id=CLIENT_ID,
    ):
        from urllib import request, parse

        url = f"https://{auth0_domain}/oauth/token"
        req = request.Request(url, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        data = {
            "grant_type": "password",
            "username": user,
            "password": password,
            "audience": api_audience,
            "client_id": client_id,
        }
        response = request.urlopen(req, data=parse.urlencode(data).encode())
        if response.status != 200:
            raise RuntimeError(f"POST {url} >> {response.status}")
        access_token = json.loads(response.read()).get("access_token", None)
        if not access_token:
            raise RuntimeError(f"Missing access_token")
        return access_token

    return _get_token


@pytest.fixture
def auth0():
    return Auth0(
        auth0_domain=AUTH0_DOMAIN, api_audience=API_AUDIENCE, jwks_cache_ttl=60
    )


def test_parse_token():
    # default token shown on https://jwt.io/
    JOHN_DOE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    payload = TokenPayload.parse_token(JOHN_DOE_TOKEN)
    assert payload.get("name") == "John Doe"


def test_validate_token(auth0, get_token):
    token = get_token()
    payload = auth0.validate_token(token)
    assert payload.get_required_claim("http://your-tenant.com/claim_name") == "your claim value"
