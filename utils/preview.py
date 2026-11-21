"""Превью короткой ссылки для мессенджеров: тянем название, описание и картинку целевого сайта.

Работает только для ботов-предпросмотров (Telegram, WhatsApp и т.п.): они получают страницу с og-тегами
целевого сайта, а люди — обычную страницу с переходом. Результат кэшируется.
"""
import http.client
import ipaddress
import re
import socket
import ssl
import threading
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

UA = "Mozilla/5.0 (compatible; MuhamedAdsPreview/1.0; +https://url.muhamedlabs.pro) Twitterbot/1.0"
TIMEOUT = 4.0
MAX_BYTES = 400_000
MAX_HOPS = 4
TTL_OK = 6 * 3600
TTL_FAIL = 10 * 60
CACHE_MAX = 2000

_cache: dict = {}
_lock = threading.Lock()


def _global_ips(host: str, port: int) -> list:
    """Только публичные адреса: защита от обращения во внутреннюю сеть (SSRF)."""
    out = []
    for fam, _t, _p, _c, sa in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
        try:
            ip = ipaddress.ip_address(sa[0])
        except ValueError:
            continue
        if ip.is_global:
            out.append((fam, sa[0]))
    return out


class _Pinned:
    """Подключаемся к проверенному IP, а имя хоста оставляем для Host/SNI (защита от подмены DNS)."""
    _ip = None

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        if isinstance(self, http.client.HTTPSConnection):
            sock = self._context.wrap_socket(sock, server_hostname=self.host)
        self.sock = sock


class _HTTP(_Pinned, http.client.HTTPConnection):
    pass


class _HTTPS(_Pinned, http.client.HTTPSConnection):
    pass


def _fetch(url: str):
    """Возвращает (html, финальный_url) или None."""
    ctx = ssl.create_default_context()
    for _ in range(MAX_HOPS):
        p = urlsplit(url)
        if p.scheme not in ("http", "https") or not p.hostname:
            return None
        port = p.port or (443 if p.scheme == "https" else 80)
        ips = _global_ips(p.hostname, port)
        if not ips:
            return None
        path = (p.path or "/") + (("?" + p.query) if p.query else "")
        conn = None
        try:
            if p.scheme == "https":
                conn = _HTTPS(p.hostname, port, timeout=TIMEOUT, context=ctx)
            else:
                conn = _HTTP(p.hostname, port, timeout=TIMEOUT)
            conn._ip = ips[0][1]
            conn.request("GET", path, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
                                              "Accept-Language": "ru,uk;q=0.9,en;q=0.8", "Accept-Encoding": "identity"})
            r = conn.getresponse()
            if r.status in (301, 302, 303, 307, 308) and r.getheader("Location"):
                url = urljoin(url, r.getheader("Location"))
                continue
            if r.status >= 400 or "html" not in (r.getheader("Content-Type") or "").lower():
                return None
            raw = r.read(MAX_BYTES)
            m = re.search(r"charset=([\w-]+)", r.getheader("Content-Type") or "", re.I) or re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", raw[:4096], re.I)
            enc = (m.group(1).decode() if m and isinstance(m.group(1), bytes) else (m.group(1) if m else "utf-8"))
            try:
                return raw.decode(enc, "replace"), url
            except LookupError:
                return raw.decode("utf-8", "replace"), url
        except (OSError, http.client.HTTPException, ssl.SSLError, ValueError):
            return None
        finally:
            if conn is not None:
                try:
                    conn.close()
                except OSError:
                    pass
    return None


class _Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.icons, self.title, self._in_title, self.done = {}, [], "", False, False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key and "content" in a and key not in self.meta:
                self.meta[key] = a["content"].strip()
        elif tag == "link" and a.get("href"):
            rel = a.get("rel", "").lower()
            if "icon" in rel or "apple-touch-icon" in rel:
                self.icons.append((rel, a.get("sizes", ""), a["href"]))
        elif tag == "title" and not self.title:
            self._in_title = True
        elif tag == "body":
            self.done = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "head":
            self.done = True

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def _clean(s, n):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _best_icon(icons, base):
    def size(i):
        m = re.match(r"(\d+)x\d+", i[1])
        return int(m.group(1)) if m else 0
    cand = sorted((i for i in icons if "mask-icon" not in i[0]), key=lambda i: ("apple" in i[0], size(i)), reverse=True)
    return urljoin(base, cand[0][2]) if cand else ""


def parse(html: str, base: str) -> dict:
    p = _Head()
    try:
        p.feed(html[:300_000])
    except Exception:
        pass
    m = p.meta
    title = m.get("og:title") or m.get("twitter:title") or p.title
    desc = m.get("og:description") or m.get("twitter:description") or m.get("description") or ""
    img = m.get("og:image") or m.get("og:image:url") or m.get("twitter:image") or m.get("twitter:image:src") or ""
    large = bool(img)
    if img:
        img = urljoin(base, img)
    else:
        img = _best_icon(p.icons, base) or urljoin(base, "/favicon.ico")   # нет картинки — логотип сайта
    if urlsplit(img).scheme not in ("http", "https"):
        img, large = "", False

    def num(v):
        return int(v) if v and v.isdigit() else 0
    w, h = num(m.get("og:image:width")), num(m.get("og:image:height"))
    if large and w and w < 400:
        large = False
    return {"title": _clean(title, 120), "desc": _clean(desc, 300), "image": img, "large": large,
            "width": w, "height": h, "site": _clean(m.get("og:site_name", ""), 60)}


def get_preview(url: str):
    """Превью целевой страницы или None (тогда показываем фирменное превью сервиса)."""
    now = time.time()
    with _lock:
        hit = _cache.get(url)
        if hit and hit[0] > now:
            return hit[1]
    data = None
    try:
        got = _fetch(url)
        if got:
            d = parse(*got)
            if d["title"] or d["desc"]:
                data = d
    except Exception as e:
        print("[PREVIEW] error:", e)
    with _lock:
        if len(_cache) >= CACHE_MAX:
            for k in sorted(_cache, key=lambda k: _cache[k][0])[: CACHE_MAX // 4]:
                _cache.pop(k, None)
        _cache[url] = (now + (TTL_OK if data else TTL_FAIL), data)
    return data
