"""Хранилище ссылок.

Записи ссылок (адрес, даты, автор) хранятся через ashredis.
Всё, что ashredis не умеет атомарно, остаётся на обычном redis-клиенте:
  * Index   — множество кодов; SADD возвращает 1 только одному из параллельных запросов,
              поэтому два человека не получат один и тот же короткий код;
  * Clicks  — счётчики переходов (HINCRBY);
  * Owners  — какие ссылки создал владелец;
  * Stats   — общая статистика.
Публичные функции этого модуля остались прежними, routes/* менять не нужно.
"""
import asyncio
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

import redis
from ashredis import MISSING, RecordBase, RedisObject, RedisParams

import settings

ROOT = "shorten_links_database:"
PREV_ROOT = "MuhamedLabs:URL:"
LINKS = ROOT + "Links:"          # старые хеши (до ashredis), нужны только для миграции
OWNERS = ROOT + "Owners:"
STATS = ROOT + "Stats"
INDEX = ROOT + "Index"
CLICKS = ROOT + "Clicks"
MIGRATED = ROOT + "AshMigrated"
LEGACY = "Url:"
LEGACY_IDX = "UrlIdx:"

FIELDS = ("short_id", "original_url", "created_at", "updated_at", "created_by", "created_ip")


@dataclass
class LinkRecord(RecordBase):
    short_id: Optional[str] = MISSING
    original_url: Optional[str] = MISSING
    created_at: Optional[str] = MISSING
    updated_at: Optional[str] = MISSING
    created_by: Optional[str] = MISSING
    created_ip: Optional[str] = MISSING


_lock = threading.Lock()
_client: Optional[redis.Redis] = None
_mem: Dict[str, str] = {}
_file_cache = {"mtime": 0.0, "data": {}}
_state = {"redis_ok": None, "last_error": "", "last_backup": 0.0}

# ---- ashredis работает в asyncio, Flask — синхронный: держим один фоновый event loop ----
_loop: Optional[asyncio.AbstractEventLoop] = None
_loop_lock = threading.Lock()


def _get_loop() -> asyncio.AbstractEventLoop:
    global _loop
    with _loop_lock:
        if _loop is None:
            loop = asyncio.new_event_loop()
            threading.Thread(target=loop.run_forever, daemon=True, name="ashredis-loop").start()
            _loop = loop
        return _loop


def _run(coro, timeout: float = 6.0):
    return asyncio.run_coroutine_threadsafe(coro, _get_loop()).result(timeout)


def _params() -> RedisParams:
    return RedisParams(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                       password=settings.REDIS_PASSWORD or "", db=settings.REDIS_DB)


def _val(v):
    return None if v is MISSING or v is None else v


async def _a_save(code: str, rec: dict) -> None:
    async with RedisObject(redis_params=_params()) as ro:
        await ro.save(record=LinkRecord(**{k: rec.get(k) for k in FIELDS}), key=code)


async def _a_load(code: str) -> Optional[dict]:
    async with RedisObject(redis_params=_params()) as ro:
        try:
            r = await ro.load(record_type=LinkRecord, key=code)
        except (KeyError, LookupError):
            return None
    if r is None:
        return None
    out = {k: _val(getattr(r, k, None)) for k in FIELDS}
    return out if out["original_url"] else None


async def _a_delete(code: str) -> None:
    async with RedisObject(redis_params=_params()) as ro:
        await ro.delete(record_type=LinkRecord, key=code)


def _load(code: str) -> Optional[dict]:
    return _run(_a_load(code))


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


def get_link(code: str) -> Optional[dict]:
    rec = _load(code)
    return dict(rec, id=code, clicks=client().hget(CLICKS, code) or "0") if rec else None


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
        _run(_a_save(code, rec))
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
    _run(_a_save(code, rec))
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


def migrate_to_ashredis() -> int:
    """Разово переносит старые хеши в ashredis. Старые ключи не удаляются.
    Перед переносом делает резервную копию в DATA_FILE."""
    r = client()
    if r.get(MIGRATED):
        return 0
    old = _raw_old_hashes()
    if not old:
        r.set(MIGRATED, _now())
        return 0
    _write_file(old)
    n = 0
    for code, v in old.items():
        rec = {k: v.get(k) for k in FIELDS}
        rec["short_id"] = rec["short_id"] or _short(code)
        _run(_a_save(code, rec))
        r.sadd(INDEX, code)
        if v.get("clicks"):
            r.hset(CLICKS, code, v["clicks"])
        n += 1
    r.set(MIGRATED, _now())
    print(f"[MIGRATE] перенесено в ashredis: {n}")
    return n


def seed_from_file() -> int:
    try:
        if count():
            return 0
        n = 0
        for code, rec in _read_file().items():
            if create(code, rec["original_url"], rec.get("created_by", "legacy"), rec.get("created_ip", ""),
                      rec.get("created_at", ""), rec.get("updated_at", "")):
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
