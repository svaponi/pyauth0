# Usage

Python utilities for Auth0.

### How to

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
    auth0_domain="your-domain.auth0.com",
    api_audience="https://your-domain.com/api",
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
