import re


def _sanitize_issuer(issuer: str):
    issuer = re.sub("/$", "", issuer)
    if not re.match("^https?://", issuer):
        issuer = f"https://{issuer}"
    return issuer
