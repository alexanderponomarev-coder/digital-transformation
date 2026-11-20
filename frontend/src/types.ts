export type LayerId = 'strategy' | 'processes' | 'data' | 'tools' | 'governance'
export type CoverageStatus = 'closed' | 'partial' | 'missing'
export type Confidence = 'high' | 'medium' | 'low' | 'none'
export type ApprovalStatus = 'draft' | 'hypothesis' | 'pending' | 'approved' | 'rejected'

export interface SourceRef {
  document_id: string
  document_title: string
  fragment: string
  page?: number | null
}

export interface Fact {
  id: string
  text: string
  entity_type: string
  layers: LayerId[]
  source: SourceRef
  confidence: Confidence
  evidence_kind?: 'norm' | 'observed' | 'unknown'
  period?: string | null
  sample_size?: number | null
  metric_value?: string | null
  metric_unit?: string | null
}

export interface DocumentRecord {
  id: string
  title: string
  format: string
  uploaded_at: string
  version: number
  replaces_id?: string | null
  layers: LayerId[]
  freshness_days: number
  size_label: string
  summary: string
  status: string
  version_status?: 'active' | 'superseded' | 'conflict'
  conflict_with_ids?: string[]
  ingest_error?: string | null
  owner_id?: string | null
  acl_readers?: string[]
}

export interface BlindZone {
  id: string
  title: string
  reason: string
  question_ids: string[]
}

export interface LayerCoverage {
  layer_id: LayerId
  status: CoverageStatus
  score: number
  threshold: number
  document_ids: string[]
  blind_zones: BlindZone[]
  can_infer: boolean
}

export interface ClarifyingQuestion {
  id: string
  layer_id: LayerId
  to_role: string
  question: string
  why: string
  status: 'open' | 'answered'
  answer?: string | null
  answered_at?: string | null
}

export interface Insight {
  id: string
  layer_id: LayerId
  kind: 'finding' | 'proposal'
  title: string
  body: string
  sources: SourceRef[]
  confidence: Confidence
  approval: ApprovalStatus
  owner_role: string
}

export interface Opportunity {
  id: string
  title: string
  process: string
  autonomy_level: 1 | 2 | 3 | 4 | 5
  impact: 'high' | 'medium' | 'low'
  effort: 'high' | 'medium' | 'low'
  regulatory_flags: string[]
  admissible: boolean
  roi_hint: string
}

export interface RoadmapPhase {
  id: string
  name: string
  horizon: string
  items: string[]
  investment_mln: number
}

export interface RoiModel {
  investment_mln: number
  annual_benefit_mln: number
  payback_months: number
  tco_3y_mln: number
  kpis: { name: string; as_is: string; to_be: string }[]
  assumptions: string[]
}

export interface RegulatoryCheck {
  id: string
  title: string
  basis: string
  status: 'pass' | 'warn' | 'block'
  detail: string
}

export interface EnterpriseNode {
  id: string
  type: 'org' | 'process' | 'system' | 'data' | 'agent' | 'kpi'
  label: string
  meta?: string | null
  linked_ids: string[]
}

export interface MethodologyLayer {
  id: LayerId
  number: number
  title: string
  short_title: string
  description: string
  practices: string[]
  mvp: boolean
  blind_spot_hints: string[]
}

export interface ProjectOverview {
  project_name: string
  company_name: string
  industry: string
  coverage_threshold: number
  version: string
  mvp_layers: LayerId[]
  open_questions_count: number
  approved_insights_count: number
  blocked_cases_count: number
  overall_coverage: number
}

export interface PlatformSnapshot {
  overview: ProjectOverview
  layers: MethodologyLayer[]
  documents: DocumentRecord[]
  facts: Fact[]
  coverage: LayerCoverage[]
  questions: ClarifyingQuestion[]
  insights: Insight[]
  opportunities: Opportunity[]
  roadmap: RoadmapPhase[]
  roi: RoiModel
  regulatory: RegulatoryCheck[]
  model_nodes: EnterpriseNode[]
  engine_metrics: {
    extraction_accuracy: number
    hallucination_rate: number
    coverage_completeness: number
  }
}

export interface ClassifyResult {
  document: DocumentRecord
  facts: Fact[]
  layers: LayerId[]
  message: string
}
