from pyauth0 import DecodedToken
from test.const import JWT_IO_TOKEN


def test_decode():
    decoded_token = DecodedToken.decode(JWT_IO_TOKEN)
    assert decoded_token
    assert decoded_token.header
    assert decoded_token.payload
    assert decoded_token.payload.get("name") == "John Doe"
