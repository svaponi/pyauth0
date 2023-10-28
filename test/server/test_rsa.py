from pyauth0.server.server import _Rsa


def test_rsa():
    data = b"Hello, World!"
    rsa = _Rsa()
    signature = rsa.sign(data)
    assert rsa.verify_signature(signature, data)
