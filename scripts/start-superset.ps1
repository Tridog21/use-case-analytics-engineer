[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    docker info --format '{{.ServerVersion}}' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Demarrer Docker Desktop et attendre que son moteur soit pret.' }
    if (-not (Test-Path -LiteralPath '.env.superset')) {
        function New-LocalSecret {
            $bytes = New-Object byte[] 32
            $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
            try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
            return ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
        }
        $settings = @(
            "SUPERSET_SECRET_KEY=$(New-LocalSecret)"
            "POSTGRES_PASSWORD=$(New-LocalSecret)"
            'SUPERSET_ADMIN_USERNAME=admin'
            "SUPERSET_ADMIN_PASSWORD=$(New-LocalSecret)"
            "CLICKHOUSE_SUPERSET_PASSWORD=$(New-LocalSecret)"
        )
        [IO.File]::WriteAllLines((Join-Path $projectRoot '.env.superset'), $settings, (New-Object Text.UTF8Encoding $false))
    }
    docker compose --env-file .env.superset -f docker-compose.yml -f docker-compose.superset.yml up -d --build --wait --wait-timeout 600
    if ($LASTEXITCODE -ne 0) { throw 'Echec du demarrage. Voir docs/superset.md pour les logs.' }
    Write-Host 'Superset pret : http://localhost:8088'
    Write-Host 'Identifiant : admin. Mot de passe : SUPERSET_ADMIN_PASSWORD dans .env.superset (fichier local prive).'
} finally { Pop-Location }
