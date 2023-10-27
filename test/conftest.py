import dataclasses
import os

import dotenv
import pytest

from pyauth0 import TokenVerifier, TokenProvider


@dataclasses.dataclass
class TestConfig:
    ISSUER: str
    AUDIENCE: str
    CLIENT_ID: str
    CLIENT_SECRET: str


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    dotenv.load_dotenv(dotenv.find_dotenv(".env"))
    dotenv.load_dotenv(dotenv.find_dotenv(".env.test"))
    return TestConfig(
        ISSUER=os.getenv("AUTH0_ISSUER"),
        AUDIENCE=os.getenv("AUTH0_AUDIENCE"),
        CLIENT_ID=os.getenv("AUTH0_CLIENT_ID"),
        CLIENT_SECRET=os.getenv("AUTH0_CLIENT_SECRET"),
    )


@pytest.fixture(scope="session")
def token_verifier(test_config):
    return TokenVerifier(
        issuer=test_config.ISSUER,
        audience=test_config.AUDIENCE,
        jwks_cache_ttl=60,
    )


@pytest.fixture
def token_provider(test_config):
    return TokenProvider(
        issuer=test_config.ISSUER,
        audience=test_config.AUDIENCE,
        client_id=test_config.CLIENT_ID,
        client_secret=test_config.CLIENT_SECRET,
    )
