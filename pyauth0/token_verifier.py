import abc
import dataclasses
import datetime
import json
from typing import Optional
from urllib.request import urlopen

from jose import jwt

from pyauth0.errors import Auth0Error
from pyauth0.utils import _sanitize_issuer


@dataclasses.dataclass
class DecodedToken:
    """
    Helper class to access properties inside the token payload
    """

    header: dict
    payload: dict

    @staticmethod
    def decode(token: str) -> "DecodedToken":
        """
        Decodes the token payload

        :param token: the token as string
        :returns The dict representation of the claims set, assuming the signature is valid
                and all requested data validation passes.
        """
        header = jwt.get_unverified_header(token)
        payload = jwt.get_unverified_claims(token)
        return DecodedToken(payload=payload, header=header)


class JwksProvider(abc.ABC):
    """
    Provides the JSON Web Key Sets.
    See https://auth0.com/docs/tokens/json-web-tokens/json-web-key-sets
    """

    @abc.abstractmethod
    def get(self):
        pass


class _JwksProviderBase(JwksProvider):
    def __init__(self, issuer: str) -> None:
        self._issuer = issuer

    def get(self):
        url = self._issuer + "/.well-known/jwks.json"
        return json.loads(urlopen(url).read())


class _JwksProviderCacheDecorator(JwksProvider):
    def __init__(self, delegate: JwksProvider, ttl: int) -> None:
        self._delegate = delegate
        self._ttl = ttl
        self._jwks = None
        self._expires_at = None

    def get(self):
        if not self._expires_at or self._expires_at <= datetime.datetime.now():
            self._jwks = self._delegate.get()
            self._expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self._ttl
            )
        return self._jwks


class TokenVerifier:
    def __init__(
        self,
        issuer: str,
        audience: str,
        jwks_provider: Optional[JwksProvider] = None,
        jwks_cache_ttl: Optional[int] = None,
    ):
        self._issuer = _sanitize_issuer(issuer)
        self._audience = audience
        # this is not safe to change without double-checking configuration in Auth0 dashboard + current codebase
        self._algorithms = ["RS256"]
        if jwks_provider:
            self._jwks_provider = jwks_provider
        else:
            self._jwks_provider = _JwksProviderBase(self._issuer)
            if jwks_cache_ttl:
                self._jwks_provider = _JwksProviderCacheDecorator(
                    self._jwks_provider, jwks_cache_ttl
                )

    def verify(self, token: str) -> DecodedToken:
        """
        Decodes and verifies the token payload

        :param token: the token as string
        :returns The dict representation of the claims set, assuming the signature is valid
                and all requested data validation passes.
        """
        if not token:
            raise Auth0Error(
                status_code=401, code="invalid_token", description="Token is missing."
            )

        try:
            header = jwt.get_unverified_headers(token)
        except jwt.JWSError as error:
            raise Auth0Error(
                status_code=401,
                code="malformed_token",
                description="Malformed token.",
            ) from error

        if header["alg"] == "HS256":
            raise Auth0Error(
                status_code=401,
                code="invalid_token",
                description="Invalid token. Use an RS256 signed JWT Access Token.",
            )

        rsa_key = {}
        jwks = self._jwks_provider.get()
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if not rsa_key:
            raise Auth0Error(
                status_code=401,
                code="invalid_token",
                description="Unable to find appropriate key.",
            )

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=self._algorithms,
                audience=self._audience,
                issuer=self._issuer + "/",
            )
        except jwt.ExpiredSignatureError as error:
            raise Auth0Error(
                status_code=401,
                code="token_expired",
                description="Token is expired.",
            ) from error
        except jwt.JWTClaimsError as error:
            raise Auth0Error(
                status_code=401,
                code="invalid_claims",
                description="Incorrect claims, check audience and issuer.",
            ) from error
        except Exception as error:
            raise Auth0Error(
                status_code=401, code="invalid_token", description=str(error)
            ) from error

        return DecodedToken(payload=payload, header=header)
