"""Integration smoke check. Never print credentials, tokens or connection URIs."""
import os

import requests
from sqlalchemy import text
from superset.app import create_app
from superset.extensions import db

base = "http://localhost:8088"
assert requests.get(base + "/health", timeout=10).status_code == 200
assert requests.get(base + "/login/", timeout=10).status_code == 200
response = requests.post(
    base + "/api/v1/security/login",
    json={
        "username": os.environ["SUPERSET_ADMIN_USERNAME"],
        "password": os.environ["SUPERSET_ADMIN_PASSWORD"],
        "provider": "db",
        "refresh": False,
    },
    timeout=30,
)
assert response.status_code == 200, f"Login HTTP {response.status_code}"
token = response.json()["access_token"]
response = requests.get(
    base + "/api/v1/database/",
    headers={"Authorization": "Bearer " + token},
    timeout=30,
)
assert response.status_code == 200, f"Database API HTTP {response.status_code}"
assert any(item["database_name"] == "ClickHouse - case" for item in response.json()["result"])
print("OK: HTTP health, login, authenticated API and configured connection")

app = create_app()
with app.app_context():
    from superset.models.core import Database

    database = db.session.query(Database).filter_by(database_name="ClickHouse - case").one()
    with database.get_sqla_engine() as engine:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar() == 1
            assert connection.execute(text("SELECT getSetting('readonly')")).scalar() == 1
            count = connection.execute(text(
                "SELECT count() FROM system.tables WHERE database IN ('raw', 'hubspot', 'ref')"
            )).scalar()
            assert count == 15, f"Expected 15 source tables, got {count}"
            connection.execute(text("SELECT count() FROM ref.stage_probabilities")).scalar()
    assert db.session.query(Database).filter_by(database_name="ClickHouse - case").count() == 1
print("OK: Superset SQLAlchemy connection, SELECT, readonly=1 and 15 source tables")
