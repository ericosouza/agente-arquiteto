import React, { useState } from 'react'
import {
  Layers,
  Edit2,
  Trash2,
  PlusCircle,
  Network,
  ShieldAlert,
  CheckCircle,
} from 'lucide-react'
import type {
  ArchitectureProposal,
  ComponentItem,
} from '../types/archimate'

interface AreaBProps {
  proposal: ArchitectureProposal | null
  onEditComponent: (component: ComponentItem) => void
  onDeleteComponent: (componentId: string) => void
  onAddComponent: () => void
  onEditIntegrations: () => void
}

export const AreaB_ArchitectureProposal: React.FC<AreaBProps> = ({
  proposal,
  onEditComponent,
  onDeleteComponent,
  onAddComponent,
  onEditIntegrations,
}) => {
  const [activeTab, setActiveTab] = useState<'components' | 'decisions' | 'nfr'>('components')

  if (!proposal) {
    return (
      <div className="card area-b-card empty-card">
        <div className="card-header">
          <div className="card-title">
            <Layers className="text-primary" size={18} />
            <span>Área B — Proposta Arquitetural</span>
          </div>
        </div>
        <div className="empty-state-content">
          <Layers size={40} className="text-muted" />
          <p className="empty-title">Aguardando descrição da necessidade</p>
          <p className="empty-subtitle">
            Digite sua necessidade na Área A para que o agente gere os componentes, tecnologias e integrações.
          </p>
        </div>
      </div>
    )
  }

  // Map integrations for each component for the table column
  const getIntegrationsSummary = (compId: string): string => {
    const outgoing = proposal.integrations.filter((i) => i.sourceComponentId === compId)
    const incoming = proposal.integrations.filter((i) => i.targetComponentId === compId)

    const parts: string[] = []
    if (outgoing.length > 0) {
      const targets = outgoing
        .map((i) => {
          const targetComp = proposal.components.find((c) => c.id === i.targetComponentId)
          return `→ ${targetComp?.name.split(' ')[0] || i.targetComponentId} (${i.protocol})`
        })
        .join(', ')
      parts.push(targets)
    }
    if (incoming.length > 0) {
      const sources = incoming
        .map((i) => {
          const srcComp = proposal.components.find((c) => c.id === i.sourceComponentId)
          return `← ${srcComp?.name.split(' ')[0] || i.sourceComponentId}`
        })
        .join(', ')
      parts.push(sources)
    }

    return parts.length > 0 ? parts.join(' | ') : 'Sem conexões diretas'
  }

  const getCategoryBadgeClass = (category: string) => {
    switch (category.toLowerCase()) {
      case 'frontend':
        return 'badge-frontend'
      case 'backend':
      case 'bff':
        return 'badge-backend'
      case 'database':
        return 'badge-database'
      case 'cache':
        return 'badge-cache'
      case 'messaging':
        return 'badge-messaging'
      default:
        return 'badge-default'
    }
  }

  return (
    <div className="card area-b-card">
      <div className="card-header">
        <div className="card-title">
          <Layers className="text-primary" size={18} />
          <span>Área B — Proposta Arquitetural (Etapa 4)</span>
          <span className="version-pill">v{proposal.version}</span>
        </div>

        <div className="tab-group">
          <button
            onClick={() => setActiveTab('components')}
            className={`tab-btn ${activeTab === 'components' ? 'active' : ''}`}
          >
            Componentes ({proposal.components.length})
          </button>
          <button
            onClick={() => setActiveTab('decisions')}
            className={`tab-btn ${activeTab === 'decisions' ? 'active' : ''}`}
          >
            Decisões ({proposal.decisions.length})
          </button>
          <button
            onClick={() => setActiveTab('nfr')}
            className={`tab-btn ${activeTab === 'nfr' ? 'active' : ''}`}
          >
            Requisitos Não Funcionais ({proposal.nonFunctionalRequirements.length})
          </button>
        </div>
      </div>

      <div className="proposal-summary-banner">
        <div>
          <h4 className="proposal-title">{proposal.title}</h4>
          {proposal.prerequisites && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', margin: '6px 0 8px' }}>
              {proposal.prerequisites.iniciativa && (
                <span className="badge-style">
                  <strong>Iniciativa:</strong> {proposal.prerequisites.iniciativa}
                </span>
              )}
              {proposal.prerequisites.sigla && (
                <span className="badge-style">
                  <strong>Sigla:</strong> {proposal.prerequisites.sigla.toUpperCase()}
                </span>
              )}
              {proposal.prerequisites.feature && (
                <span className="badge-style">
                  <strong>Feature:</strong> {proposal.prerequisites.feature}
                </span>
              )}
              {proposal.prerequisites.arqcor && (
                <span className="badge-style">
                  <strong>ARQCOR:</strong> {proposal.prerequisites.arqcor}
                </span>
              )}
            </div>
          )}
          <p className="proposal-style">
            <strong>Estilo Arquitetural:</strong>{' '}
            <span className="badge-style">{proposal.architecturalStyle}</span>
          </p>
          <p className="proposal-justification">{proposal.styleJustification}</p>
        </div>
      </div>

      {activeTab === 'components' && (
        <div className="tab-content">
          <div className="table-actions-bar">
            <span className="table-subtitle">
              Revise e edite os componentes antes de gerar o modelo ArchiMate definitivo:
            </span>
            <div className="action-buttons-row">
              <button onClick={onAddComponent} className="btn-secondary btn-sm">
                <PlusCircle size={14} />
                <span>Adicionar Componente</span>
              </button>
              <button onClick={onEditIntegrations} className="btn-secondary btn-sm">
                <Network size={14} />
                <span>Gerenciar Integrações ({proposal.integrations.length})</span>
              </button>
            </div>
          </div>

          <div className="table-responsive">
            <table className="architecture-table">
              <thead>
                <tr>
                  <th style={{ width: '80px' }}>ID</th>
                  <th style={{ width: '180px' }}>Componente</th>
                  <th>Responsabilidade</th>
                  <th style={{ width: '190px' }}>Tecnologia sugerida</th>
                  <th style={{ width: '220px' }}>Integrações</th>
                  <th style={{ width: '80px', textAlign: 'center' }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {proposal.components.map((comp) => (
                  <tr key={comp.id}>
                    <td>
                      <span className="component-id-badge">{comp.id}</span>
                    </td>
                    <td>
                      <div className="component-name-cell">
                        <strong>{comp.name}</strong>
                        <span className={`category-tag ${getCategoryBadgeClass(comp.category)}`}>
                          {comp.category}
                        </span>
                      </div>
                    </td>
                    <td>
                      <p className="cell-responsibility">{comp.responsibility}</p>
                    </td>
                    <td>
                      <div className="tech-cell">
                        <span className="tech-main">⚙ {comp.suggestedTechnology}</span>
                        {comp.alternativeTechnology && (
                          <span className="tech-alt" title="Opção alternativa">
                            Alt: {comp.alternativeTechnology}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="integrations-cell-text">
                        {getIntegrationsSummary(comp.id)}
                      </span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <button
                          onClick={() => onEditComponent(comp)}
                          className="btn-icon"
                          title="Editar componente"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          onClick={() => onDeleteComponent(comp.id)}
                          className="btn-icon btn-icon-danger"
                          title="Remover componente"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'decisions' && (
        <div className="tab-content">
          <div className="decisions-grid">
            {proposal.decisions.map((dec, idx) => (
              <div key={idx} className="decision-card">
                <div className="decision-header">
                  <CheckCircle size={16} className="text-success" />
                  <h5>{dec.decision}</h5>
                  <span className="badge-decision-status">{dec.status}</span>
                </div>
                <p className="decision-rationale">{dec.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'nfr' && (
        <div className="tab-content">
          <div className="nfr-grid">
            {proposal.nonFunctionalRequirements.map((nfr, idx) => (
              <div key={idx} className="nfr-card">
                <div className="nfr-header">
                  <ShieldAlert size={16} className="text-primary" />
                  <h5>{nfr.category}</h5>
                </div>
                <p className="nfr-description">{nfr.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
