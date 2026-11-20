import json
import os

from flask import Flask, redirect, render_template, request

import settings
from routes.api import api_bp
from routes.pages import pages_bp
from storage import redis_store as store


PORT = 5001

app = Flask(__name__, template_folder=os.path.join(settings.BASE_DIR, "templates"),
            static_folder=os.path.join(settings.BASE_DIR, "static"), static_url_path="/static")
app.register_blueprint(api_bp)
app.register_blueprint(pages_bp)


def _backgrounds() -> list:
    d = os.path.join(settings.BASE_DIR, "static", "images", "background")
    try:
        names = [n for n in os.listdir(d) if n.lower().endswith((".webp", ".jpg", ".jpeg", ".png"))]
    except OSError:
        return []
    key = lambda n: (0, int(os.path.splitext(n)[0]), n) if os.path.splitext(n)[0].isdigit() else (1, 0, n)
    return ["/static/images/background/" + n for n in sorted(names, key=key)]


def _site_url() -> str:
    return settings.PUBLIC_BASE_URL or request.host_url.rstrip("/")


@app.context_processor
def seo():
    base = _site_url()
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": f"{base}/#org", "name": "Мухамед Ads",
             "alternateName": ["Muhamed Ads", "Мухамед Ads"], "url": "https://muhamedlabs.pro",
             "logo": f"{base}/static/logo.webp",
             "description": "Креативная и технологическая сеть"},
            {"@type": "WebSite", "@id": f"{base}/#site", "url": f"{base}/", "name": "Мухамед Ads · сокращатель ссылок",
             "alternateName": "Сокращатель ссылок Мухамед Ads", "inLanguage": ["ru", "uk", "en"],
             "publisher": {"@id": f"{base}/#org"}},
            {"@type": "WebApplication", "@id": f"{base}/#app", "name": "Умный сокращатель ссылок",
             "url": f"{base}/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
             "browserRequirements": "Requires JavaScript", "inLanguage": ["ru", "uk", "en"],
             "description": "Предоставляем удобный инструмент для создания коротких ссылок, упрощая обмен адресами и делая переход к нужным ресурсам быстрее и комфортнее.",
             "image": f"{base}/static/images/twitter/SEO_4.webp",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
             "featureList": ["Сокращение длинных ссылок", "Автокопирование результата", "Поддержка http и https",
                             "Редактирование адреса автором", "Интерфейс на русском, украинском и английском"],
             "publisher": {"@id": f"{base}/#org"}},
        ],
    }

    dumped = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    bgs = _backgrounds()
    return {"site_url": base, "jsonld": dumped, "bg_json": json.dumps(bgs), "bg_first": bgs[0] if bgs else ""}


@app.after_request
def secure(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.path.startswith("/static/") and resp.status_code == 200:
        resp.headers["Cache-Control"] = "public, max-age=2592000" if request.args.get("v") else "public, max-age=3600"
    elif request.path.startswith("/api/") or resp.mimetype == "text/html":

        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.route("/favicon.ico")
def favicon():
    return redirect("/static/logo.webp", code=301)


@app.errorhandler(404)
def not_found(_e):
    return render_template("go.html", code="", delay=0, missing=True), 404


def init():
    try:
        store.client().ping()
        print(f"[REDIS] OK {settings.REDIS_HOST}:{settings.REDIS_PORT} db={settings.REDIS_DB}")
        store.migrate_legacy()
        store.sync_storage()
        store.backup_once()
    except Exception as e:
        print(f"[REDIS] Сейчас недоступен ({e}). Работаем из резервной копии, повторим при первом запросе.")
    store.start_backup_thread()


_inited = False


def ensure_init():
    """Запуск и через `python main.py`, и через gunicorn/uwsgi (раньше init() работал только при прямом запуске)."""
    global _inited
    if not _inited:
        _inited = True
        init()


ensure_init()

if __name__ == "__main__":
    print(f"[FLASK] http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
