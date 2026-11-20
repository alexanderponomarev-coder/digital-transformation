from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class LayerId(str, Enum):
    STRATEGY = "strategy"
    PROCESSES = "processes"
    DATA = "data"
    TOOLS = "tools"
    GOVERNANCE = "governance"


class CoverageStatus(str, Enum):
    CLOSED = "closed"
    PARTIAL = "partial"
    MISSING = "missing"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    HYPOTHESIS = "hypothesis"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    LINK = "link"


class SourceRef(BaseModel):
    document_id: str
    document_title: str
    fragment: str
    page: int | None = None


class Fact(BaseModel):
    id: str
    text: str
    entity_type: Literal["role", "system", "process", "kpi", "risk", "data", "other"]
    layers: list[LayerId]
    source: SourceRef
    confidence: Confidence = Confidence.MEDIUM
    # P1 / TC-02: do not mix regulation with practice
    evidence_kind: Literal["norm", "observed", "unknown"] = "unknown"
    period: str | None = None
    sample_size: int | None = None
    metric_value: str | None = None
    metric_unit: str | None = None


class DocumentRecord(BaseModel):
    id: str
    title: str
    format: DocFormat
    uploaded_at: str
    version: int = 1
    replaces_id: str | None = None
    layers: list[LayerId] = Field(default_factory=list)
    freshness_days: int = 0
    size_label: str = ""
    summary: str = ""
    status: Literal["processing", "classified", "ready", "partial", "failed"] = "ready"
    # P1 / TC-03: active vs conflict — never auto-pick «действующая» by upload date
    version_status: Literal["active", "superseded", "conflict"] = "active"
    conflict_with_ids: list[str] = Field(default_factory=list)
    ingest_error: str | None = None
    # ACL: empty acl_readers = readable by all callers; else owner + listed users
    owner_id: str | None = None
    acl_readers: list[str] = Field(default_factory=list)


class BlindZone(BaseModel):
    id: str
    title: str
    reason: str
    question_ids: list[str] = Field(default_factory=list)


class LayerCoverage(BaseModel):
    layer_id: LayerId
    status: CoverageStatus
    score: float
    threshold: float
    document_ids: list[str]
    blind_zones: list[BlindZone]
    can_infer: bool


class ClarifyingQuestion(BaseModel):
    id: str
    layer_id: LayerId
    to_role: str
    question: str
    why: str
    status: Literal["open", "answered"] = "open"
    answer: str | None = None
    answered_at: str | None = None


class Insight(BaseModel):
    id: str
    layer_id: LayerId
    kind: Literal["finding", "proposal"]
    title: str
    body: str
    sources: list[SourceRef]
    confidence: Confidence
    approval: ApprovalStatus = ApprovalStatus.HYPOTHESIS
    owner_role: str


class Opportunity(BaseModel):
    id: str
    title: str
    process: str
    autonomy_level: Literal[1, 2, 3, 4, 5]
    impact: Literal["high", "medium", "low"]
    effort: Literal["high", "medium", "low"]
    regulatory_flags: list[str] = Field(default_factory=list)
    admissible: bool = True
    roi_hint: str = ""
    # P2: structured effect for ROI engine / anti-double-count
    process_step_id: str | None = None
    hours_per_year: float | None = None


class RoadmapPhase(BaseModel):
    id: str
    name: str
    horizon: str
    items: list[str]
    investment_mln: float


class KpiDelta(BaseModel):
    name: str
    as_is: str
    to_be: str


class RoiBenefitLine(BaseModel):
    id: str
    description: str
    process_step_id: str
    opportunity_id: str | None = None
    hours_per_year: float | None = None
    hourly_rate: float | None = None  # same currency as investment
    cash_benefit: float | None = None  # direct money, optional
    included: bool = True
    excluded_reason: str | None = None


class RoiComputeRequest(BaseModel):
    investment: float | None = None
    currency: str = "RUB"
    horizon_months: int = 12
    benefits: list[RoiBenefitLine] = Field(default_factory=list)
    allow_overlap: bool = False


class RoiModel(BaseModel):
    investment_mln: float
    annual_benefit_mln: float
    payback_months: int
    tco_3y_mln: float
    kpis: list[KpiDelta]
    assumptions: list[str]
    # P2 / audit ROI rule
    kind: Literal["illustrative", "calculated", "hours_only", "insufficient_inputs"] = (
        "illustrative"
    )
    formula: str = "ROI = (подтверждённые денежные выгоды − совокупные затраты) / совокупные затраты"
    currency: str = "RUB"
    horizon_months: int = 12
    monetary_roi: float | None = None  # None → do not publish as proven ROI
    hours_saved_per_year: float | None = None
    benefit_lines: list[RoiBenefitLine] = Field(default_factory=list)
    overlapping_steps: list[str] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    disclaimer: str = ""


class RegulatoryCheck(BaseModel):
    id: str
    title: str
    basis: str
    status: Literal["pass", "warn", "block"]
    detail: str


class EnterpriseNode(BaseModel):
    id: str
    type: Literal["org", "process", "system", "data", "agent", "kpi"]
    label: str
    meta: str | None = None
    linked_ids: list[str] = Field(default_factory=list)


class EngineMetrics(BaseModel):
    extraction_accuracy: float
    hallucination_rate: float
    coverage_completeness: float


class MethodologyLayer(BaseModel):
    id: LayerId
    number: int
    title: str
    short_title: str
    description: str
    practices: list[str]
    mvp: bool
    blind_spot_hints: list[str]


class ProjectOverview(BaseModel):
    project_name: str
    company_name: str
    industry: str
    coverage_threshold: float
    version: str
    mvp_layers: list[LayerId]
    open_questions_count: int
    approved_insights_count: int
    blocked_cases_count: int
    overall_coverage: float


class PlatformSnapshot(BaseModel):
    overview: ProjectOverview
    layers: list[MethodologyLayer]
    documents: list[DocumentRecord]
    facts: list[Fact]
    coverage: list[LayerCoverage]
    questions: list[ClarifyingQuestion]
    insights: list[Insight]
    opportunities: list[Opportunity]
    roadmap: list[RoadmapPhase]
    roi: RoiModel
    regulatory: list[RegulatoryCheck]
    model_nodes: list[EnterpriseNode]
    engine_metrics: EngineMetrics


class DocumentUploadRequest(BaseModel):
    title: str
    format: DocFormat = DocFormat.PDF
    summary: str = ""
    content_hint: str = ""
    # If non-empty, document is restricted to owner + these user ids
    acl_readers: list[str] = Field(default_factory=list)
    # Simulate / report unreadable source (TC-08)
    read_error: bool = False
    read_error_detail: str = ""


class DocumentAclRequest(BaseModel):
    acl_readers: list[str]
    owner_id: str | None = None


class ConfirmVersionRequest(BaseModel):
    """Owner confirms which conflicting version is the active regulation."""

    note: str = ""


class AnswerQuestionRequest(BaseModel):
    answer: str


class ApprovalRequest(BaseModel):
    status: Literal["approved", "rejected", "pending"]


class ClassifyResult(BaseModel):
    document: DocumentRecord
    facts: list[Fact]
    layers: list[LayerId]
    message: str
