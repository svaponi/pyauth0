import base64
import json

import pytest

from pyauth0.token_creator import Signer, TokenCreator
from test.testutils.mock_server import MockServer


def test_signer():
    data = "Hello, World!"
    signer = Signer()
    signature = signer.sign(data)
    assert signer.verify_signature(signature, data)


@pytest.mark.asyncio
async def test_token_creator(
    mock_server: MockServer,
):
    signer = Signer()
    token_creator = TokenCreator(signer)

    response_data = token_creator.jwk()
    mock_server.respond_with_json(r"/.well-known/jwks.json", response_data)

    token = token_creator.create_token(
        mock_server.server_url,
        subject="nobody",
        audience="https://api.your-domain.com",
        expires_in=3600,
    )

    assert token

    header, payload, _ = token.split(".", maxsplit=2)

    header = base64.urlsafe_b64decode(header + "==")
    header = json.loads(header)
    assert header.get("typ") == "JWT"
    assert header.get("kid") == token_creator.kid

    payload = base64.urlsafe_b64decode(payload + "==")
    payload = json.loads(payload)
    assert payload.get("iss") == f"{mock_server.server_url}/"
    assert payload.get("sub") == "nobody"
    assert payload.get("aud") == "https://api.your-domain.com"

    signed_data, _, signature = token.rpartition(".")
    signature = base64.urlsafe_b64decode(signature + "==")
    assert signer.verify_signature(signature, signed_data)
