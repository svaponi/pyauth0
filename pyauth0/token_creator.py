import base64
import hashlib
import json
import os
import re
import tempfile
import time
import typing

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from pyauth0.utils import sanitize_issuer


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


def load_rsa_private_key(key_path: str) -> RSAPrivateKey:
    # Load the private key from a file
    with open(key_path, "rb") as f:
        private_pem = f.read()
    private_key = serialization.load_pem_private_key(
        private_pem,
        password=None,  # Use a password if your private key is encrypted
    )
    return private_key


def generate_rsa_private_key() -> RSAPrivateKey:
    return rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=4096
    )


def get_rsa_private_key(key_path: str) -> RSAPrivateKey:
    if not key_path:
        key_dir = tempfile.mkdtemp(prefix="pyauth0-")
        key_path = f"{key_dir}/key.pem"
    if os.path.exists(key_path):
        private_key = load_rsa_private_key(key_path)
    else:
        # Generate an RSA key pair
        private_key = generate_rsa_private_key()
        # Serialize the private key to a PEM format
        private_pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        # Save the private and public keys to files
        with open(key_path, "+wb") as f:
            f.write(private_pem)

    return private_key


class Signer:
    def __init__(self, private_key: RSAPrivateKey = None, private_key_path: str = None):
        super().__init__()
        self.private_key = private_key or get_rsa_private_key(private_key_path)

    @property
    def public_key(self) -> RSAPublicKey:
        return self.private_key.public_key()

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
        signature: typing.Union[bytes, str],
        data: typing.Union[bytes, str],
    ) -> bool:
        if isinstance(signature, str):
            signature = signature.encode("utf-8")
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


class TokenCreator:
    def __init__(self, signer: Signer = None):
        super().__init__()
        self.signer = signer or Signer()
        self._kid = None

    @property
    def kid(self) -> str:
        if not self._kid:
            # Calculate a deterministic "kid" by hashing the public key
            public_key_bytes = self.signer.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            self._kid = hashlib.sha256(public_key_bytes).hexdigest()
        return self._kid

    def jwk(self) -> dict:
        """
        See https://datatracker.ietf.org/doc/html/rfc7517
        """

        # Serialize the public key to get the components (n and e) for the JWK
        public_key = self.signer.private_key.public_key()
        pn = public_key.public_numbers()
        n = _to_base64(_int_to_bytes(pn.n))
        e = _to_base64(_int_to_bytes(pn.e))

        # Extract the modulus (n) and exponent (e) from the PEM-encoded public key
        jwk = {
            "kty": "RSA",
            "kid": self.kid,
            "use": "sig",
            "n": n,
            "e": e,
        }

        return jwk

    def create_token(
        self,
        issuer: str,
        subject: str,
        audience: str,
        expires_in: int,
        scope: str = None,
        extra_claims: dict = None,
    ) -> str:
        header = dict(alg="RS256", typ="JWT", kid=self.kid)
        enc_header = _to_base64(json.dumps(header), no_padding=True)
        issued_at = int(time.time())
        expires_at = issued_at + expires_in
        issuer = f"{sanitize_issuer(issuer)}/"  # trailing slash is required!
        payload = dict(
            iss=issuer,
            exp=expires_at,
            iat=issued_at,
            sub=subject,
            aud=audience,
            scope=scope,
        )
        if extra_claims:
            payload.update(extra_claims)
        enc_payload = _to_base64(json.dumps(payload), no_padding=True)
        to_sign = f"{enc_header}.{enc_payload}"
        signature = _to_base64(self.signer.sign(to_sign), no_padding=True)
        return f"{to_sign}.{signature}"
