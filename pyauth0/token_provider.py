import dataclasses
import datetime
import json
import typing
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pyauth0.utils import _sanitize_issuer


@dataclasses.dataclass
class GetTokenResponse:
    response_body: dict
    access_token: str
    token_type: str
    expires_at: datetime.datetime

    def get_authorization(self) -> str:
        return f"{self.token_type} {self.access_token}"

    def is_expired(self, skew_seconds: int = None):
        if self.expires_at is not None:
            now = datetime.datetime.now()
            if skew_seconds:
                now += datetime.timedelta(seconds=skew_seconds)
            return now >= self.expires_at
        return True


class TokenProvider:
    def __init__(
        self,
        issuer,
        audience,
        client_id,
        client_secret,
        payload_customizer: typing.Callable[[dict], dict] = None,
    ):
        """
        :param issuer: hostname of the tenant in Auth0, example `spartanapproach-dev.us.auth0.com`
        :param audience: API identifier
        :param client_id:
        :param client_secret:
        """
        if not issuer:
            raise ValueError("missing issuer")
        if not audience:
            raise ValueError("missing audience")
        if not client_id:
            raise ValueError("missing client_id")
        if not client_secret:
            raise ValueError("missing client_secret")
        self._issuer = _sanitize_issuer(issuer)
        self._audience = audience
        self._client_id = client_id
        self._client_secret = client_secret
        self._payload_customizer = payload_customizer
        self._cache: typing.Optional[GetTokenResponse] = None

    def get_token(self) -> GetTokenResponse:
        if self._cache is None or self._cache.is_expired():
            url = f"{self._issuer}/oauth/token"
            payload = {
                "grant_type": "client_credentials",
                "audience": self._audience,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if self._payload_customizer:
                payload = self._payload_customizer(payload)

            request_data = json.dumps(payload)
            request = Request(
                url,
                method="POST",
                data=request_data.encode("utf-8"),
                headers={"content-type": "application/json"},
            )

            try:
                response = urlopen(request)
            except HTTPError as error:
                raise RuntimeError(
                    f"Invalid response POST {url} {request_data} >> {error.code}"
                )

            response_data = response.read().decode("utf-8")
            if response.status != 200:
                raise RuntimeError(
                    f"Invalid response POST {url} {request_data} >> {response.status} {response_data}"
                )

            response_dict = json.loads(response_data)
            self._cache = GetTokenResponse(
                response_body=response_dict,
                access_token=response_dict.get("access_token"),
                token_type=response_dict.get("token_type"),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_dict.get("expires_in")),
            )

        return self._cache
