import React, { useState, useEffect } from 'react'
import { Header } from './components/Header'
import { AreaA_ChatDescription } from './components/AreaA_ChatDescription'
import { AreaB_ArchitectureProposal } from './components/AreaB_ArchitectureProposal'
import { AreaC_DiagramViewer } from './components/AreaC_DiagramViewer'
import { AreaD_ExportToolbar } from './components/AreaD_ExportToolbar'
import { EditComponentModal } from './components/EditComponentModal'
import { EditIntegrationModal } from './components/EditIntegrationModal'
import { ProviderConfigModal } from './components/ProviderConfigModal'
import type {
  ArchitectureProposal,
  ArchiMateModel,
  ComponentItem,
  IntegrationItem,
  SystemInfo,
  ValidationReport,
  ChatMessage,
  PrerequisitesInfo,
} from './types/archimate'
import {
  fetchSystemInfo,
  analyzeArchitecture,
  refineArchitecture,
  approveArchitecture,
  downloadJsonModel,
  downloadXmlModel,
} from './services/api'

export const App: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [prerequisites, setPrerequisites] = useState<PrerequisitesInfo | null>(null)
  const [proposal, setProposal] = useState<ArchitectureProposal | null>(null)
  const [archimateModel, setArchimateModel] = useState<ArchiMateModel | null>(null)
  const [diagramSvg, setDiagramSvg] = useState<string | null>(null)
  const [validation, setValidation] = useState<ValidationReport | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  // Modals state
  const [showConfigModal, setShowConfigModal] = useState<boolean>(false)
  const [showComponentModal, setShowComponentModal] = useState<boolean>(false)
  const [showIntegrationModal, setShowIntegrationModal] = useState<boolean>(false)
  const [editingComponent, setEditingComponent] = useState<ComponentItem | null>(null)
  const [isNewComponent, setIsNewComponent] = useState<boolean>(false)

  // Load system info on mount
  useEffect(() => {
    fetchSystemInfo()
      .then(setSystemInfo)
      .catch((err) => console.error('Erro ao carregar status do sistema:', err))
  }, [])

  const refreshDiagramFromProposal = async (updatedProposal: ArchitectureProposal) => {
    try {
      const res = await approveArchitecture(updatedProposal)
      if (res.archimateModel && res.diagramSvg) {
        setArchimateModel(res.archimateModel)
        setDiagramSvg(res.diagramSvg)
        setValidation(res.validation || null)
      }
    } catch (err) {
      console.error('Erro ao atualizar diagrama:', err)
    }
  }

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    const previousMessages = [...messages]
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    try {
      if (!proposal) {
        // Step 1: Validate prerequisites and generate initial proposal + diagram
        const res = await analyzeArchitecture(text, [], previousMessages, prerequisites)
        if (res.prerequisites) {
          setPrerequisites(res.prerequisites)
        }
        if (res.proposal) {
          setProposal(res.proposal)
        }
        if (res.archimateModel && res.diagramSvg) {
          setArchimateModel(res.archimateModel)
          setDiagramSvg(res.diagramSvg)
          setValidation(res.validation || null)
        }
        const assistantMsg: ChatMessage = {
          id: `msg-ast-${Date.now()}`,
          role: 'assistant',
          content: res.message,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, assistantMsg])
      } else {
        // Step 4: Iterative Refinement — updates both proposal AND diagram immediately
        const res = await refineArchitecture(proposal, text)
        if (res.proposal) {
          setProposal(res.proposal)
          if (res.archimateModel && res.diagramSvg) {
            setArchimateModel(res.archimateModel)
            setDiagramSvg(res.diagramSvg)
            setValidation(res.validation || null)
          } else {
            await refreshDiagramFromProposal(res.proposal)
          }

          const assistantMsg: ChatMessage = {
            id: `msg-ast-${Date.now()}`,
            role: 'assistant',
            content: res.message,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }
          setMessages((prev) => [...prev, assistantMsg])
        }
      }
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'system',
        content: `Erro: ${err.message || 'Falha ao processar solicitação.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleApproveAndGenerate = async () => {
    if (!proposal) return
    setIsLoading(true)

    try {
      const res = await approveArchitecture(proposal)
      if (res.archimateModel && res.diagramSvg) {
        setArchimateModel(res.archimateModel)
        setDiagramSvg(res.diagramSvg)
        setValidation(res.validation || null)
        setProposal((prev) => (prev ? { ...prev, status: 'approved' } : null))

        const assistantMsg: ChatMessage = {
          id: `msg-gen-${Date.now()}`,
          role: 'assistant',
          content: res.message,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, assistantMsg])
      }
    } catch (err: any) {
      alert(`Erro ao gerar arquitetura ArchiMate: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  // Component edits
  const handleOpenEditComponent = (comp: ComponentItem) => {
    setEditingComponent(comp)
    setIsNewComponent(false)
    setShowComponentModal(true)
  }

  const handleOpenAddComponent = () => {
    const sigla = proposal?.prerequisites?.sigla?.toLowerCase() || 'proj'
    const newComp: ComponentItem = {
      id: `COMP-${Date.now().toString().slice(-3)}`,
      name: `sboot-${sigla}-base-atom-novo-dominio`,
      category: 'Backend',
      responsibility: 'Responsabilidade do novo componente',
      suggestedTechnology: 'Spring Boot Java',
      justification: 'Necessidade arquitetural adicionada pelo usuário',
      layer: 'Application',
      archimateType: 'ApplicationComponent',
    }
    setEditingComponent(newComp)
    setIsNewComponent(true)
    setShowComponentModal(true)
  }

  const handleSaveComponent = (updatedComp: ComponentItem) => {
    if (!proposal) return
    let updatedList: ComponentItem[]
    if (isNewComponent) {
      updatedList = [...proposal.components, updatedComp]
    } else {
      updatedList = proposal.components.map((c) => (c.id === updatedComp.id ? updatedComp : c))
    }

    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      components: updatedList,
      version: proposal.version + 1,
      status: 'modified',
    }
    setProposal(updatedProposal)
    void refreshDiagramFromProposal(updatedProposal)
  }

  const handleDeleteComponent = (compId: string) => {
    if (!proposal) return
    if (!confirm(`Remover componente ${compId}? As integrações associadas também serão removidas.`))
      return

    const updatedComponents = proposal.components.filter((c) => c.id !== compId)
    const updatedIntegrations = proposal.integrations.filter(
      (i) => i.sourceComponentId !== compId && i.targetComponentId !== compId
    )

    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      components: updatedComponents,
      integrations: updatedIntegrations,
      version: proposal.version + 1,
      status: 'modified',
    }
    setProposal(updatedProposal)
    void refreshDiagramFromProposal(updatedProposal)
  }

  // Integrations edits
  const handleSaveIntegrations = (updatedIntegrations: IntegrationItem[]) => {
    if (!proposal) return
    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      integrations: updatedIntegrations,
      version: proposal.version + 1,
      status: 'modified',
    }
    setProposal(updatedProposal)
    void refreshDiagramFromProposal(updatedProposal)
  }

  // Exports
  const handleDownloadSvg = () => {
    if (!diagramSvg) return
    const blob = new Blob([diagramSvg], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${archimateModel?.identifier || 'archimate_diagram'}.svg`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleDownloadPng = () => {
    if (!diagramSvg) return
    const img = new Image()
    const svgBlob = new Blob([diagramSvg], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)

    img.onload = () => {
      const canvas = document.createElement('canvas')
      // High-res multiplier (2x for retina sharpness)
      const scale = 2
      canvas.width = (img.width || 1200) * scale
      canvas.height = (img.height || 800) * scale

      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.fillStyle = '#FFFFFF'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.scale(scale, scale)
        ctx.drawImage(img, 0, 0)

        canvas.toBlob((blob) => {
          if (!blob) return
          const pngUrl = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = pngUrl
          a.download = `${archimateModel?.identifier || 'archimate_diagram'}.png`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(pngUrl)
        }, 'image/png')
      }
      URL.revokeObjectURL(url)
    }

    img.src = url
  }

  const handleDownloadJson = () => {
    if (archimateModel) {
      downloadJsonModel(archimateModel).catch((err) => alert(err.message))
    }
  }

  const handleDownloadXml = () => {
    if (archimateModel) {
      downloadXmlModel(archimateModel).catch((err) => alert(err.message))
    }
  }

  const handleReset = () => {
    if (proposal && !confirm('Deseja iniciar um novo projeto e limpar a arquitetura atual?'))
      return
    setMessages([])
    setPrerequisites(null)
    setProposal(null)
    setArchimateModel(null)
    setDiagramSvg(null)
    setValidation(null)
  }

  return (
    <div className="app-layout">
      <Header
        systemInfo={systemInfo}
        onOpenConfig={() => setShowConfigModal(true)}
        onReset={handleReset}
      />

      <main className="main-container">
        {/* Top Grid: Area A (Chat) + Area B (Proposal Table) */}
        <div className="top-grid">
          <div className="grid-col-left">
            <AreaA_ChatDescription
              messages={messages}
              isLoading={isLoading}
              hasProposal={Boolean(proposal)}
              onSendMessage={handleSendMessage}
            />
          </div>
          <div className="grid-col-right">
            <AreaB_ArchitectureProposal
              proposal={proposal}
              onEditComponent={handleOpenEditComponent}
              onDeleteComponent={handleDeleteComponent}
              onAddComponent={handleOpenAddComponent}
              onEditIntegrations={() => setShowIntegrationModal(true)}
            />
          </div>
        </div>

        {/* Middle: Area C (Diagram Viewer) */}
        <div className="diagram-section">
          <AreaC_DiagramViewer
            svgMarkup={diagramSvg}
            diagramTitle={proposal?.title}
          />
        </div>

        {/* Bottom: Area D (Export & Action Toolbar) */}
        <div className="export-section">
          <AreaD_ExportToolbar
            proposal={proposal}
            model={archimateModel}
            svgMarkup={diagramSvg}
            validation={validation}
            isProcessing={isLoading}
            onApproveAndGenerate={handleApproveAndGenerate}
            onDownloadSvg={handleDownloadSvg}
            onDownloadPng={handleDownloadPng}
            onDownloadJson={handleDownloadJson}
            onDownloadXml={handleDownloadXml}
            onReset={handleReset}
          />
        </div>
      </main>

      {/* Modals */}
      {showComponentModal && (
        <EditComponentModal
          component={editingComponent}
          isNew={isNewComponent}
          onSave={handleSaveComponent}
          onClose={() => setShowComponentModal(false)}
        />
      )}

      {showIntegrationModal && proposal && (
        <EditIntegrationModal
          components={proposal.components}
          integrations={proposal.integrations}
          onSaveIntegrations={handleSaveIntegrations}
          onClose={() => setShowIntegrationModal(false)}
        />
      )}

      {showConfigModal && (
        <ProviderConfigModal
          systemInfo={systemInfo}
          onClose={() => setShowConfigModal(false)}
        />
      )}
    </div>
  )
}

export default App
