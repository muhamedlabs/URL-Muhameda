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
INDEX = ROOT + "Index"
CLICKS = ROOT + "Clicks"
LEGACY = "Url:"
LEGACY_IDX = "UrlIdx:"

FIELDS = ("short_id", "original_url", "created_at", "updated_at", "created_by", "created_ip")


_lock = threading.Lock()
_client: Optional[redis.Redis] = None
_mem: Dict[str, str] = {}
_file_cache = {"mtime": 0.0, "data": {}}
_state = {"redis_ok": None, "last_error": "", "last_backup": 0.0}

def _load(code: str) -> Optional[dict]:
    h = client().hgetall(LINKS + code)
    if not h or not h.get("original_url"):
        return None
    return {k: (h.get(k) or None) for k in FIELDS}


def _save(code: str, rec: dict) -> None:
    mapping = {"id": code}
    mapping.update({k: (rec.get(k) or "") for k in FIELDS})
    client().hset(LINKS + code, mapping=mapping)


def client() -> redis.Redis:
    global _client
    with _lock:
        if _client is None:
            _client = redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB, decode_responses=True,
                socket_connect_timeout=3, socket_timeout=3, health_check_interval=30,
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
        if r.sismember(INDEX, code):
            n = r.hincrby(CLICKS, code, 1)
            r.hincrby(STATS, "visits", 1)
            if n > int(r.hget(STATS, "top") or 0):
                r.hset(STATS, "top", n)
    except redis.RedisError as e:
        _mark(False, str(e))


def stats() -> dict:
    try:
        h = client().hgetall(STATS)
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
        if not client().sismember(INDEX, code):
            _mark(True)
            _mem.pop(code, None)
            return None
        rec = _load(code)
        _mark(True)
        if rec:
            _mem[code] = rec["original_url"]
            return rec["original_url"]
        _mem.pop(code, None)
        return None
    except Exception as e:
        _mark(False, str(e))
        print("[REDIS] get error:", e)
    return _mem.get(code) or (_read_file().get(code) or {}).get("original_url")


def scan_all() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for code in sorted(client().smembers(INDEX)):
        rec = _load(code)
        if rec:
            out[code] = rec
    return out


def count() -> Optional[int]:
    try:
        n = client().scard(INDEX)
        _mark(True)
        return n
    except redis.RedisError as e:
        _mark(False, str(e))
        return None


def create(code: str, url: str, owner: str = "", ip: str = "", created_at: str = "", updated_at: str = "") -> bool:
    r = client()
    if not r.sadd(INDEX, code):          # код уже занят
        return False
    now = _now()
    rec = {"short_id": _short(code), "original_url": url,
           "created_at": created_at or now, "updated_at": updated_at or created_at or now,
           "created_by": owner, "created_ip": ip}
    try:
        _save(code, rec)
    except Exception:
        r.srem(INDEX, code)              # не оставляем «пустой» код в индексе
        raise
    if owner and owner != "legacy":
        r.sadd(OWNERS + owner, code)
    r.hincrby(STATS, "created:" + _today(), 1)
    _mem[code] = url
    return True


def update(code: str, url: str, owner: str) -> str:
    rec = _load(code)
    if not rec:
        return "missing"
    if not owner or rec.get("created_by") != owner:
        return "forbidden"
    rec.update(original_url=url, updated_at=_now())
    _save(code, rec)
    _mem[code] = url
    return "ok"


def by_owner(owner: str) -> list:
    out = []
    for c in sorted(client().smembers(OWNERS + owner)):
        rec = _load(c)
        if rec:
            out.append(dict(rec, id=c))
    return out


def _raw_old_hashes() -> Dict[str, dict]:
    """Ссылки старого формата (обычные хеши Redis) — только для разовой миграции."""
    r = client()
    out: Dict[str, dict] = {}
    for k in r.scan_iter(match=LINKS + "*", count=500):
        if r.type(k) != "hash":
            continue
        v = r.hgetall(k)
        if v.get("original_url"):
            out[k[len(LINKS):]] = v
    return out


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
        old = _raw_old_hashes()
        if old:
            _write_file(old)
        for k in keys:
            code = k[len(LEGACY):]
            if r.hget(LINKS + code, "original_url"):
                r.delete(k)
    for k in r.scan_iter(match=LEGACY_IDX + "*", count=500):
        r.delete(k)
    return moved


def sync_storage() -> int:
    r = client()
    n = 0
    for code, v in _raw_old_hashes().items():
        r.sadd(INDEX, code)
        if v.get("clicks") and not r.hexists(CLICKS, code):
            r.hset(CLICKS, code, v["clicks"])
    for code, rec in _read_file().items():
        if r.exists(LINKS + code):
            continue
        now = _now()
        _save(code, {"short_id": rec.get("short_id") or _short(code), "original_url": rec["original_url"],
                     "created_at": rec.get("created_at") or now, "updated_at": rec.get("updated_at") or rec.get("created_at") or now,
                     "created_by": rec.get("created_by") or "legacy", "created_ip": rec.get("created_ip") or ""})
        r.sadd(INDEX, code)
        n += 1
    if n:
        print(f"[SYNC] восстановлено из файла: {n}")
    return n


def backup_once() -> bool:
    try:
        data = scan_all()
        _mark(True)
    except Exception as e:
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
