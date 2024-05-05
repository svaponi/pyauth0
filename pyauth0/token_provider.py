import dataclasses
import datetime
import typing

from pyauth0.utils import sanitize_issuer


@dataclasses.dataclass
class GetTokenResponse:
    response_body: dict
    access_token: str
    token_type: str
    expires_at: datetime.datetime

    @property
    def authorization(self) -> str:
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
        :param issuer: hostname of the tenant in Auth0, example `your-domain.auth0.com`
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
        self._issuer = sanitize_issuer(issuer)
        self._audience = audience
        self._client_id = client_id
        self._client_secret = client_secret
        self._payload_customizer = payload_customizer
        self._get_token_response: typing.Optional[GetTokenResponse] = None

    async def get_token(self) -> GetTokenResponse:
        if not self._get_token_response or self._get_token_response.is_expired():
            url = f"{self._issuer}/oauth/token"
            payload = {
                "grant_type": "client_credentials",
                "audience": self._audience,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if self._payload_customizer:
                payload = self._payload_customizer(payload)

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers={"content-type": "application/json"},
                    )
            except Exception as error:
                raise RuntimeError(f"Invalid response POST {url} >> {error}")
            if response.status_code != 200:
                raise RuntimeError(
                    f"Invalid response POST {url} >> {response.status_code} {response.text}"
                )
            response_dict = response.json()
            self._get_token_response = GetTokenResponse(
                response_body=response_dict,
                access_token=response_dict.get("access_token"),
                token_type=response_dict.get("token_type"),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_dict.get("expires_in")),
            )

        return self._get_token_response

    async def get_access_token(self) -> str:
        res = await self.get_token()
        return res.access_token

    async def get_authorization(self) -> str:
        res = await self.get_token()
        return res.authorization
