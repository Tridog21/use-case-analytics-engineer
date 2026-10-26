[CmdletBinding()]
param([switch]$IncludeClickHouse)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    $services = @('superset', 'superset-db')
    if ($IncludeClickHouse) { $services += 'clickhouse' }
    docker compose --env-file .env.superset -f docker-compose.yml -f docker-compose.superset.yml stop @services
    if ($LASTEXITCODE -ne 0) { throw 'Echec de l’arret des services.' }
} finally { Pop-Location }
