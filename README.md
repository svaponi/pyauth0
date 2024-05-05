# pyauth0

[![Test](https://github.com/svaponi/pyauth0/actions/workflows/run-tests.yml/badge.svg)](https://github.com/svaponi/pyauth0/actions/workflows/run-tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/svaponi/pyauth0/badge.svg?branch=main)](https://coveralls.io/github/svaponi/pyauth0?branch=main)
[![PyPI version](https://badge.fury.io/py/pyauth0.svg)](https://badge.fury.io/py/pyauth0)

Python utilities for [Auth0](https://auth0.com/).

- [Install](#install)
- [Usage](#usage)
  - [Get a machine-to-machine token](#get-a-machine-to-machine-token)
  - [Verify a token](#verify-a-token)
- [Contribute](#contribute)

## Install

```shell
pip install pyauth0
```

## Usage

### Get a machine-to-machine token

```python
import asyncio
import httpx
from pyauth0 import TokenProvider

token_provider = TokenProvider(
    issuer="your-domain.auth0.com",
    audience="https://api.your-domain.com",
    client_id="1234",
    client_secret="secret"
)


async def main():
    authorization = await token_provider.get_authorization()
    async with httpx.AsyncClient() as client:
        # Machine to machine request
        response = await client.get(
            "https://api.your-domain.com",
            headers={"authorization": authorization},
        )
        print(response.content)


asyncio.run(main())
```

### Verify a token

```python
import asyncio

from pyauth0 import TokenVerifier, Auth0Error

token_verifier = TokenVerifier(
    issuer="your-domain.auth0.com",
    audience="https://api.your-domain.com",
    jwks_cache_ttl=60,  # optional
)


async def main():
    try:
        decoded_token = await token_verifier.verify(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
        )
    except Auth0Error as error:
        status_code = error.status_code  # suggested status code (401 or 403)
        code = error.code  # auth0 error code (example "token_expired")
        description = error.description  # auth0 error description (example "Token is expired.")
        raise error

    claim_value = decoded_token.payload.get("http://your-domain.com/claim_name", "default value")


asyncio.run(main())
```

## Contribute

If you want to contribute, open a [GitHub Issue](https://github.com/svaponi/pyauth0/issues) and motivate your request.
