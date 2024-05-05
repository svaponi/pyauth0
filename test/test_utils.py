import pytest

from pyauth0.utils import sanitize_issuer


def test_sanitize_issuer():
    assert sanitize_issuer("https://your-domain.com") == "https://your-domain.com"
    assert sanitize_issuer("https://your-domain.com/") == "https://your-domain.com"
    assert sanitize_issuer("your-domain.com") == "https://your-domain.com"
    with pytest.raises(ValueError):
        assert sanitize_issuer("")
    with pytest.raises(ValueError):
        assert sanitize_issuer(None)
