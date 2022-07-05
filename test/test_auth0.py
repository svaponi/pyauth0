import json
import os

import pytest

from pyauth0 import TokenPayload, Auth0

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
CLIENT_ID = os.getenv("CLIENT_ID")
TEST_USER = os.getenv("TEST_USER")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
CLAIM = os.getenv("CLAIM")
CLAIM_VALUE = os.getenv("CLAIM_VALUE")


@pytest.fixture
def get_token():
    def _get_token(
            auth0_domain=AUTH0_DOMAIN,
            api_audience=API_AUDIENCE,
            user=TEST_USER,
            password=TEST_PASSWORD,
            client_id=CLIENT_ID,
    ):
        from urllib import request, parse, error

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
        try:
            response = request.urlopen(req, data=parse.urlencode(data).encode())
        except error.HTTPError as error:
            raise RuntimeError(f"POST {url} >> {error.code}")
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
    assert payload.get_required_claim(CLAIM) == CLAIM_VALUE
