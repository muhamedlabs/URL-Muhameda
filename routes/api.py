import time
from collections import defaultdict, deque

import secrets

from flask import Blueprint, jsonify, request

import settings
from storage import redis_store as store
from utils.helpers import generate_short_code, host_of, is_valid_code, normalize_url

api_bp = Blueprint("api", __name__)


_hits = defaultdict(deque)


def _limited(ip: str, limit: int = 12, window: int = 60) -> bool:
    now = time.time()
    if len(_hits) > 5000:                      # чистим старые IP, чтобы память не росла бесконечно
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > window]:
            _hits.pop(k, None)
    q = _hits[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False


def _base() -> str:
    return settings.PUBLIC_BASE_URL or request.host_url.rstrip("/")


COOKIE = "mid"


def _client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return request.headers.get("CF-Connecting-IP") or fwd or request.remote_addr or ""


def _is_self(url: str) -> bool:
    h = host_of(url).lower()
    own = {request.host.split(":")[0].lower()}
    if settings.PUBLIC_BASE_URL:
        own.add(host_of(settings.PUBLIC_BASE_URL).lower())
    return h in own


def _owner(create: bool = False):
    token = request.cookies.get(COOKIE)
    fresh = False
    if not token and create:
        token, fresh = secrets.token_urlsafe(24), True
    return (store.owner_id(token) if token else ""), (token if fresh else None)


def _json(payload, status=200):
    resp = jsonify(payload)
    resp.status_code = status
    resp.headers["Cache-Control"] = "no-store"
    return resp


@api_bp.post("/api/shorten")
def shorten():
    data = request.get_json(silent=True) or {}
    raw = data.get("url")
    if not raw:
        return _json({"error": "url_required"}, 400)
    url = normalize_url(raw)
    if not url:
        return _json({"error": "url_invalid"}, 400)
    if _is_self(url):
        return _json({"error": "url_self"}, 400)
    ip = _client_ip()
    if _limited(ip or "?"):
        return _json({"error": "rate_limited"}, 429)
    owner, token = _owner(create=True)
    try:
        code = None
        for _ in range(12):
            c = generate_short_code()
            if store.create(c, url, owner, ip):
                code = c
                break
        if not code:
            return _json({"error": "server"}, 500)
    except Exception as e:
        print("[API] shorten error:", e)
        return _json({"error": "storage_down"}, 503)
    resp = _json({"short_code": code, "original_url": url, "short_url": f"{_base()}/{code}"}, 201)
    if token:
        resp.set_cookie(COOKIE, token, max_age=60 * 60 * 24 * 365, httponly=True, samesite="Lax", secure=request.is_secure)
    return resp


@api_bp.patch("/api/links/<code>")
def edit(code):
    if not is_valid_code(code):
        return _json({"error": "missing"}, 404)
    url = normalize_url((request.get_json(silent=True) or {}).get("url"))
    if not url:
        return _json({"error": "url_invalid"}, 400)
    if _is_self(url):
        return _json({"error": "url_self"}, 400)
    owner, _ = _owner()
    try:
        res = store.update(code, url, owner)
    except Exception as e:
        print("[API] edit error:", e)
        return _json({"error": "storage_down"}, 503)
    if res != "ok":
        return _json({"error": res}, 404 if res == "missing" else 403)
    return _json({"short_code": code, "original_url": url, "short_url": f"{_base()}/{code}"})


@api_bp.get("/api/mine")
def mine():
    owner, _ = _owner()
    if not owner:
        return _json({"links": []})
    try:
        items = store.by_owner(owner)
    except Exception:
        return _json({"error": "storage_down"}, 503)
    return _json({"links": [{"id": i["id"], "short_url": f"{_base()}/{i['id']}", "original_url": i.get("original_url"),
                             "created_at": i.get("created_at")} for i in items]})


@api_bp.get("/api/resolve/<code>")
def resolve(code):
    if not is_valid_code(code):
        return _json({"ok": False}, 404)
    url = store.get_url(code)
    if not url:
        return _json({"ok": False}, 404)
    safe = normalize_url(url)
    if not safe:
        return _json({"ok": False, "error": "unsafe"}, 404)
    return _json({"ok": True, "url": safe, "host": host_of(safe), "short_url": f"{_base()}/{code}"})


@api_bp.get("/api/stats")
def stats():
    return _json({"total_urls": store.count()})


@api_bp.get("/api/health")
def health():
    n = store.count()
    st = store.status()
    return _json({"status": "healthy" if st["redis_ok"] else "degraded", "storage": "redis",
                  "total_urls": n, "redis": bool(st["redis_ok"])}, 200 if st["redis_ok"] else 503)
