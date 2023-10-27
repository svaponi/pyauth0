def test_validate_token(token_provider, token_verifier):
    token = token_provider.get_token().access_token
    assert token
    decoded_token = token_verifier.verify(token)
    assert decoded_token.header
    assert decoded_token.payload
