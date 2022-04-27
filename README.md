# pyauth0

Library for Auth0 token validation.

## Usage

```python
from auth0.auth0 import Auth0, Auth0Error

auth0 = Auth0(
    auth0_domain="your-tenant-dev.us.auth0.com",
    api_audience="https://api-dev.your-tenant.com",
    jwks_cache_ttl=60,  # optional
)
try:
    token_payload = auth0.validate_auth_header(
        "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
    )
except Auth0Error as error:
    status_code = error.status_code  # suggested status code (401 or 403)
    code = error.code  # auth0 error code (example "invalid_header")
    description = error.description  # auth0 error description (example "Unable to parse authentication token")
    raise

claim_value = token_payload.get_claim("http://your-tenant.com/claim_name", "default value")
```
