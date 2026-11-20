import ipaddress
import re
import secrets
import string
from urllib.parse import urlsplit

ALPHABET = string.ascii_letters + string.digits
CODE_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
MAX_URL_LEN = 2048


def generate_short_code(n: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(n))


def is_valid_code(code: str) -> bool:
    return bool(code) and bool(CODE_RE.match(code))


def normalize_url(raw: str):
    if not isinstance(raw, str):
        return None
    url = raw.strip()
    if not url or len(url) > MAX_URL_LEN or any(c.isspace() for c in url) or any(ord(c) < 32 for c in url):
        return None
    if "://" not in url:
        url = "https://" + url
    try:
        p = urlsplit(url)
        host = p.hostname
        p.port
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not host:
        return None
    if not re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}|[0-9a-fA-F]*:[0-9a-fA-F:.]+|(?:[^\W_](?:[\w-]{0,61}[^\W_])?\.)+[^\W\d_]{2,}", host):
        return None
    if _is_private(host):
        return None
    return url


def _is_private(host: str) -> bool:
    """Не даём сокращать localhost и внутренние адреса (локальная сеть, loopback)."""
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified
    except ValueError:
        return host.lower() in ("localhost",) or host.lower().endswith((".local", ".internal", ".localhost"))


def host_of(url: str) -> str:
    try:
        return urlsplit(url).hostname or ""
    except ValueError:
        return ""
