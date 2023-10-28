import asyncio
import base64
import hashlib
import json
import logging
import os.path
import random
import re
import threading
import time
import traceback
import typing

from aiohttp import web
from aiohttp.abc import Request
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from pyauth0.utils import _sanitize_issuer


def _int_to_bytes(n: int):
    num_bytes = (n.bit_length() + 7) // 8
    return n.to_bytes(length=num_bytes, byteorder="big")


def _to_base64(data: typing.Union[bytes, str], no_padding=False) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    b64encoded = base64.urlsafe_b64encode(data).decode("utf-8")
    if no_padding:
        b64encoded = re.sub("=+$", "", b64encoded)
    return b64encoded


class _Rsa:
    def __init__(self, key_path=None):
        super().__init__()
        if key_path:
            self.private_key = self.load_rsa_private_key(key_path)
        else:
            self.private_key = self.generate_rsa_private_key()

    @property
    def public_key(self) -> RSAPublicKey:
        return self.private_key.public_key()

    @classmethod
    def load_rsa_private_key(cls, key_path: str) -> RSAPrivateKey:
        if os.path.exists(key_path):
            # Load the private key from a file
            with open(key_path, "rb") as f:
                private_pem = f.read()
            private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,  # Use a password if your private key is encrypted
            )
        else:
            # Generate an RSA key pair
            private_key = cls.generate_rsa_private_key()
            # Serialize the private key to a PEM format
            private_pem = private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
            # Save the private and public keys to files
            with open(key_path, "wb") as f:
                f.write(private_pem)

        return private_key

    @classmethod
    def generate_rsa_private_key(cls) -> RSAPrivateKey:
        return rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537, key_size=4096
        )

    def get_public_pem(self):
        return self.public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH,
        )

    def sign(self, data: typing.Union[bytes, str]) -> bytes:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return self.private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())

    def verify_signature(
        self,
        signature: bytes,
        data: typing.Union[bytes, str],
    ) -> bool:
        if isinstance(data, str):
            data = data.encode("utf-8")
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False


class _Jwt:
    def __init__(self):
        super().__init__()
        key_path = f"{os.path.dirname(__file__)}/private_key.pem"
        self._rsa = _Rsa(key_path)
        self._kid = None

    @property
    def kid(self) -> str:
        if not self._kid:
            # Calculate a deterministic "kid" by hashing the public key
            public_key_bytes = self._rsa.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            self._kid = hashlib.sha256(public_key_bytes).hexdigest()
        return self._kid

    def jwks(self) -> dict:
        # Serialize the public key to get the components (n and e) for the JWKS
        public_key = self._rsa.private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Calculate a deterministic "kid" by hashing the public key
        kid = hashlib.sha256(public_key_bytes).hexdigest()

        pn = public_key.public_numbers()
        n = _to_base64(_int_to_bytes(pn.n))
        e = _to_base64(_int_to_bytes(pn.e))

        # Extract the modulus (n) and exponent (e) from the PEM-encoded public key
        public_key_dict = {
            "kty": "RSA",
            "kid": kid,
            "use": "sig",
            "n": n,
            "e": e,
        }

        # JWKS structure with a single key
        jwks = {"keys": [public_key_dict]}

        return jwks

    def create_token(
        self,
        expires_in: int,
        subject: str,
        issuer: str,
        audience: str,
        scope: str = None,
        gty: str = "client-credentials",
        extra_claims: dict = None,
    ) -> str:
        header = dict(alg="RS256", typ="JWT", kid=self.kid)
        enc_header = _to_base64(json.dumps(header), no_padding=True)
        issued_at = int(time.time())
        expires_at = issued_at + expires_in
        issuer = f"{_sanitize_issuer(issuer)}/"  # trailing slash is required!
        payload = dict(
            iss=issuer,
            exp=expires_at,
            iat=issued_at,
            sub=subject,
            aud=audience,
            scope=scope,
            gty=gty,
        )
        if extra_claims:
            payload.update(extra_claims)
        enc_payload = _to_base64(json.dumps(payload), no_padding=True)
        to_sign = f"{enc_header}.{enc_payload}"
        signature = _to_base64(self._rsa.sign(to_sign), no_padding=True)
        return f"{to_sign}.{signature}"


class Server(web.Application):
    def __init__(self):
        super().__init__()
        self.jwt = _Jwt()
        self.add_routes(
            [
                web.get("/.well-known/jwks.json", self._well_known_jwks),
                web.get(
                    "/.well-known/openid-configuration",
                    self._well_known_openid_configuration,
                ),
                web.post("/oauth/token", self._get_token),
                web.get("/{not_found:.*}", self._handle_not_found),
            ]
        )

    async def _handle_not_found(self, request: Request):
        endpoints = []
        for route in self.router.routes():
            if route.method != "HEAD" and route.resource.canonical != "/{not_found}":
                endpoints.append(
                    dict(method=route.method, path=route.resource.canonical)
                )

        return self._response(
            dict(
                status_code=404,
                message=f"not found",
                endpoints=endpoints,
            ),
            status_code=404,
        )

    async def _well_known_jwks(self, request: Request):
        try:
            return self._response(self.jwt.jwks())
        except Exception as error:
            return self._error_response(error)

    async def _well_known_openid_configuration(self, request: Request):
        try:
            baseurl = request.url.origin()
            payload = {
                "jwks_uri": f"{baseurl}/.well-known/jwks.json",
                "issuer": f"{baseurl}",
            }
            return self._response(payload)
        except Exception as error:
            return self._error_response(error)

    async def _get_token(self, request: Request):
        try:
            expires_in = 3600
            access_token = self.jwt.create_token(
                issuer=str(request.url.origin()),
                expires_in=expires_in,
                subject="foobar",
                audience="whatever",
            )
            payload = {
                "access_token": access_token,
                "expires_in": expires_in,
                "scope": "",
                "token_type": "bearer",
            }
            return self._response(payload)
        except Exception as error:
            return self._error_response(error)

    def _response(self, payload: dict, status_code: int = 200) -> web.Response:
        return web.Response(
            text=json.dumps(payload),
            status=status_code,
            headers={"Content-type": "application/json"},
        )

    def _error_response(self, error: Exception) -> web.Response:
        logging.exception(error)
        return self._response(
            dict(
                status_code=500,
                error=str(error),
                stack_trace=traceback.format_exc().splitlines(keepends=False),
            ),
            status_code=500,
        )


def start_server():
    host = "localhost"
    port = random.randint(8000, 9000)
    server = Server()

    async def _on_startup(_app: web.Application) -> None:
        print(f"Started on http://{host}:{port}")

    server.on_startup.append(_on_startup)
    web.run_app(server, port=port, host=host)


def start_server_in_thread():
    host = "localhost"
    port = random.randint(8000, 9000)

    async def _on_startup(_app: web.Application) -> None:
        print(f"Started on http://{host}:{port}")

    server = Server()
    server.on_startup.append(_on_startup)
    runner = web.AppRunner(server)

    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, host, port)
        loop.run_until_complete(site.start())
        loop.run_forever()

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    return f"http://{host}:{port}"


if __name__ == "__main__":
    start_server()
