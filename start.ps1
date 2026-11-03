# ==============================================================================
# Script de Inicialização Rápida - Agente Arquiteto de Software AI
# Executa o Backend FastAPI e o Frontend React/Vite com um único comando.
# ==============================================================================

$RootPath = $PSScriptRoot
if (-not $RootPath) { $RootPath = (Get-Location).Path }

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  🚀 Inicializando Agente Arquiteto de Software AI         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifica e prepara o arquivo .env na raiz
$envPath = Join-Path $RootPath ".env"
$envExample = Join-Path $RootPath ".env.example"
if (-not (Test-Path $envPath)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envPath
        Write-Host "ℹ️  Arquivo .env criado a partir de .env.example." -ForegroundColor Yellow
    }
}

# 2. Inicia o Backend FastAPI (porta 8000)
$backendPortCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $backendPortCheck) {
    Write-Host "▶️  Iniciando Backend FastAPI (Porta 8000)..." -ForegroundColor Green
    $backendDir = Join-Path $RootPath "backend"
    $pythonExe = Join-Path $backendDir "venv\Scripts\uvicorn.exe"
    
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "uvicorn"
    }

    Start-Process -FilePath $pythonExe -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $backendDir -WindowStyle Hidden
} else {
    Write-Host "✓  Backend FastAPI já está ativo na porta 8000." -ForegroundColor DarkGreen
}

# 3. Inicia o Frontend Vite (porta 5173)
$frontendPortCheck = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if (-not $frontendPortCheck) {
    Write-Host "▶️  Iniciando Frontend Vite (Porta 5173)..." -ForegroundColor Green
    $frontendDir = Join-Path $RootPath "frontend"
    
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -WorkingDirectory $frontendDir -WindowStyle Hidden
} else {
    Write-Host "✓  Frontend Vite já está ativo na porta 5173." -ForegroundColor DarkGreen
}

# Aguarda 2 segundos para estabilização dos serviços
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ✅ Sistema Pronto e Online para Uso!                     " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  👉 Frontend (Interface Web):  http://localhost:5173" -ForegroundColor Cyan
Write-Host "  👉 Backend API (Swagger):     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  👉 Backend Status:            http://localhost:8000/api/info" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# Abre automaticamente o navegador padrão no Frontend
Start-Process "http://localhost:5173"
