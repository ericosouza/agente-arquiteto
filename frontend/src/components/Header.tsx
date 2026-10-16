import React from 'react'
import { Sparkles, Info, RotateCcw, Cpu } from 'lucide-react'
import type { SystemInfo } from '../types/archimate'

interface HeaderProps {
  systemInfo: SystemInfo | null
  onOpenConfig: () => void
  onReset: () => void
}

export const Header: React.FC<HeaderProps> = ({
  systemInfo,
  onOpenConfig,
  onReset,
}) => {
  const active = systemInfo?.activeProvider || 'builtin'
  const isCloud = active === 'gemini' || active === 'openai' || active === 'anthropic'

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
