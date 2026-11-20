import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Optional

import redis

import settings

ROOT = "shorten_links_database:"
PREV_ROOT = "MuhamedLabs:URL:"
LINKS = ROOT + "Links:"
OWNERS = ROOT + "Owners:"
STATS = ROOT + "Stats"
LEGACY = "Url:"
LEGACY_IDX = "UrlIdx:"

_lock = threading.Lock()
_client: Optional[redis.Redis] = None
_mem: Dict[str, str] = {}
_file_cache = {"mtime": 0.0, "data": {}}
_state = {"redis_ok": None, "last_error": "", "last_backup": 0.0}


def client() -> redis.Redis:
    global _client
    with _lock:
        if _client is None:
            _client = redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB, decode_responses=True,
                socket_connect_timeout=3, socket_timeout=3, health_check_interval=30, retry_on_timeout=True,
            )
        return _client


def _mark(ok: bool, err: str = ""):
    _state["redis_ok"] = ok
    _state["last_error"] = "" if ok else err


def status() -> dict:
    return dict(_state)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def visit(code: str) -> None:
    try:
        r = client()
        if r.exists(LINKS + code):
            n = r.hincrby(LINKS + code, "clicks", 1)
            r.hincrby(STATS, "visits", 1)
            if n > int(r.hget(STATS, "top") or 0):
                r.hset(STATS, "top", n)
    except redis.RedisError as e:
        _mark(False, str(e))


def stats() -> dict:
    try:
        r = client()
        h = r.hgetall(STATS)
        return {"visits": int(h.get("visits", 0)), "top": int(h.get("top", 0))}
    except (redis.RedisError, ValueError):
        return {"visits": 0, "top": 0}


def _short(code: str) -> str:
    base = settings.PUBLIC_BASE_URL or "https://url.muhamedlabs.pro"
    return f"{base}/{code}"


def owner_id(token: str) -> str:
    return "anon:" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:24]


def _read_file() -> Dict[str, dict]:
    path = settings.DATA_FILE
    try:
        m = os.stat(path).st_mtime
    except OSError:
        return {}
    if m == _file_cache["mtime"]:
        return _file_cache["data"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        data = {i["id"]: i for i in items if i.get("id") and i.get("original_url")}
    except Exception as e:
        print("[FILE] read error:", e)
        return _file_cache["data"]
    _file_cache.update(mtime=m, data=data)
    return data


def _write_file(data: Dict[str, dict]) -> None:
    path = settings.DATA_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    items = [dict(v, id=k) for k, v in sorted(data.items())]
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    os.replace(tmp, path)
    try:
        _file_cache.update(mtime=os.stat(path).st_mtime, data=dict(data))
    except OSError:
        pass


def get_url(code: str) -> Optional[str]:
    try:
        v = client().hget(LINKS + code, "original_url") or client().hget(LEGACY + code, "original_url")
        _mark(True)
        if v:
            _mem[code] = v
            return v
        _mem.pop(code, None)
        return None
    except redis.RedisError as e:
        _mark(False, str(e))
        print("[REDIS] get error:", e)
    return _mem.get(code) or (_read_file().get(code) or {}).get("original_url")


def get_link(code: str) -> Optional[dict]:
    return client().hgetall(LINKS + code) or None


def scan_all() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    r = client()
    keys = list(r.scan_iter(match=LINKS + "*", count=500))
    if not keys:
        return out
    pipe = r.pipeline(transaction=False)
    for k in keys:
        pipe.hgetall(k)
    for k, v in zip(keys, pipe.execute()):
        if v.get("original_url"):
            out[k[len(LINKS):]] = v
    return out


def count() -> Optional[int]:
    try:
        n = sum(1 for _ in client().scan_iter(match=LINKS + "*", count=500))
        _mark(True)
        return n
    except redis.RedisError as e:
        _mark(False, str(e))
        return None


def create(code: str, url: str, owner: str = "", ip: str = "") -> bool:
    r = client()
    if not r.hsetnx(LINKS + code, "id", code):
        return False
    now = _now()
    r.hset(LINKS + code, mapping={
        "short_id": _short(code), "original_url": url,
        "created_at": now, "updated_at": now,
        "created_by": owner, "created_ip": ip,
    })
    if owner and owner != "legacy":
        r.sadd(OWNERS + owner, code)
    r.hincrby(STATS, "created:" + _today(), 1)
    _mem[code] = url
    return True


def update(code: str, url: str, owner: str) -> str:
    r = client()
    rec = r.hgetall(LINKS + code)
    if not rec:
        return "missing"
    if not owner or rec.get("created_by") != owner:
        return "forbidden"
    r.hset(LINKS + code, mapping={"original_url": url, "updated_at": _now()})
    _mem[code] = url
    return "ok"


def by_owner(owner: str) -> list:
    r = client()
    codes = sorted(r.smembers(OWNERS + owner))
    pipe = r.pipeline(transaction=False)
    for c in codes:
        pipe.hgetall(LINKS + c)
    return [dict(v, id=c) for c, v in zip(codes, pipe.execute()) if v]


def migrate_legacy() -> int:
    r = client()
    for k in list(r.scan_iter(match=PREV_ROOT + "*", count=500)):
        r.rename(k, ROOT + k[len(PREV_ROOT):])
    keys = list(r.scan_iter(match=LEGACY + "*", count=500))
    moved = 0
    for k in keys:
        rec = r.hgetall(k)
        code, url = k[len(LEGACY):], rec.get("original_url")
        if not url:
            continue
        r.hsetnx(LINKS + code, "id", code)
        r.hsetnx(LINKS + code, "original_url", url)
        r.hsetnx(LINKS + code, "short_id", rec.get("short_id") or _short(code))
        r.hsetnx(LINKS + code, "created_by", "legacy")
        moved += 1
    if moved:
        backup_once()
        for k in keys:
            code = k[len(LEGACY):]
            if r.hget(LINKS + code, "original_url"):
                r.delete(k)
    for k in r.scan_iter(match=LEGACY_IDX + "*", count=500):
        r.delete(k)
    return moved


def seed_from_file() -> int:
    try:
        if count():
            return 0
        n = 0
        for code, rec in _read_file().items():
            if create(code, rec["original_url"], rec.get("created_by", "legacy"), rec.get("created_ip", "")):
                for f in ("created_at", "updated_at"):
                    if rec.get(f):
                        client().hset(LINKS + code, f, rec[f])
                n += 1
        if n:
            print(f"[SEED] {n}")
        return n
    except redis.RedisError as e:
        _mark(False, str(e))
        print("[SEED] Redis:", e)
        return 0


def backup_once() -> bool:
    try:
        data = scan_all()
        _mark(True)
    except redis.RedisError as e:
        _mark(False, str(e))
        return False
    if not data:
        return False
    if data != _file_cache["data"]:
        _write_file(data)
    _state["last_backup"] = time.time()
    return True


def start_backup_thread() -> None:
    def run():
        while True:
            time.sleep(max(30, settings.BACKUP_EVERY))
            try:
                backup_once()
            except Exception as e:
                print("[BACKUP] error:", e)
    threading.Thread(target=run, daemon=True, name="url-backup").start()
