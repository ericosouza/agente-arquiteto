export type ArchiMateLayer =
  | 'Channel'
  | 'Business'
  | 'Application'
  | 'Technology'
  | 'Physical'
  | 'Strategy'
  | 'Implementation_Migration'

export type ArchiMateElementType =
  | 'BusinessActor'
  | 'BusinessRole'
  | 'BusinessService'
  | 'BusinessProcess'
  | 'ApplicationComponent'
  | 'ApplicationService'
  | 'ApplicationInterface'
  | 'DataObject'
  | 'Node'
  | 'SystemSoftware'
  | 'TechnologyService'
  | 'TechnologyInterface'
  | 'Artifact'

export type ArchiMateRelationshipType =
  | 'Composition'
  | 'Aggregation'
  | 'Assignment'
  | 'Realization'
  | 'Serving'
  | 'Access'
  | 'Flow'
  | 'Triggering'
  | 'Association'

export interface ComponentItem {
  id: string
  name: string
  category: string
  responsibility: string
  suggestedTechnology: string
  alternativeTechnology?: string
  justification: string
  layer: ArchiMateLayer
  archimateType: ArchiMateElementType
}

export interface IntegrationItem {
  id: string
  sourceComponentId: string
  targetComponentId: string
  relationshipType: ArchiMateRelationshipType
  protocol: string
  communicationPattern: 'Synchronous' | 'Asynchronous'
  purpose: string
}

export interface NonFunctionalRequirement {
  category: string
  description: string
}

export interface ArchitecturalDecision {
  decision: string
  rationale: string
  status: string
}

export interface PrerequisitesInfo {
  iniciativa?: string | null
  sigla?: string | null
  feature?: string | null
  arqcor?: string | null
}

export interface ArchitectureProposal {
  id: string
  title: string
  summary: string
  architecturalStyle: string
  styleJustification: string
  components: ComponentItem[]
  integrations: IntegrationItem[]
  decisions: ArchitecturalDecision[]
  nonFunctionalRequirements: NonFunctionalRequirement[]
  prerequisites?: PrerequisitesInfo | null
  status: 'proposed' | 'modified' | 'approved' | 'generated'
  version: number
}

export interface ArchiMateElement {
  id: string
  name: string
  type: ArchiMateElementType
  layer: ArchiMateLayer
  documentation?: string
  properties: Record<string, string>
}

export interface ArchiMateRelationship {
  id: string
  name?: string
  type: ArchiMateRelationshipType
  source: string
  target: string
  documentation?: string
  properties: Record<string, string>
}

export interface ArchiMateViewNode {
  elementId: string
  x: number
  y: number
  width: number
  height: number
}

export interface ArchiMateViewConnection {
  relationshipId: string
  sourceId: string
  targetId: string
}

export interface ArchiMateView {
  id: string
  name: string
  documentation?: string
  nodes: ArchiMateViewNode[]
  connections: ArchiMateViewConnection[]
}

export interface ArchiMateModel {
  identifier: string
  name: string
  documentation: string
  version: string
  metadata: {
    author: string
    createdAt: string
    standard: string
    description?: string
    architecturalStyle?: string
  }
  elements: ArchiMateElement[]
  relationships: ArchiMateRelationship[]
  views: ArchiMateView[]
}

export interface ValidationIssue {
  severity: 'error' | 'warning' | 'info'
  code: string
  message: string
  elementId?: string
  relationshipId?: string
}

export interface ValidationReport {
  isValid: boolean
  totalElements: number
  totalRelationships: number
  errors: ValidationIssue[]
  warnings: ValidationIssue[]
  info: ValidationIssue[]
  summary: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}

export interface SystemInfo {
  appName: string
  appVersion: string
  activeProvider: string
  providers: Record<
    string,
    {
      name: string
      available: boolean
      configured: boolean
      model?: string
      baseUrl?: string
      instructions?: string
      description?: string
    }
  >
}
