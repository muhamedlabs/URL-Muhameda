from flask import Blueprint, Response, abort, make_response, redirect, render_template, request

import settings
from storage import redis_store as store
from utils.helpers import is_valid_code, normalize_url

pages_bp = Blueprint("pages", __name__)


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
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /go/\n\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@pages_bp.get("/sitemap.xml")
def sitemap():
    base = settings.PUBLIC_BASE_URL or request.host_url.rstrip("/")
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'  <url><loc>{base}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
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
    store.visit(code)
    resp = make_response(render_template("go.html", code=code, delay=settings.REDIRECT_DELAY))
    return _nocache(resp)
