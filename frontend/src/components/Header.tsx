import React from 'react'
import { Sparkles, Info, RotateCcw, Cpu, Coins } from 'lucide-react'
import type { SystemInfo, FinOpsSummary } from '../types/archimate'

interface HeaderProps {
  systemInfo: SystemInfo | null
  finOpsSummary?: FinOpsSummary | null
  onOpenConfig: () => void
  onOpenFinOps?: () => void
  onReset: () => void
}

export const Header: React.FC<HeaderProps> = ({
  systemInfo,
  finOpsSummary,
  onOpenConfig,
  onOpenFinOps,
  onReset,
}) => {
  const active = systemInfo?.activeProvider || 'builtin'
  const isCloud = active === 'gemini' || active === 'openai' || active === 'anthropic'
  const totalBrl = finOpsSummary?.totalCostBrl ?? 0
  const totalTokens = finOpsSummary?.totalTokens ?? 0

  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="brand-icon-wrapper">
          <Sparkles className="brand-icon" size={24} />
        </div>
        <div>
          <h1 className="brand-title">AI Software Architecture Designer</h1>
          <p className="brand-subtitle">
            Modelagem e Documentação de Arquitetura no Padrão{' '}
            <span className="brand-highlight">The Open Group ArchiMate® 3.2</span>
          </p>
        </div>
      </div>

      <div className="header-actions">
        {onOpenFinOps && (
          <button
            type="button"
            onClick={onOpenFinOps}
            className="finops-badge"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              color: '#38bdf8',
              padding: '6px 12px',
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 600,
            }}
            title="Clique para ver o painel de FinOps, custos em tempo real e tokens consumidos"
          >
            <Coins size={14} color="#f59e0b" />
            <span>
              FinOps: R$ {totalBrl.toFixed(4)} ({totalTokens.toLocaleString('pt-BR')} tok)
            </span>
          </button>
        )}

        <button
          onClick={onOpenConfig}
          className={`provider-badge ${isCloud ? 'provider-cloud' : 'provider-builtin'}`}
          title="Clique para ver detalhes do provedor de IA"
        >
          <Cpu size={15} />
          <span>Provedor: {active === 'builtin' ? 'Expert Engine (Offline)' : active.toUpperCase()}</span>
          <Info size={14} className="badge-info-icon" />
        </button>

        <button onClick={onReset} className="btn-secondary btn-sm" title="Reiniciar projeto">
          <RotateCcw size={15} />
          <span>Novo Projeto</span>
        </button>
      </div>
    </header>
  )
}
