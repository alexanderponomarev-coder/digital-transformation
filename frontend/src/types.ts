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

export interface RoiBenefitLine {
  id: string
  description: string
  process_step_id: string
  opportunity_id?: string | null
  hours_per_year?: number | null
  hourly_rate?: number | null
  cash_benefit?: number | null
  included?: boolean
  excluded_reason?: string | null
}

export interface RoiModel {
  investment_mln: number
  annual_benefit_mln: number
  payback_months: number
  tco_3y_mln: number
  kpis: { name: string; as_is: string; to_be: string }[]
  assumptions: string[]
  kind?: 'illustrative' | 'calculated' | 'hours_only' | 'insufficient_inputs'
  formula?: string
  currency?: string
  horizon_months?: number
  monetary_roi?: number | null
  hours_saved_per_year?: number | null
  benefit_lines?: RoiBenefitLine[]
  overlapping_steps?: string[]
  missing_inputs?: string[]
  disclaimer?: string
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
  deploy_mode?: 'lab' | 'demo'
  persistence?: 'in_memory'
  storage_disclaimer?: string
}

export type MaturityDomainId =
  | 'infrastructure'
  | 'governance'
  | 'agents'
  | 'organization'
export type MaturityAspectId = 'technology' | 'accountability' | 'rules'

export interface MaturityScore {
  domain_id: MaturityDomainId
  aspect_id: MaturityAspectId
  level: number
}

export interface MaturityDomainResult {
  domain_id: MaturityDomainId
  title: string
  scores: Record<string, number>
  domain_level: number
  weakest_aspect: MaturityAspectId
}

export interface MaturityAssessment {
  scores: MaturityScore[]
  domain_results: MaturityDomainResult[]
  system_level: number
  max_operating_mode: number
  mode_label: string
  next_step: string
  profile_summary: string
  notes?: string
}

export interface MaturityCell {
  domain_id: MaturityDomainId
  aspect_id: MaturityAspectId
  level: number
  description: string
}

export interface MaturityMatrix {
  title: string
  rule: string
  domains: {
    id: MaturityDomainId
    title: string
    capabilities: string
    focus: string
    order: number
  }[]
  aspects: { id: MaturityAspectId; title: string; description: string }[]
  levels: { level: number; title: string; description: string }[]
  cells: MaturityCell[]
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
  maturity?: MaturityAssessment | null
}

export interface AuditEvent {
  id: string
  ts: string
  actor: string
  action: string
  resource?: string
  tools_invoked?: string[]
  allowed?: boolean
  detail?: string
}

export interface AlternativeOutcome {
  kind: 'as_is' | 'rules_engine' | 'agent_hitl'
  decision: string
  requires_hitl: boolean
  writes_to_erp: boolean
  latency_hours: number
  rationale: string
}

export interface ComparisonCaseResult {
  case_id: string
  as_is: AlternativeOutcome
  rules_engine: AlternativeOutcome
  agent_hitl: AlternativeOutcome
  rules_agent_agree: boolean
  notes: string
}

export interface ComparisonResponse {
  process_step_id: string
  cases: ComparisonCaseResult[]
  agreement_rate: number
  summary: string
}

export interface ClassifyResult {
  document: DocumentRecord
  facts: Fact[]
  layers: LayerId[]
  message: string
}
