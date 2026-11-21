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


def _static_file(name, mimetype):
    resp = send_from_directory(os.path.join(settings.BASE_DIR, "static"), name, mimetype=mimetype)
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


@pages_bp.get("/robots.txt")
def robots():
    """Файл лежит отдельно: static/robots.txt"""
    return _static_file("robots.txt", "text/plain")


@pages_bp.get("/manifest.webmanifest")
def manifest():
    """Манифест PWA лежит отдельным файлом: static/manifest.webmanifest (от него Chrome предлагает установку)."""
    resp = send_from_directory(os.path.join(settings.BASE_DIR, "static"), "manifest.webmanifest",
                               mimetype="application/manifest+json")
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


@pages_bp.get("/sw.js")
def service_worker():
    resp = send_from_directory(os.path.join(settings.BASE_DIR, "static", "js"), "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@pages_bp.get("/sitemap.xml")
def sitemap():
    """Файл лежит отдельно: static/sitemap.xml (дату lastmod меняйте руками при обновлении сайта)"""
    return _static_file("sitemap.xml", "application/xml")


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
