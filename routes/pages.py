import json
from datetime import date

from flask import Blueprint, Response, abort, make_response, redirect, render_template, request

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


@pages_bp.get("/robots.txt")
def robots():
    base = settings.PUBLIC_BASE_URL or request.host_url.rstrip("/")
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /go/\nDisallow: /*?boot\n\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@pages_bp.get("/manifest.webmanifest")
def manifest():
    data = {"name": "Мухамед Ads · сокращатель ссылок", "short_name": "Сокращатель", "start_url": "/",
            "display": "standalone", "background_color": "#222222", "theme_color": "#222222", "lang": "ru",
            "icons": [{"src": "/static/logo.webp", "sizes": "900x900", "type": "image/webp"}]}
    return Response(json.dumps(data, ensure_ascii=False), mimetype="application/manifest+json")


@pages_bp.get("/sitemap.xml")
def sitemap():
    base = settings.PUBLIC_BASE_URL or request.host_url.rstrip("/")
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'  <url><loc>{base}/</loc><lastmod>{date.today().isoformat()}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
            '</urlset>\n')
    return Response(body, mimetype="application/xml")


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
