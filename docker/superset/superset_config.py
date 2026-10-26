"""Local case environment. Credentials are generated once in .env.superset."""
import os
from urllib.parse import quote_plus

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://superset:"
    + quote_plus(os.environ["POSTGRES_PASSWORD"])
    + "@superset-db:5432/superset"
)
WTF_CSRF_ENABLED = True
TALISMAN_ENABLED = False  # Local HTTP; no public deployment configured.
SQLLAB_TIMEOUT = 60
SQLLAB_ASYNC_TIME_LIMIT_SEC = 60
ROW_LIMIT = 10000
BABEL_DEFAULT_LOCALE = "fr"
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    # Presentation classes only: scripts, event handlers and inline styles
    # remain subject to the default HTML sanitizer.
    "attributes": {tag: ["className"] for tag in ("div", "span", "table", "th", "td", "b")}
}
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_CROSS_FILTERS": True,
}
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "fr": {"flag": "fr", "name": "Français"},
}
