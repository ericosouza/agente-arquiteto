import type {
  ArchitectureProposal,
  ArchiMateModel,
  SystemInfo,
  ValidationReport,
  ChatMessage,
  PrerequisitesInfo,
  PersonaType,
  BrainstormResponse,
} from '../types/archimate'

const API_BASE = '/api'

export interface ChatResponsePayload {
  message: string
  inScope?: boolean
  proposal?: ArchitectureProposal
  validation?: ValidationReport
  archimateModel?: ArchiMateModel
  diagramSvg?: string
  prerequisites?: PrerequisitesInfo
  missingPrerequisites?: string[]
  persona?: PersonaType
}

export async function fetchSystemInfo(): Promise<SystemInfo> {
  const res = await fetch(`${API_BASE}/info`)
  if (!res.ok) throw new Error('Falha ao obter status do sistema')
  return res.json()
}

export async function brainstormArchitecture(
  message: string,
  history: ChatMessage[] = [],
  prerequisites?: PrerequisitesInfo | null,
  persona: PersonaType = 'arquiteto'
): Promise<BrainstormResponse> {
  const res = await fetch(`${API_BASE}/architecture/brainstorm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history,
      prerequisites: prerequisites || undefined,
      persona,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro no brainstorm' }))
    throw new Error(err.detail || 'Falha na sessão de brainstorm')
  }
  return res.json()
}

export async function analyzeArchitecture(
  description: string,
  constraints: string[] = [],
  history: ChatMessage[] = [],
  prerequisites?: PrerequisitesInfo | null,
  persona: PersonaType = 'arquiteto'
): Promise<ChatResponsePayload> {
  const res = await fetch(`${API_BASE}/architecture/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      description,
      constraints,
      history,
      prerequisites: prerequisites || undefined,
      persona,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro no servidor' }))
    throw new Error(err.detail || 'Falha ao analisar requisitos')
  }
  return res.json()
}

export async function refineArchitecture(
  proposal: ArchitectureProposal,
  feedback: string,
  persona: PersonaType = 'arquiteto'
): Promise<ChatResponsePayload> {
  const res = await fetch(`${API_BASE}/architecture/refine`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proposal, feedback, persona }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro no servidor' }))
    throw new Error(err.detail || 'Falha ao ajustar proposta')
  }
  return res.json()
}

export async function approveArchitecture(
  proposal: ArchitectureProposal
): Promise<ChatResponsePayload> {
  const res = await fetch(`${API_BASE}/architecture/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proposal }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro no servidor' }))
    throw new Error(err.detail || 'Falha ao aprovar arquitetura')
  }
  return res.json()
}

export async function downloadJsonModel(model: ArchiMateModel): Promise<void> {
  const res = await fetch(`${API_BASE}/architecture/export/json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model),
  })
  if (!res.ok) throw new Error('Falha ao exportar JSON')
  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${model.identifier || 'archimate_model'}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

export async function downloadXmlModel(model: ArchiMateModel): Promise<void> {
  const res = await fetch(`${API_BASE}/architecture/export/xml`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model),
  })
  if (!res.ok) throw new Error('Falha ao exportar XML (.archimate)')
  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${model.identifier || 'archimate_model'}.archimate`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}


export async function fetchFinOpsSummary(): Promise<import('../types/archimate').FinOpsSummary> {
  const res = await fetch(`${API_BASE}/observability/finops/summary`)
  if (!res.ok) throw new Error('Falha ao obter métricas de FinOps')
  return res.json()
}

export async function resetFinOpsMetrics(): Promise<void> {
  const res = await fetch(`${API_BASE}/observability/finops/reset`, { method: 'POST' })
  if (!res.ok) throw new Error('Falha ao reiniciar métricas de FinOps')
}
