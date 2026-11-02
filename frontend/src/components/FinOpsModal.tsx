import React from 'react'
import {
  X,
  Coins,
  Cpu,
  ExternalLink,
  RotateCcw,
  Clock,
} from 'lucide-react'
import type { FinOpsSummary } from '../types/archimate'

interface FinOpsModalProps {
  summary: FinOpsSummary | null
  isOpen: boolean
  onClose: () => void
  onReset: () => void
}

export const FinOpsModal: React.FC<FinOpsModalProps> = ({
  summary,
  isOpen,
  onClose,
  onReset,
}) => {
  if (!isOpen) return null

  const spans = summary?.spans || []
  const totalBrl = summary?.totalCostBrl ?? 0
  const totalUsd = summary?.totalCostUsd ?? 0
  const totalTokens = summary?.totalTokens ?? 0
  const totalCalls = summary?.totalCalls ?? 0

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1100 }}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '850px', width: '95%' }}
      >
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Coins size={20} color="#f59e0b" />
            <h3 style={{ margin: 0 }}>Observabilidade de Custos & FinOps</h3>
            <span
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '12px',
                backgroundColor: '#1e3a8a',
                color: '#93c5fd',
              }}
            >
              LangGraph & Phoenix OTel
            </span>
          </div>
          <button type="button" className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
          {/* Top KPI Cards */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '12px',
              marginBottom: '20px',
            }}
          >
            <div
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
              }}
            >
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>Custo Total (BRL)</span>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#10b981', marginTop: '4px' }}>
                R$ {totalBrl.toFixed(4)}
              </div>
              <span style={{ fontSize: '10px', color: '#64748b' }}>Câmbio: R$ 5,80/USD</span>
            </div>

            <div
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
              }}
            >
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>Custo Total (USD)</span>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#f59e0b', marginTop: '4px' }}>
                ${totalUsd.toFixed(5)}
              </div>
              <span style={{ fontSize: '10px', color: '#64748b' }}>Preço por 1M tokens</span>
            </div>

            <div
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
              }}
            >
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>Tokens Consumidos</span>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>
                {totalTokens.toLocaleString('pt-BR')}
              </div>
              <span style={{ fontSize: '10px', color: '#64748b' }}>
                In: {summary?.totalPromptTokens ?? 0} | Out: {summary?.totalCompletionTokens ?? 0}
              </span>
            </div>

            <div
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
              }}
            >
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>Chamadas de LLM</span>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#a855f7', marginTop: '4px' }}>
                {totalCalls}
              </div>
              <span style={{ fontSize: '10px', color: '#64748b' }}>Provedor: {summary?.activeProvider || 'builtin'}</span>
            </div>
          </div>

          {/* External Phoenix Docker Integration Banner */}
          <div
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              backgroundColor: '#0f172a',
              border: '1px solid #1e293b',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '10px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Cpu size={16} color="#60a5fa" />
                <span style={{ fontWeight: 600, fontSize: '13px', color: '#f8fafc' }}>
                  Painel Arize Phoenix (Container Docker)
                </span>
              </div>
              <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#94a3b8' }}>
                Inspecione grafos de nós do LangGraph, waterfall de spans, latência e traces completos em tempo real.
              </p>
            </div>

            <a
              href="http://localhost:6006"
              target="_blank"
              rel="noreferrer"
              className="btn-primary"
              style={{
                fontSize: '11px',
                padding: '6px 12px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                textDecoration: 'none',
              }}
            >
              <span>Abrir Phoenix (:6006)</span>
              <ExternalLink size={12} />
            </a>
          </div>

          {/* Table of Spans */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#e2e8f0' }}>
                Histórico de Spans & Etapas do Fluxograma ({spans.length})
              </span>
              <button
                type="button"
                onClick={onReset}
                className="btn-link btn-xs"
                style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#ef4444' }}
              >
                <RotateCcw size={12} />
                <span>Reiniciar Sessão FinOps</span>
              </button>
            </div>

            {spans.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px', color: '#64748b', fontSize: '12px' }}>
                Nenhuma chamada registrada ainda. Realize um brainstorm ou gere uma proposta para ver o consumo de tokens.
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                      <th style={{ padding: '8px 6px' }}>Etapa</th>
                      <th style={{ padding: '8px 6px' }}>Modelo</th>
                      <th style={{ padding: '8px 6px' }}>Persona</th>
                      <th style={{ padding: '8px 6px' }}>Tokens (In / Out)</th>
                      <th style={{ padding: '8px 6px' }}>Latência</th>
                      <th style={{ padding: '8px 6px' }}>Custo (BRL)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {spans.map((s, idx) => (
                      <tr key={s.spanId || idx} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '8px 6px', fontWeight: 600, color: '#f1f5f9' }}>
                          {s.name}
                        </td>
                        <td style={{ padding: '8px 6px', color: '#cbd5e1' }}>{s.model}</td>
                        <td style={{ padding: '8px 6px', color: '#94a3b8' }}>{s.persona || '—'}</td>
                        <td style={{ padding: '8px 6px', color: '#38bdf8' }}>
                          {s.usage.totalTokens} ({s.usage.promptTokens} / {s.usage.completionTokens})
                        </td>
                        <td style={{ padding: '8px 6px', color: '#94a3b8' }}>
                          <Clock size={11} style={{ display: 'inline', marginRight: '3px' }} />
                          {s.latencyMs.toFixed(0)} ms
                        </td>
                        <td style={{ padding: '8px 6px', fontWeight: 600, color: '#10b981' }}>
                          R$ {s.cost.brl.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer" style={{ justifyContent: 'space-between' }}>
          <span style={{ fontSize: '11px', color: '#64748b' }}>
            Baseado na tabela oficial de precificação FinOps do Banco BV.
          </span>
          <button type="button" className="btn-secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}
