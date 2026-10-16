import React, { useState } from 'react'
import { X, Plus, Trash2, Save, ArrowRight } from 'lucide-react'
import type {
  ComponentItem,
  IntegrationItem,
  ArchiMateRelationshipType,
} from '../types/archimate'

interface EditIntegrationModalProps {
  components: ComponentItem[]
  integrations: IntegrationItem[]
  onSaveIntegrations: (updated: IntegrationItem[]) => void
  onClose: () => void
}

export const EditIntegrationModal: React.FC<EditIntegrationModalProps> = ({
  components,
  integrations,
  onSaveIntegrations,
  onClose,
}) => {
  const [list, setList] = useState<IntegrationItem[]>([...integrations])
  const [newIntegration, setNewIntegration] = useState<Partial<IntegrationItem>>({
    sourceComponentId: components[0]?.id || '',
    targetComponentId: components[1]?.id || components[0]?.id || '',
    relationshipType: 'Serving',
    protocol: 'HTTP/REST',
    communicationPattern: 'Synchronous',
    purpose: '',
  })

  const handleRemove = (id: string) => {
    setList((prev) => prev.filter((i) => i.id !== id))
  }

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newIntegration.sourceComponentId || !newIntegration.targetComponentId || !newIntegration.purpose) {
      alert('Preencha os componentes de origem, destino e a finalidade da integração.')
      return
    }

    const item: IntegrationItem = {
      id: `INT-${Date.now().toString().slice(-4)}`,
      sourceComponentId: newIntegration.sourceComponentId,
      targetComponentId: newIntegration.targetComponentId,
      relationshipType: (newIntegration.relationshipType as ArchiMateRelationshipType) || 'Serving',
      protocol: newIntegration.protocol || 'HTTP/REST',
      communicationPattern: (newIntegration.communicationPattern as 'Synchronous' | 'Asynchronous') || 'Synchronous',
      purpose: newIntegration.purpose,
    }

    setList((prev) => [...prev, item])
    setNewIntegration({
      sourceComponentId: components[0]?.id || '',
      targetComponentId: components[1]?.id || components[0]?.id || '',
      relationshipType: 'Serving',
      protocol: 'HTTP/REST',
      communicationPattern: 'Synchronous',
      purpose: '',
    })
  }

  const handleSaveAll = () => {
    onSaveIntegrations(list)
    onClose()
  }

  const getCompName = (id: string) => {
    const comp = components.find((c) => c.id === id)
    return comp ? `${comp.id} (${comp.name.split(' ')[0]})` : id
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-card modal-wide">
        <div className="modal-header">
          <h4>Gerenciar Integrações e Conexões ArchiMate</h4>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="integrations-list-section">
            <h5 className="section-subtitle">Integrações Atuais ({list.length})</h5>
            {list.length === 0 ? (
              <p className="text-muted">Nenhuma integração configurada ainda.</p>
            ) : (
              <div className="integrations-table-wrapper">
                <table className="architecture-table">
                  <thead>
                    <tr>
                      <th>Origem → Destino</th>
                      <th>Tipo ArchiMate</th>
                      <th>Protocolo</th>
                      <th>Padrão</th>
                      <th>Finalidade</th>
                      <th style={{ textAlign: 'center' }}>Ação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {list.map((inte) => (
                      <tr key={inte.id}>
                        <td>
                          <div className="integration-endpoint-cell">
                            <strong>{getCompName(inte.sourceComponentId)}</strong>
                            <ArrowRight size={13} className="text-muted" />
                            <strong>{getCompName(inte.targetComponentId)}</strong>
                          </div>
                        </td>
                        <td>
                          <span className="badge-relationship">{inte.relationshipType}</span>
                        </td>
                        <td>{inte.protocol}</td>
                        <td>
                          <span
                            className={
                              inte.communicationPattern === 'Synchronous'
                                ? 'badge-sync'
                                : 'badge-async'
                            }
                          >
                            {inte.communicationPattern}
                          </span>
                        </td>
                        <td className="cell-purpose">{inte.purpose}</td>
                        <td style={{ textAlign: 'center' }}>
                          <button
                            onClick={() => handleRemove(inte.id)}
                            className="btn-icon btn-icon-danger"
                            title="Remover integração"
                          >
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="divider-h"></div>

          <form onSubmit={handleAdd} className="add-integration-form">
            <h5 className="section-subtitle">Adicionar Nova Integração</h5>
            <div className="form-row-3">
              <div className="form-group">
                <label>Origem (Source)</label>
                <select
                  value={newIntegration.sourceComponentId}
                  onChange={(e) =>
                    setNewIntegration({ ...newIntegration, sourceComponentId: e.target.value })
                  }
                  className="form-select"
                >
                  {components.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.id} - {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Destino (Target)</label>
                <select
                  value={newIntegration.targetComponentId}
                  onChange={(e) =>
                    setNewIntegration({ ...newIntegration, targetComponentId: e.target.value })
                  }
                  className="form-select"
                >
                  {components.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.id} - {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Tipo ArchiMate</label>
                <select
                  value={newIntegration.relationshipType}
                  onChange={(e) =>
                    setNewIntegration({
                      ...newIntegration,
                      relationshipType: e.target.value as ArchiMateRelationshipType,
                    })
                  }
                  className="form-select"
                >
                  <option value="Serving">Serving (Atende / Provê serviço)</option>
                  <option value="Access">Access (Acesso a dados / DB / Cache)</option>
                  <option value="Flow">Flow (Fluxo de eventos / Fila)</option>
                  <option value="Realization">Realization (Realização)</option>
                  <option value="Assignment">Assignment (Alocação)</option>
                </select>
              </div>
            </div>

            <div className="form-row-3">
              <div className="form-group">
                <label>Protocolo / Mecanismo</label>
                <input
                  type="text"
                  value={newIntegration.protocol}
                  onChange={(e) =>
                    setNewIntegration({ ...newIntegration, protocol: e.target.value })
                  }
                  placeholder="Ex: HTTP/REST, JDBC, AMQP..."
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Comunicação</label>
                <select
                  value={newIntegration.communicationPattern}
                  onChange={(e) =>
                    setNewIntegration({
                      ...newIntegration,
                      communicationPattern: e.target.value as 'Synchronous' | 'Asynchronous',
                    })
                  }
                  className="form-select"
                >
                  <option value="Synchronous">Síncrono (Request / Response)</option>
                  <option value="Asynchronous">Assíncrono (Event-Driven / Queue)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Finalidade da Integração</label>
                <input
                  type="text"
                  value={newIntegration.purpose}
                  onChange={(e) =>
                    setNewIntegration({ ...newIntegration, purpose: e.target.value })
                  }
                  placeholder="Ex: Consultar e cadastrar produtos..."
                  className="form-input"
                />
              </div>
            </div>

            <button type="submit" className="btn-secondary btn-sm">
              <Plus size={14} />
              <span>Incluir Conexão</span>
            </button>
          </form>
        </div>

        <div className="modal-footer">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancelar
          </button>
          <button type="button" onClick={handleSaveAll} className="btn-primary">
            <Save size={15} />
            <span>Confirmar Integrações</span>
          </button>
        </div>
      </div>
    </div>
  )
}
