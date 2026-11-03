# ==============================================================================
# Script de Parada - Agente Arquiteto de Software AI
# Encerra os servidores Backend e Frontend de forma limpa.
# ==============================================================================

Write-Host ""
Write-Host "🛑 Encerrando servidores do Agente Arquiteto..." -ForegroundColor Yellow

$ports = 8000, 5173
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            try {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                Write-Host "✓ Processo $procId (porta $p) finalizado com sucesso." -ForegroundColor Green
            } catch {}
        }
    } else {
        Write-Host "ℹ️  Nenhum processo ativo na porta $p." -ForegroundColor Gray
    }
}

Write-Host "✅ Todos os servidores foram encerrados com sucesso." -ForegroundColor Green
Write-Host ""
