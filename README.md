[![Test](https://github.com/svaponi/pyauth0/actions/workflows/run-tests.yml/badge.svg)](https://github.com/svaponi/pyauth0/actions/workflows/run-tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/svaponi/pyauth0/badge.svg?branch=main)](https://coveralls.io/github/svaponi/pyauth0?branch=main)
[![PyPI version](https://badge.fury.io/py/pyauth0.svg)](https://badge.fury.io/py/pyauth0)

# pyauth0

Python utilities for [Auth0](https://auth0.com/).

## Usage

Verify a token.

```python
from pyauth0 import TokenProvider
from urllib.request import Request, urlopen

token_provider = TokenProvider(
    issuer="your-domain.auth0.com",
    audience="https://api.your-domain.com",
    client_id="1234",
    client_secret="secret"
)

# Machine to machine request
response = urlopen(Request(
    "https://api.your-domain.com",
    headers={"authorization": token_provider.get_token().get_authorization()},
))
```

Get a machine-to-machine token.

```python
from pyauth0 import TokenVerifier, Auth0Error

token_verifier = TokenVerifier(
    issuer="your-domain.auth0.com",
    audience="https://your-domain.com/api",
    jwks_cache_ttl=60,  # optional
)
try:
    decoded_token = token_verifier.verify(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
    )
except Auth0Error as error:
    status_code = error.status_code  # suggested status code (401 or 403)
    code = error.code  # pyauth0 error code (example "token_expired")
    description = error.description  # pyauth0 error description (example "Token is expired.")
    raise error

claim_value = decoded_token.payload.get("http://your-tenant.com/claim_name", "default value")
```

## Contribute

If you want to contribute, open a [GitHub Issue](https://github.com/svaponi/pyauth0/issues) and motivate your request.
