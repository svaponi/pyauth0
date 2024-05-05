import re


def sanitize_issuer(issuer: str) -> str:
    if not issuer:
        raise ValueError("missing issuer")
    if not re.match(r"^https?://", issuer):
        issuer = "https://" + issuer
    if issuer.endswith("/"):
        issuer = re.sub(r"/+$", "", issuer)
    return issuer
