import pytest

from pyauth0 import Auth0Error


def test_validate_token(token_provider, token_verifier):
    token = token_provider.get_token().access_token
    assert token
    decoded_token = token_verifier.verify(token)
    assert decoded_token.header
    assert decoded_token.payload


def test_invalid_token(token_provider, token_verifier):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    with pytest.raises(Auth0Error) as info:
        token_verifier.verify(token)
    assert info.value.code == "invalid_token"
