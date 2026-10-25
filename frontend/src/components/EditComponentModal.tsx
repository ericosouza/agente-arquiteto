import React, { useState } from 'react'
import { X, Save } from 'lucide-react'
import type {
  ComponentItem,
  ArchiMateLayer,
  ArchiMateElementType,
} from '../types/archimate'

interface EditComponentModalProps {
  component: ComponentItem | null
  isNew?: boolean
  onSave: (updated: ComponentItem) => void
  onClose: () => void
}

export const EditComponentModal: React.FC<EditComponentModalProps> = ({
  component,
  isNew = false,
  onSave,
  onClose,
}) => {
  if (!component) return null

  const [formData, setFormData] = useState<ComponentItem>({ ...component })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onClose()
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <h4>{isNew ? 'Adicionar Novo Componente' : `Editar Componente: ${component.id}`}</h4>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-group">
            <label>ID do Componente</label>
            <input
              type="text"
              value={formData.id}
              onChange={(e) => setFormData({ ...formData, id: e.target.value })}
              required
              disabled={!isNew}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Nome do Componente</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="form-input"
              placeholder="Ex: Frontend Web, API de Produtos"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Categoria</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="form-select"
              >
                <option value="Frontend">Frontend</option>
                <option value="Backend">Backend</option>
                <option value="BFF">BFF (Backend for Frontend)</option>
                <option value="Database">Database</option>
                <option value="Cache">Cache</option>
                <option value="Messaging">Messaging</option>
                <option value="External">External System</option>
                <option value="Auth">Auth & Security</option>
                <option value="Observability">Observability</option>
                <option value="Infrastructure">Infrastructure</option>
              </select>
            </div>

            <div className="form-group">
              <label>Camada ArchiMate (Layer)</label>
              <select
                value={formData.layer}
                onChange={(e) =>
                  setFormData({ ...formData, layer: e.target.value as ArchiMateLayer })
                }
                className="form-select"
              >
                <option value="Channel">Channel Layer</option>
                <option value="Application">Application Layer</option>
                <option value="Technology">Technology Layer</option>
                <option value="Business">Business Layer</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Tipo ArchiMate (Metamodelo)</label>
            <select
              value={formData.archimateType}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  archimateType: e.target.value as ArchiMateElementType,
                })
              }
              className="form-select"
            >
              <option value="ApplicationComponent">ApplicationComponent</option>
              <option value="ApplicationService">ApplicationService</option>
              <option value="DataObject">DataObject</option>
              <option value="SystemSoftware">SystemSoftware</option>
              <option value="Node">Node</option>
              <option value="TechnologyService">TechnologyService</option>
              <option value="BusinessActor">BusinessActor</option>
            </select>
          </div>

          <div className="form-group">
            <label>Tecnologia Sugerida</label>
            <input
              type="text"
              value={formData.suggestedTechnology}
              onChange={(e) =>
                setFormData({ ...formData, suggestedTechnology: e.target.value })
              }
              required
              className="form-input"
              placeholder="Ex: React com TypeScript, Python com FastAPI, PostgreSQL..."
            />
          </div>

          <div className="form-group">
            <label>Tecnologia Alternativa (Opcional)</label>
            <input
              type="text"
              value={formData.alternativeTechnology || ''}
              onChange={(e) =>
                setFormData({ ...formData, alternativeTechnology: e.target.value })
              }
              className="form-input"
              placeholder="Ex: Angular, MySQL, RabbitMQ..."
            />
          </div>

          <div className="form-group">
            <label>Responsabilidade Arquitetural</label>
            <textarea
              value={formData.responsibility}
              onChange={(e) =>
                setFormData({ ...formData, responsibility: e.target.value })
              }
              required
              rows={2}
              className="form-textarea"
            />
          </div>

          <div className="form-group">
            <label>Justificativa Técnica</label>
            <textarea
              value={formData.justification}
              onChange={(e) =>
                setFormData({ ...formData, justification: e.target.value })
              }
              required
              rows={2}
              className="form-textarea"
            />
          </div>

          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancelar
            </button>
            <button type="submit" className="btn-primary">
              <Save size={15} />
              <span>Salvar Alterações</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
