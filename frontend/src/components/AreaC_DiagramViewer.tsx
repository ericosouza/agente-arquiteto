import React, { useState, useRef, useEffect } from 'react'
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Compass,
  Layers,
  Eye,
} from 'lucide-react'

interface AreaCProps {
  svgMarkup: string | null
  diagramTitle?: string
}

export const AreaC_DiagramViewer: React.FC<AreaCProps> = ({
  svgMarkup,
  diagramTitle,
}) => {
  const [zoom, setZoom] = useState<number>(1)
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState<boolean>(false)
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 })
  const [showLegend, setShowLegend] = useState<boolean>(true)

  const containerRef = useRef<HTMLDivElement>(null)

  // Reset zoom and pan when new svg is received
  useEffect(() => {
    if (svgMarkup) {
      setZoom(1)
      setPan({ x: 0, y: 0 })
    }
  }, [svgMarkup])

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.15, 3.0))
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.15, 0.4))
  const handleResetZoom = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return // only left click
    setIsDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    })
  }

  const handleMouseUp = () => setIsDragging(false)

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const zoomFactor = e.deltaY < 0 ? 0.08 : -0.08
    setZoom((prev) => Math.min(Math.max(prev + zoomFactor, 0.4), 3.0))
  }

  return (
    <div className="card area-c-card">
      <div className="card-header">
        <div className="card-title">
          <Eye className="text-primary" size={18} />
          <span>Área C — Diagrama ArchiMate 3.2</span>
          {diagramTitle && <span className="diagram-subtitle">• {diagramTitle}</span>}
        </div>

        {svgMarkup && (
          <div className="diagram-controls">
            <button
              onClick={() => setShowLegend(!showLegend)}
              className={`btn-control ${showLegend ? 'active' : ''}`}
              title="Alternar legenda ArchiMate"
            >
              <Compass size={14} />
              <span>Legenda</span>
            </button>
            <div className="zoom-btn-group">
              <button onClick={handleZoomOut} className="btn-control" title="Reduzir zoom">
                <ZoomOut size={14} />
              </button>
              <span className="zoom-indicator">{Math.round(zoom * 100)}%</span>
              <button onClick={handleZoomIn} className="btn-control" title="Aumentar zoom">
                <ZoomIn size={14} />
              </button>
              <button onClick={handleResetZoom} className="btn-control" title="Ajustar à tela">
                <Maximize2 size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      <div
        ref={containerRef}
        className={`diagram-viewport ${isDragging ? 'is-dragging' : ''}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        {svgMarkup ? (
          <div
            className="svg-transform-container"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center',
            }}
            dangerouslySetInnerHTML={{ __html: svgMarkup }}
          />
        ) : (
          <div className="diagram-placeholder">
            <Layers size={48} className="text-muted" />
            <p className="placeholder-title">Nenhum diagrama gerado ainda</p>
            <p className="placeholder-subtitle">
              Revise a proposta na <strong>Área B</strong> e clique no botão{' '}
              <strong>"Aprovar Arquitetura"</strong> ou <strong>"Gerar Diagrama"</strong> na{' '}
              <strong>Área D</strong>.
            </p>
          </div>
        )}

        {/* Floating ArchiMate Layer & Glyph Legend */}
        {svgMarkup && showLegend && (
          <div className="floating-legend">
            <h6 className="legend-title">Convenção ArchiMate 3.2</h6>
            <div className="legend-items">
              <div className="legend-row">
                <span className="legend-color-box legend-business"></span>
                <span>
                  <strong>Business Layer:</strong> Atores de negócio e processos
                </span>
              </div>
              <div className="legend-row">
                <span className="legend-color-box legend-application"></span>
                <span>
                  <strong>Application Layer:</strong> Frontend, APIs, Serviços, Objetos de Dados
                </span>
              </div>
              <div className="legend-row">
                <span className="legend-color-box legend-technology"></span>
                <span>
                  <strong>Technology Layer:</strong> Bancos de Dados, Redis, Fila, Nós de Execução
                </span>
              </div>
              <div className="legend-divider"></div>
              <div className="legend-row">
                <span className="legend-symbol">──▶</span>
                <span>
                  <strong>Serving:</strong> Provedor atende consumidor
                </span>
              </div>
              <div className="legend-row">
                <span className="legend-symbol">- - ▶</span>
                <span>
                  <strong>Access:</strong> Leitura/Escrita de dados
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
