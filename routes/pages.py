import json
import os
from datetime import date

from flask import Blueprint, Response, abort, make_response, redirect, render_template, request, send_from_directory

import settings
from storage import redis_store as store
from utils.helpers import is_valid_code, normalize_url

pages_bp = Blueprint("pages", __name__)


_BOTS = ("bot", "crawl", "spider", "slurp", "preview", "facebookexternalhit", "telegram", "whatsapp", "discord", "curl", "wget")


def _is_bot() -> bool:
    """Боты и предпросмотр в мессенджерах не должны накручивать счётчик переходов."""
    ua = (request.headers.get("User-Agent") or "").lower()
    return request.method == "HEAD" or any(b in ua for b in _BOTS)


def _nocache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@pages_bp.get("/")
def home():
    st = store.stats()
    return render_template("home.html", count=store.count() or 0, visits=st["visits"], top=st["top"],
                           delay=settings.REDIRECT_DELAY)


def _find_file(name, mimetype, *subdirs):
    """Ищем файл по очереди в указанных папках (относительно проекта) — берём первую, где он есть."""
    for sub in subdirs:
        d = os.path.join(settings.BASE_DIR, sub)
        if os.path.isfile(os.path.join(d, name)):
            resp = send_from_directory(d, name, mimetype=mimetype)
            resp.headers["Cache-Control"] = "public, max-age=3600"
            return resp
    return None


@pages_bp.get("/robots.txt")
def robots():
    """Файл лежит в корне проекта: robots.txt"""
    return _find_file("robots.txt", "text/plain", "", "static") or abort(404)


_MANIFEST_FALLBACK = {
    "id": "/", "name": "Мухамед Ads · Сокращатель ссылок", "short_name": "Сокращатель", "lang": "ru",
    "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#222222", "theme_color": "#222222",
    "icons": [{"src": "/static/icons/pwa-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
              {"src": "/static/icons/pwa-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "/static/icons/pwa-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
}


@pages_bp.get("/manifest.webmanifest")
def manifest():
    """Манифест PWA: файл static/js/manifest.webmanifest. Если файла нет — отдаём встроенный."""
    resp = _find_file("manifest.webmanifest", "application/manifest+json", "static/js", "static", "")
    if resp is None:
        resp = Response(json.dumps(_MANIFEST_FALLBACK, ensure_ascii=False), mimetype="application/manifest+json")
        resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


@pages_bp.get("/sw.js")
def service_worker():
    resp = send_from_directory(os.path.join(settings.BASE_DIR, "static", "js"), "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@pages_bp.get("/sitemap.xml")
def sitemap():
    """Файл лежит в корне проекта: sitemap.xml (дату lastmod меняйте руками при обновлении сайта)"""
    return _find_file("sitemap.xml", "application/xml", "", "static") or abort(404)


@pages_bp.get("/go/<code>")
def go_now(code):
    if not is_valid_code(code):
        abort(404)
    url = normalize_url(store.get_url(code) or "")
    if not url:
        abort(404)
    return _nocache(redirect(url, code=302))


@pages_bp.get("/<code>")
def wait_page(code):
    if not is_valid_code(code):
        abort(404)
    if not store.get_url(code):
        abort(404)
    if not _is_bot():
        store.visit(code)
    resp = make_response(render_template("go.html", code=code, delay=settings.REDIRECT_DELAY))
    return _nocache(resp)
