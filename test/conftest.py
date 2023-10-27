import dataclasses
import os

import dotenv
import pytest

from pyauth0 import TokenVerifier, TokenProvider


@dataclasses.dataclass
class TestConfig:
    AUTH0_DOMAIN: str
    API_AUDIENCE: str
    CLIENT_ID: str
    CLIENT_SECRET: str


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    dotenv.load_dotenv(dotenv.find_dotenv(".env"))
    dotenv.load_dotenv(dotenv.find_dotenv(".env.test"))
    return TestConfig(
        AUTH0_DOMAIN=os.getenv("AUTH0_DOMAIN"),
        API_AUDIENCE=os.getenv("API_AUDIENCE"),
        CLIENT_ID=os.getenv("CLIENT_ID"),
        CLIENT_SECRET=os.getenv("CLIENT_SECRET"),
    )


@pytest.fixture(scope="session")
def token_verifier(test_config):
    return TokenVerifier(
        auth0_domain=test_config.AUTH0_DOMAIN,
        api_audience=test_config.API_AUDIENCE,
        jwks_cache_ttl=60,
    )


@pytest.fixture
def token_provider(test_config):
    return TokenProvider(
        issuer=test_config.AUTH0_DOMAIN,
        audience=test_config.API_AUDIENCE,
        client_id=test_config.CLIENT_ID,
        client_secret=test_config.CLIENT_SECRET,
    )
