#!/bin/bash
set -euo pipefail
# Loads the Parquet seeds into the tables created by 01_schema.sql.

clickhouse client --query "INSERT INTO raw.\`opportunities\` FORMAT Parquet" < /seed/raw/opportunities.parquet
clickhouse client --query "INSERT INTO raw.\`actions\` FORMAT Parquet" < /seed/raw/actions.parquet
clickhouse client --query "INSERT INTO raw.\`companies\` FORMAT Parquet" < /seed/raw/companies.parquet
clickhouse client --query "INSERT INTO raw.\`contacts\` FORMAT Parquet" < /seed/raw/contacts.parquet
clickhouse client --query "INSERT INTO raw.\`ressources\` FORMAT Parquet" < /seed/raw/ressources.parquet
clickhouse client --query "INSERT INTO raw.\`businessunits\` FORMAT Parquet" < /seed/raw/businessunits.parquet
clickhouse client --query "INSERT INTO raw.\`agencies\` FORMAT Parquet" < /seed/raw/agencies.parquet
clickhouse client --query "INSERT INTO raw.\`poles\` FORMAT Parquet" < /seed/raw/poles.parquet
clickhouse client --query "INSERT INTO raw.\`dictionaries\` FORMAT Parquet" < /seed/raw/dictionaries.parquet
clickhouse client --query "INSERT INTO raw.\`projects\` FORMAT Parquet" < /seed/raw/projects.parquet
clickhouse client --query "INSERT INTO raw.\`deliveries\` FORMAT Parquet" < /seed/raw/deliveries.parquet
clickhouse client --query "INSERT INTO hubspot.\`contacts\` FORMAT Parquet" < /seed/hubspot/contacts.parquet
clickhouse client --query "INSERT INTO hubspot.\`deals\` FORMAT Parquet" < /seed/hubspot/deals.parquet
clickhouse client --query "INSERT INTO ref.\`sales_targets\` FORMAT Parquet" < /seed/ref/sales_targets.parquet
clickhouse client --query "INSERT INTO ref.\`stage_probabilities\` FORMAT Parquet" < /seed/ref/stage_probabilities.parquet
