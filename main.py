import json
import os

from flask import Flask, render_template, request

import settings
from routes.api import api_bp
from routes.pages import pages_bp
from storage import redis_store as store


PORT = 5001

app = Flask(__name__, template_folder=os.path.join(settings.BASE_DIR, "templates"),
            static_folder=os.path.join(settings.BASE_DIR, "static"), static_url_path="/static")
app.register_blueprint(api_bp)
app.register_blueprint(pages_bp)


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
            {"@type": "WebSite", "@id": f"{base}/#site", "url": f"{base}/", "name": "Мухамед Ads — сокращатель ссылок",
             "alternateName": "Сокращатель ссылок Мухамед Ads", "inLanguage": ["ru", "uk", "en"],
             "publisher": {"@id": f"{base}/#org"}},
            {"@type": "WebApplication", "@id": f"{base}/#app", "name": "Сокращатель ссылок",
             "url": f"{base}/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
             "browserRequirements": "Requires JavaScript", "inLanguage": ["ru", "uk", "en"],
             "description": "Один аккуратный адрес вместо длинной ссылки: вставьте, нажмите и делитесь с кем угодно.",
             "image": f"{base}/static/images/SEO_1.webp",
             "publisher": {"@id": f"{base}/#org"}},
        ],
    }

    dumped = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return {"site_url": base, "jsonld": dumped}


@app.after_request
def secure(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
    if resp.mimetype == "text/html":

        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.errorhandler(404)
def not_found(_e):
    return render_template("go.html", code="", delay=0, missing=True), 404


def init():
    try:
        store.client().ping()
        print(f"[REDIS] OK {settings.REDIS_HOST}:{settings.REDIS_PORT} db={settings.REDIS_DB}")
        store.migrate_legacy()
        store.migrate_to_ashredis()
        store.seed_from_file()
        store.backup_once()
    except Exception as e:
        print(f"[REDIS] Сейчас недоступен ({e}). Работаем из резервной копии, повторим при первом запросе.")
    store.start_backup_thread()


if __name__ == "__main__":
    init()
    print(f"[FLASK] http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
