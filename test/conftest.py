import pytest
import pytest_httpserver

from test.testutils.mock_server import MockServer


@pytest.fixture
def mock_server(httpserver: pytest_httpserver.HTTPServer):
    server = MockServer(httpserver)
    yield server
    server.clear()
