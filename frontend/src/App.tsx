import React, { useState, useEffect } from 'react'
import { Header } from './components/Header'
import { AreaA_ChatDescription } from './components/AreaA_ChatDescription'
import { AreaB_ArchitectureProposal } from './components/AreaB_ArchitectureProposal'
import { AreaC_DiagramViewer } from './components/AreaC_DiagramViewer'
import { AreaD_ExportToolbar } from './components/AreaD_ExportToolbar'
import { EditComponentModal } from './components/EditComponentModal'
import { EditIntegrationModal } from './components/EditIntegrationModal'
import { ProviderConfigModal } from './components/ProviderConfigModal'
import { FinOpsModal } from './components/FinOpsModal'
import type {
  ArchitectureProposal,
  ArchiMateModel,
  ComponentItem,
  IntegrationItem,
  SystemInfo,
  ValidationReport,
  ChatMessage,
  PrerequisitesInfo,
  PersonaType,
  FinOpsSummary,
} from './types/archimate'
import {
  fetchSystemInfo,
  analyzeArchitecture,
  refineArchitecture,
  approveArchitecture,
  brainstormArchitecture,
  downloadJsonModel,
  downloadXmlModel,
  fetchFinOpsSummary,
  resetFinOpsMetrics,
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

  // Persona & Brainstorm State
  const [persona, setPersona] = useState<PersonaType>('arquiteto')
  const [activeMode, setActiveMode] = useState<'brainstorm' | 'direct'>('brainstorm')
  const [isReadyForModeling, setIsReadyForModeling] = useState<boolean>(false)

  // FinOps & Observability state
  const [finOpsSummary, setFinOpsSummary] = useState<FinOpsSummary | null>(null)
  const [showFinOpsModal, setShowFinOpsModal] = useState<boolean>(false)

  const refreshFinOps = () => {
    fetchFinOpsSummary().then(setFinOpsSummary).catch(() => {})
  }

  const handleResetFinOps = async () => {
    await resetFinOpsMetrics()
    refreshFinOps()
  }

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
    refreshFinOps()
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

  const handleTriggerModeling = async (additionalContext?: string) => {
    setIsLoading(true)
    const combinedTexts = messages
      .filter((m) => m.role === 'user')
      .map((m) => m.content)

    if (additionalContext) {
      combinedTexts.push(additionalContext)
    }

    const descriptionToAnalyze = combinedTexts.join('\n') || 'Sistema corporativo Banco BV'
    try {
      const res = await analyzeArchitecture(
        descriptionToAnalyze,
        [],
        messages,
        prerequisites,
        persona
      )

      if (res.prerequisites) {
        setPrerequisites(res.prerequisites)
      }

      if (res.inScope === false) {
        const refusalMsg: ChatMessage = {
          id: `msg-ast-${Date.now()}`,
          role: 'assistant',
          content: res.message,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, refusalMsg])
        return
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
      setIsReadyForModeling(false)
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'system',
        content: `Erro na modelagem: ${err.message || 'Falha ao processar.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setIsLoading(false)
      refreshFinOps()
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
        // Mode 1: Brainstorming & RAG interaction
        if (activeMode === 'brainstorm') {
          const lowerText = text.trim().toLowerCase()
          const isTriggerCall =
            lowerText === 'ok' ||
            lowerText.startsWith('ok,') ||
            lowerText.includes('pode gerar') ||
            lowerText.includes('gerar modelo')

          if (isTriggerCall && (prerequisites?.sigla || previousMessages.length >= 2)) {
            await handleTriggerModeling(text)
            return
          }

          const res = await brainstormArchitecture(
            text,
            previousMessages,
            prerequisites,
            persona
          )
          if (res.prerequisites) {
            setPrerequisites(res.prerequisites)
          }
          if (res.isReadyForModeling) {
            setIsReadyForModeling(true)
          }

          const assistantMsg: ChatMessage = {
            id: `msg-ast-${Date.now()}`,
            role: 'assistant',
            content: res.reply,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }
          setMessages((prev) => [...prev, assistantMsg])
        } else {
          // Mode 2: Direct analysis and modeling
          const res = await analyzeArchitecture(text, [], previousMessages, prerequisites, persona)
          if (res.prerequisites) {
            setPrerequisites(res.prerequisites)
          }

          if (res.inScope === false) {
            const refusalMsg: ChatMessage = {
              id: `msg-ast-${Date.now()}`,
              role: 'assistant',
              content: res.message,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            }
            setMessages((prev) => [...prev, refusalMsg])
            return
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
        }
      } else {
        // Proposal already exists: Refinement loop
        const res = await refineArchitecture(proposal, text, persona)
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
      refreshFinOps()
    }
  }

  const handleRequestAdjustments = () => {
    setActiveMode('brainstorm')
    const personaLabel =
      persona === 'arquiteto' ? 'Arquiteto de Software BV' : 'Engenheiro de Software BV'
    const adjustmentPrompt: ChatMessage = {
      id: `msg-adj-${Date.now()}`,
      role: 'assistant',
      content: `🔄 **Modo de Ajuste Ativado**\n\nComo ${personaLabel}, estou pronto para refinar a arquitetura. O que você gostaria de modificar? (Ex: alterar tecnologias, adicionar filas PubSub, mudar o banco para PostgreSQL ou adicionar processamento Batch).`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages((prev) => [...prev, adjustmentPrompt])
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
      refreshFinOps()
    }
  }

  // Component manipulation handlers
  const handleOpenAddComponent = () => {
    setEditingComponent(null)
    setIsNewComponent(true)
    setShowComponentModal(true)
  }

  const handleOpenEditComponent = (component: ComponentItem) => {
    setEditingComponent(component)
    setIsNewComponent(false)
    setShowComponentModal(true)
  }

  const handleDeleteComponent = (componentId: string) => {
    if (!proposal) return
    const updatedComponents = proposal.components.filter((c) => c.id !== componentId)
    const updatedIntegrations = proposal.integrations.filter(
      (i) => i.sourceComponentId !== componentId && i.targetComponentId !== componentId
    )
    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      components: updatedComponents,
      integrations: updatedIntegrations,
      status: 'modified',
      version: proposal.version + 1,
    }
    setProposal(updatedProposal)
    refreshDiagramFromProposal(updatedProposal)
  }

  const handleSaveComponent = (savedComp: ComponentItem) => {
    if (!proposal) return
    let updatedComponents: ComponentItem[]
    if (isNewComponent) {
      updatedComponents = [...proposal.components, savedComp]
    } else {
      updatedComponents = proposal.components.map((c) => (c.id === savedComp.id ? savedComp : c))
    }
    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      components: updatedComponents,
      status: 'modified',
      version: proposal.version + 1,
    }
    setProposal(updatedProposal)
    setShowComponentModal(false)
    refreshDiagramFromProposal(updatedProposal)
  }

  const handleSaveIntegrations = (newIntegrations: IntegrationItem[]) => {
    if (!proposal) return
    const updatedProposal: ArchitectureProposal = {
      ...proposal,
      integrations: newIntegrations,
      status: 'modified',
      version: proposal.version + 1,
    }
    setProposal(updatedProposal)
    setShowIntegrationModal(false)
    refreshDiagramFromProposal(updatedProposal)
  }

  // Export handlers
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
    setIsReadyForModeling(false)
  }

  return (
    <div className="app-layout">
      <Header
        systemInfo={systemInfo}
        finOpsSummary={finOpsSummary}
        onOpenConfig={() => setShowConfigModal(true)}
        onOpenFinOps={() => setShowFinOpsModal(true)}
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
              persona={persona}
              onPersonaChange={setPersona}
              activeMode={activeMode}
              onModeChange={setActiveMode}
              onSendMessage={handleSendMessage}
              onTriggerModeling={() => handleTriggerModeling()}
              isReadyForModeling={isReadyForModeling}
              prerequisites={prerequisites}
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
            onRequestAdjustments={handleRequestAdjustments}
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

      <FinOpsModal
        summary={finOpsSummary}
        isOpen={showFinOpsModal}
        onClose={() => setShowFinOpsModal(false)}
        onReset={handleResetFinOps}
      />
    </div>
  )
}

export default App
