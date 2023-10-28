import pytest

from pyauth0 import Auth0Error, DecodedToken


def test_validate_token(token_provider, token_verifier):
    access_token = token_provider.get_token().access_token
    assert access_token
    decoded_token = token_verifier.verify(access_token)
    assert decoded_token.header
    assert decoded_token.payload


def test_get_token(token_provider, token_verifier):
    access_token = token_provider.get_token().access_token
    assert access_token
    authorization = token_provider.get_token().get_authorization()
    assert authorization
    assert authorization.lower().startswith("bearer ")
    assert authorization[7:] == access_token


# See https://jwt.io/
JWT_IO_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


def test_invalid_token(token_provider, token_verifier):
    with pytest.raises(Auth0Error) as info:
        token_verifier.verify(JWT_IO_TOKEN)
    assert info.value.code == "invalid_token"
    assert "Invalid token" in info.value.description


def test_missing_token(token_provider, token_verifier):
    with pytest.raises(Auth0Error) as info:
        token_verifier.verify(None)
    assert info.value.code == "invalid_token"
    assert "Token is missing" in info.value.description


def test_malformed_token(token_provider, token_verifier):
    with pytest.raises(Auth0Error) as info:
        token_verifier.verify("gibberish")
    assert info.value.code == "invalid_token"
    assert "Malformed token" in info.value.description


def test_decode(token_provider, token_verifier):
    decoded_token = DecodedToken.decode(JWT_IO_TOKEN)
    assert decoded_token
    assert decoded_token.header
    assert decoded_token.payload
    assert decoded_token.payload.get("name") == "John Doe"
