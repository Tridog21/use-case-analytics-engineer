"""Idempotent local bootstrap: read-only warehouse account and Superset connection."""
import os
from urllib.parse import quote_plus

import clickhouse_connect


def sql_literal(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


client = clickhouse_connect.get_client(host="clickhouse", port=8123, username="default")
client.command("CREATE DATABASE IF NOT EXISTS analytics")
password = os.environ["CLICKHOUSE_SUPERSET_PASSWORD"]
client.command(
    "CREATE USER IF NOT EXISTS superset_reader IDENTIFIED WITH sha256_password BY "
    + sql_literal(password)
)
for schema in ("analytics", "raw", "hubspot", "ref", "dtr_sales"):
    client.command(f"GRANT SELECT ON {schema}.* TO superset_reader")
client.command("GRANT SELECT ON dwh_common.int_publication TO superset_reader")
client.command("ALTER USER superset_reader SETTINGS readonly = 1, max_threads = 2")
client.close()

from superset.app import create_app
from superset.extensions import db

app = create_app()
with app.app_context():
    from superset.models.core import Database

    sm = app.appbuilder.sm
    username = os.environ["SUPERSET_ADMIN_USERNAME"]
    if not sm.find_user(username=username):
        user = sm.add_user(
            username=username,
            first_name="Orest",
            last_name="Case",
            email="admin@example.invalid",
            role=sm.find_role("Admin"),
            password=os.environ["SUPERSET_ADMIN_PASSWORD"],
        )
        if not user:
            raise RuntimeError("Could not create Superset administrator")
    database = db.session.query(Database).filter_by(database_name="ClickHouse - case").one_or_none()
    if database is None:
        database = Database(database_name="ClickHouse - case")
        db.session.add(database)
    database.sqlalchemy_uri = (
        "clickhousedb://superset_reader:"
        + quote_plus(password)
        + "@clickhouse:8123/analytics"
    )
    database.expose_in_sqllab = True
    database.allow_dml = False
    database.allow_ctas = False
    database.allow_cvas = False
    db.session.commit()
print("Bootstrap complete: administrator and read-only ClickHouse connection ready.")
