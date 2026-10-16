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
          {/* Primary Action: Approve & Generate */}
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

          {/* Regenerate if proposal was modified after generation */}
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

          {/* Export Buttons */}
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
              <span>Baixar Open Exchange XML</span>
            </button>
          </div>

          <button onClick={onReset} className="btn-outline-danger" title="Reiniciar projeto">
            <RotateCcw size={15} />
            <span>Reiniciar</span>
          </button>
        </div>
      </div>
    </div>
  )
}
