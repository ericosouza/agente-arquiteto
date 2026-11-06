import React from 'react'
import {
  CheckCircle,
  FileDown,
  Download,
  RotateCcw,
  Sparkles,
  FileCode,
  ShieldCheck,
  AlertCircle,
} from 'lucide-react'
import type {
  ArchiMateModel,
  ArchitectureProposal,
  ValidationReport,
} from '../types/archimate'

interface AreaDProps {
  proposal: ArchitectureProposal | null
  model: ArchiMateModel | null
  svgMarkup: string | null
  validation: ValidationReport | null
  isProcessing: boolean
  onApproveAndGenerate: () => void
  onRequestAdjustments?: () => void
  onDownloadSvg: () => void
  onDownloadPng: () => void
  onDownloadJson: () => void
  onDownloadXml: () => void
  onReset: () => void
}

export const AreaD_ExportToolbar: React.FC<AreaDProps> = ({
  proposal,
  model,
  svgMarkup,
  validation,
  isProcessing,
  onApproveAndGenerate,
  onRequestAdjustments,
  onDownloadSvg,
  onDownloadPng,
  onDownloadJson,
  onDownloadXml,
  onReset,
}) => {
  const hasDiagram = Boolean(svgMarkup && model)

  return (
    <div className="card area-d-card">
      <div className="area-d-content">
        <div className="area-d-left">
          <div className="section-label">
            <span className="section-title">Área D — Ações & Exportação ArchiMate</span>
            {validation && (
              <span
                className={`validation-pill ${
                  validation.isValid ? 'val-valid' : 'val-invalid'
                }`}
                title={validation.summary}
              >
                {validation.isValid ? (
                  <>
                    <ShieldCheck size={14} />
                    <span>Metamodelo ArchiMate 3.2 Válido ({validation.totalElements} elem, {validation.totalRelationships} rel)</span>
                  </>
                ) : (
                  <>
                    <AlertCircle size={14} />
                    <span>Erros na validação: {validation.errors.length}</span>
                  </>
                )}
              </span>
            )}
          </div>
        </div>

        <div className="area-d-buttons">
          {/* Ação Primária: Aprovar e Gerar */}
          {proposal && !hasDiagram && (
            <button
              onClick={onApproveAndGenerate}
              disabled={isProcessing}
              className="btn-primary btn-cta"
            >
              <CheckCircle size={16} />
              <span>Aprovar e Gerar Diagrama ArchiMate</span>
            </button>
          )}

          {/* Regerar modelo se a proposta foi alterada após a geração */}
          {proposal && hasDiagram && proposal.status === 'modified' && (
            <button
              onClick={onApproveAndGenerate}
              disabled={isProcessing}
              className="btn-warning"
            >
              <Sparkles size={16} />
              <span>Atualizar Diagrama ArchiMate</span>
            </button>
          )}

          {/* Loop de Ajuste: Voltar para Brainstorming */}
          {hasDiagram && onRequestAdjustments && (
            <button
              onClick={onRequestAdjustments}
              disabled={isProcessing}
              className="btn-secondary"
              style={{ borderColor: '#f59e0b', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '6px' }}
              title="Solicitar alterações retornando para o chat com a Persona"
            >
              <RotateCcw size={15} />
              <span>Solicitar Ajustes</span>
            </button>
          )}

          {/* Botões de Exportação */}
          <div className="export-btn-group">
            <button
              onClick={onDownloadSvg}
              disabled={!hasDiagram || isProcessing}
              className="btn-secondary"
              title="Baixar diagrama visual em formato vetorial SVG"
            >
              <Download size={15} />
              <span>Baixar SVG</span>
            </button>

            <button
              onClick={onDownloadPng}
              disabled={!hasDiagram || isProcessing}
              className="btn-secondary"
              title="Baixar imagem do diagrama em alta resolução PNG"
            >
              <Download size={15} />
              <span>Baixar PNG</span>
            </button>

            <button
              onClick={onDownloadJson}
              disabled={!hasDiagram || isProcessing}
              className="btn-secondary"
              title="Baixar modelo estruturado no formato oficial JSON ArchiMate 3.2"
            >
              <FileCode size={15} />
              <span>Baixar JSON</span>
            </button>

            <button
              onClick={onDownloadXml}
              disabled={!hasDiagram || isProcessing}
              className="btn-secondary"
              title="Baixar formato The Open Group ArchiMate Model Exchange (XML compatível com Archi)"
            >
              <FileDown size={15} />
              <span>Baixar XML (Archi)</span>
            </button>
          </div>

          {/* Botão de Reinício */}
          <button
            onClick={onReset}
            disabled={isProcessing}
            className="btn-link text-danger"
            title="Limpar todos os dados e reiniciar projeto"
          >
            <RotateCcw size={14} />
            <span>Novo Desenho</span>
          </button>
        </div>
      </div>
    </div>
  )
}
