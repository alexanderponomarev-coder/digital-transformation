from __future__ import annotations

from datetime import datetime, timezone

from app.core.methodology import COVERAGE_THRESHOLD_DEFAULT, LAYERS
from app.models.schemas import (
    ApprovalStatus,
    BlindZone,
    ClarifyingQuestion,
    Confidence,
    DocFormat,
    DocumentRecord,
    EngineMetrics,
    EnterpriseNode,
    Fact,
    Insight,
    KpiDelta,
    LayerCoverage,
    LayerId,
    Opportunity,
    PlatformSnapshot,
    ProjectOverview,
    RegulatoryCheck,
    RoadmapPhase,
    RoiModel,
    SourceRef,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def build_snapshot() -> PlatformSnapshot:
    docs = [
        DocumentRecord(
            id="doc-strategy-2025",
            title="Стратегия СеверПром 2025–2027",
            format=DocFormat.PDF,
            uploaded_at="2025-11-02",
            version=2,
            replaces_id="doc-strategy-2024",
            layers=[LayerId.STRATEGY, LayerId.GOVERNANCE],
            freshness_days=16,
            size_label="2.4 МБ",
            summary="Цели роста EBITDA, приоритет цифровых каналов, риск-аппетит «умеренный».",
            status="ready",
        ),
        DocumentRecord(
            id="doc-bpm-sales",
            title="Регламент процесса «Заказ → Отгрузка»",
            format=DocFormat.DOCX,
            uploaded_at="2025-10-18",
            version=3,
            layers=[LayerId.PROCESSES, LayerId.TOOLS],
            freshness_days=31,
            size_label="890 КБ",
            summary="12 шагов, 4 точки согласования, SLA 48 ч, узкое место — кредитный контроль.",
            status="ready",
            version_status="active",
        ),
        DocumentRecord(
            id="doc-otc-journal",
            title="Выгрузка журнала OTC (синтетика)",
            format=DocFormat.XLSX,
            uploaded_at="2025-10-01",
            version=1,
            layers=[LayerId.PROCESSES],
            freshness_days=48,
            size_label="640 КБ",
            summary="Синтетическая выборка кейсов кредитного контроля за 2025-Q3.",
            status="ready",
            version_status="active",
        ),
        DocumentRecord(
            id="doc-data-catalog",
            title="Каталог корпоративных данных (выдержка)",
            format=DocFormat.XLSX,
            uploaded_at="2025-09-05",
            version=1,
            layers=[LayerId.DATA],
            freshness_days=74,
            size_label="1.1 МБ",
            summary="42 датасета; 8 с ПДн; качество «клиенты» — 72%; MDM в пилоте.",
            status="ready",
        ),
        DocumentRecord(
            id="doc-it-landscape",
            title="Карта ИС и интеграций",
            format=DocFormat.PPTX,
            uploaded_at="2025-08-20",
            version=1,
            layers=[LayerId.TOOLS, LayerId.DATA],
            freshness_days=90,
            size_label="3.6 МБ",
            summary="ERP 1С:УХ, CRM Bitrix24, WMS, шина Kafka; 37 API без единого каталога SLA.",
            status="ready",
        ),
        DocumentRecord(
            id="doc-ai-policy-draft",
            title="Черновик политики ИИ (не утверждён)",
            format=DocFormat.PDF,
            uploaded_at="2025-11-10",
            version=1,
            layers=[LayerId.GOVERNANCE, LayerId.STRATEGY],
            freshness_days=8,
            size_label="410 КБ",
            summary="HITL для финансов заявлен; распределение ответственности не зафиксировано.",
            status="ready",
        ),
    ]

    facts = [
        Fact(
            id="f1",
            text="Целевой рост EBITDA +12% к 2027 за счёт операционной эффективности и цифровых каналов.",
            entity_type="kpi",
            layers=[LayerId.STRATEGY],
            source=SourceRef(
                document_id="doc-strategy-2025",
                document_title="Стратегия СеверПром 2025–2027",
                fragment="Раздел 2.1: целевые показатели",
                page=7,
            ),
            confidence=Confidence.HIGH,
        ),
        Fact(
            id="f2",
            text="Риск-аппетит руководства — умеренный; запрещены автономные write-действия без HITL в финансах.",
            entity_type="risk",
            layers=[LayerId.STRATEGY, LayerId.GOVERNANCE],
            source=SourceRef(
                document_id="doc-strategy-2025",
                document_title="Стратегия СеверПром 2025–2027",
                fragment="Раздел 4.3: риск-аппетит",
                page=19,
            ),
            confidence=Confidence.HIGH,
        ),
        Fact(
            id="f3",
            text="Процесс «Заказ → Отгрузка»: 4 decision points; норматив SLA 48 ч.",
            entity_type="process",
            layers=[LayerId.PROCESSES],
            source=SourceRef(
                document_id="doc-bpm-sales",
                document_title="Регламент процесса «Заказ → Отгрузка»",
                fragment="§3 Точки решений / SLA",
            ),
            confidence=Confidence.HIGH,
            evidence_kind="norm",
            metric_value="48",
            metric_unit="час",
        ),
        Fact(
            id="f4",
            text="По регламенту узкое место — кредитный контроль: ручное согласование (заявлена очередь 6–14 ч).",
            entity_type="process",
            layers=[LayerId.PROCESSES],
            source=SourceRef(
                document_id="doc-bpm-sales",
                document_title="Регламент процесса «Заказ → Отгрузка»",
                fragment="§5 Узкие места",
            ),
            confidence=Confidence.MEDIUM,
            evidence_kind="norm",
            metric_value="6–14",
            metric_unit="час",
        ),
        Fact(
            id="f3o",
            text="Наблюдаемый цикл OTC (медиана): 4.1 дня.",
            entity_type="process",
            layers=[LayerId.PROCESSES],
            source=SourceRef(
                document_id="doc-otc-journal",
                document_title="Выгрузка журнала OTC (синтетика)",
                fragment="Агрегат cycle_time_days",
            ),
            confidence=Confidence.HIGH,
            evidence_kind="observed",
            period="2025-07-01…2025-09-30",
            sample_size=120,
            metric_value="4.1",
            metric_unit="день",
        ),
        Fact(
            id="f4o",
            text="Наблюдаемая очередь кредитного контроля (p50): 9 ч; p90: 16 ч.",
            entity_type="process",
            layers=[LayerId.PROCESSES],
            source=SourceRef(
                document_id="doc-otc-journal",
                document_title="Выгрузка журнала OTC (синтетика)",
                fragment="Агрегат credit_queue_hours",
            ),
            confidence=Confidence.HIGH,
            evidence_kind="observed",
            period="2025-07-01…2025-09-30",
            sample_size=120,
            metric_value="9",
            metric_unit="час",
        ),
        Fact(
            id="f5",
            text="8 датасетов содержат ПДн; обработка должна оставаться на территории РФ (152-ФЗ).",
            entity_type="data",
            layers=[LayerId.DATA],
            source=SourceRef(
                document_id="doc-data-catalog",
                document_title="Каталог корпоративных данных (выдержка)",
                fragment="Лист «ПДн»",
            ),
            confidence=Confidence.HIGH,
        ),
        Fact(
            id="f6",
            text="Качество мастер-данных «Клиенты» — 72%; дубли ~9%.",
            entity_type="data",
            layers=[LayerId.DATA],
            source=SourceRef(
                document_id="doc-data-catalog",
                document_title="Каталог корпоративных данных (выдержка)",
                fragment="Лист «Качество»",
            ),
            confidence=Confidence.MEDIUM,
        ),
        Fact(
            id="f7",
            text="Ключевые системы: 1С:УХ, Bitrix24, WMS; интеграционная шина Kafka.",
            entity_type="system",
            layers=[LayerId.TOOLS],
            source=SourceRef(
                document_id="doc-it-landscape",
                document_title="Карта ИС и интеграций",
                fragment="Слайд 4 — ландшафт",
            ),
            confidence=Confidence.HIGH,
        ),
        Fact(
            id="f8",
            text="Роль CDO назначена; роль владельца ИИ-агентов формально не закреплена.",
            entity_type="role",
            layers=[LayerId.GOVERNANCE, LayerId.STRATEGY],
            source=SourceRef(
                document_id="doc-ai-policy-draft",
                document_title="Черновик политики ИИ (не утверждён)",
                fragment="§2 Роли",
            ),
            confidence=Confidence.MEDIUM,
        ),
    ]

    questions = [
        ClarifyingQuestion(
            id="q1",
            layer_id=LayerId.STRATEGY,
            to_role="CEO / стратегия",
            question="Какой целевой уровень автономии допустим для кредитного контроля (1–5)?",
            why="Документы фиксируют запрет write без HITL, но не задают целевой уровень по функции.",
        ),
        ClarifyingQuestion(
            id="q2",
            layer_id=LayerId.PROCESSES,
            to_role="Владелец процесса OTC",
            question="Какие decision points нельзя делегировать агенту даже с HITL?",
            why="Слепая зона: карта точек решений не содержит классификации по делегируемости.",
        ),
        ClarifyingQuestion(
            id="q3",
            layer_id=LayerId.DATA,
            to_role="CDO",
            question="Есть ли согласие/основание на использование ПДн клиентов в RAG для агентов поддержки?",
            why="Каталог отмечает ПДн, но не фиксирует правовой режим для ИИ-обработки.",
        ),
        ClarifyingQuestion(
            id="q4",
            layer_id=LayerId.GOVERNANCE,
            to_role="Юрист / комплаенс",
            question="Кто несёт ответственность как владелец, разработчик и оператор пилотного агента?",
            why="До пилота требуется фиксация распределения (ст. 1064 ГК РФ).",
            status="open",
        ),
        ClarifyingQuestion(
            id="q5",
            layer_id=LayerId.TOOLS,
            to_role="CIO",
            question="Какие API допускают write-доступ агента в проде на этапе пилота?",
            why="Карта ИС есть, каталог прав агента — нет (слой 4, V2).",
        ),
    ]

    coverage = [
        LayerCoverage(
            layer_id=LayerId.STRATEGY,
            status="partial",
            score=0.72,
            threshold=COVERAGE_THRESHOLD_DEFAULT,
            document_ids=["doc-strategy-2025", "doc-ai-policy-draft"],
            blind_zones=[
                BlindZone(
                    id="bz-s1",
                    title="Целевой уровень автономии по функциям",
                    reason="Стратегия задаёт риск-аппетит, но не матрицу автономии функций.",
                    question_ids=["q1"],
                )
            ],
            can_infer=True,
        ),
        LayerCoverage(
            layer_id=LayerId.PROCESSES,
            status="partial",
            score=0.72,
            threshold=COVERAGE_THRESHOLD_DEFAULT,
            document_ids=["doc-bpm-sales", "doc-otc-journal"],
            blind_zones=[
                BlindZone(
                    id="bz-p1",
                    title="Делегируемость decision points",
                    reason="Регламент описывает шаги, но не уровень автономии на каждой точке.",
                    question_ids=["q2"],
                )
            ],
            can_infer=True,
        ),
        LayerCoverage(
            layer_id=LayerId.DATA,
            status="partial",
            score=0.58,
            threshold=COVERAGE_THRESHOLD_DEFAULT,
            document_ids=["doc-data-catalog", "doc-it-landscape"],
            blind_zones=[
                BlindZone(
                    id="bz-d1",
                    title="Правовой режим ПДн для ИИ",
                    reason="Есть перечень ПДн-датасетов, нет оснований для агентной обработки.",
                    question_ids=["q3"],
                )
            ],
            can_infer=True,
        ),
        LayerCoverage(
            layer_id=LayerId.TOOLS,
            status="partial",
            score=0.41,
            threshold=COVERAGE_THRESHOLD_DEFAULT,
            document_ids=["doc-it-landscape", "doc-bpm-sales"],
            blind_zones=[
                BlindZone(
                    id="bz-t1",
                    title="Права write для агентов",
                    reason="Ландшафт систем есть; матрица tool-прав отсутствует.",
                    question_ids=["q5"],
                )
            ],
            can_infer=False,
        ),
        LayerCoverage(
            layer_id=LayerId.GOVERNANCE,
            status="missing",
            score=0.28,
            threshold=COVERAGE_THRESHOLD_DEFAULT,
            document_ids=["doc-ai-policy-draft", "doc-strategy-2025"],
            blind_zones=[
                BlindZone(
                    id="bz-g1",
                    title="Распределение ответственности",
                    reason="Политика в черновике; роли владельца/оператора не утверждены.",
                    question_ids=["q4"],
                )
            ],
            can_infer=False,
        ),
    ]

    insights = [
        Insight(
            id="i1",
            layer_id=LayerId.STRATEGY,
            kind="finding",
            title="Приоритет эффективности через цифровые каналы",
            body=(
                "Стратегия прямо связывает рост EBITDA с операционной эффективностью. "
                "Агентные сценарии в OTC и поддержке соответствуют приоритетам."
            ),
            sources=[
                SourceRef(
                    document_id="doc-strategy-2025",
                    document_title="Стратегия СеверПром 2025–2027",
                    fragment="Раздел 2.1",
                    page=7,
                )
            ],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.APPROVED,
            owner_role="Директор по стратегии",
        ),
        Insight(
            id="i2",
            layer_id=LayerId.PROCESSES,
            kind="finding",
            title="Кредитный контроль — главный кандидат на агентную поддержку",
            body=(
                "Очередь 6–14 ч на ручном согласовании. Рекомендуется агент уровня 2–3 "
                "(подготовка рекомендации + HITL), не полный автономенный write."
            ),
            sources=[
                SourceRef(
                    document_id="doc-bpm-sales",
                    document_title="Регламент процесса «Заказ → Отгрузка»",
                    fragment="§5 Узкие места",
                )
            ],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.PENDING,
            owner_role="Владелец процесса OTC",
        ),
        Insight(
            id="i3",
            layer_id=LayerId.DATA,
            kind="proposal",
            title="Перед пилотом поднять качество MDM «Клиенты»",
            body=(
                "При качестве 72% и дублях ~9% RAG будет давать ложные рекомендации. "
                "Порог допуска к пилоту — качество ≥85%."
            ),
            sources=[
                SourceRef(
                    document_id="doc-data-catalog",
                    document_title="Каталог корпоративных данных (выдержка)",
                    fragment="Лист «Качество»",
                )
            ],
            confidence=Confidence.MEDIUM,
            approval=ApprovalStatus.HYPOTHESIS,
            owner_role="CDO",
        ),
        Insight(
            id="i4",
            layer_id=LayerId.STRATEGY,
            kind="proposal",
            title="Целевая модель: агент-рекомендатель + HITL на деньги и договоры",
            body=(
                "TO-BE: агенты готовят решения; человек утверждает write по деньгам, "
                "договорам, доступам и ПДн. Полная автономия (ур. 5) вне периметра MVP."
            ),
            sources=[
                SourceRef(
                    document_id="doc-strategy-2025",
                    document_title="Стратегия СеверПром 2025–2027",
                    fragment="Раздел 4.3",
                    page=19,
                ),
                SourceRef(
                    document_id="doc-ai-policy-draft",
                    document_title="Черновик политики ИИ (не утверждён)",
                    fragment="§3 HITL",
                ),
            ],
            confidence=Confidence.MEDIUM,
            approval=ApprovalStatus.PENDING,
            owner_role="CEO",
        ),
    ]

    opportunities = [
        Opportunity(
            id="opp-1",
            title="Агент кредитного контроля",
            process="Заказ → Отгрузка / кредитный контроль",
            autonomy_level=3,
            impact="high",
            effort="medium",
            regulatory_flags=["HITL обязателен (деньги)", "ПДн клиентов"],
            admissible=True,
            roi_hint="Сокращение очереди на 60–70%, +0.8 дня к циклу OTC",
        ),
        Opportunity(
            id="opp-2",
            title="Агент подготовки коммерческих предложений",
            process="Продажи / КП",
            autonomy_level=2,
            impact="medium",
            effort="low",
            regulatory_flags=["HITL на договоры"],
            admissible=True,
            roi_hint="−30% времени менеджера на подготовку КП",
        ),
        Opportunity(
            id="opp-3",
            title="Автономное изменение лимитов в ERP без HITL",
            process="Финансы / лимиты",
            autonomy_level=5,
            impact="high",
            effort="high",
            regulatory_flags=["Блок: деньги без HITL", "Риск-аппетит"],
            admissible=False,
            roi_hint="Отклонён регуляторным фильтром",
        ),
        Opportunity(
            id="opp-4",
            title="RAG-ассистент поддержки по базе знаний",
            process="Клиентский сервис",
            autonomy_level=2,
            impact="medium",
            effort="low",
            regulatory_flags=["Локализация ПДн", "Без облачных LLM на ПДн"],
            admissible=True,
            roi_hint="−25% времени 1-й линии",
        ),
    ]

    roadmap = [
        RoadmapPhase(
            id="ph-0",
            name="Фундамент данных и прав",
            horizon="0–3 мес",
            items=[
                "Поднять качество MDM «Клиенты» до ≥85%",
                "Зафиксировать роли владельца/оператора агента",
                "Утвердить HITL-матрицу по деньгам/договорам/ПДн",
            ],
            investment_mln=4.5,
        ),
        RoadmapPhase(
            id="ph-1",
            name="Пилот OTC",
            horizon="3–6 мес",
            items=[
                "Пилот агента кредитного контроля (ур. 3 + HITL)",
                "Агент подготовки КП (ур. 2)",
                "Замер cycle time и точности рекомендаций",
            ],
            investment_mln=9.0,
        ),
        RoadmapPhase(
            id="ph-2",
            name="Масштаб и надзор",
            horizon="6–12 мес",
            items=[
                "Расширение на сервис (RAG, on-prem)",
                "Agent Passport и аудит действий",
                "Фактический ROI vs прогноз",
            ],
            investment_mln=14.0,
        ),
    ]

    roi = RoiModel(
        investment_mln=27.5,
        annual_benefit_mln=41.0,
        payback_months=10,
        tco_3y_mln=48.0,
        kpis=[
            KpiDelta(
                name="Цикл OTC",
                as_is="норматив SLA 48 ч / наблюдение 4.1 дня (n=120, 2025-Q3)",
                to_be="2.2 дня",
            ),
            KpiDelta(
                name="Очередь кредитного контроля",
                as_is="норматив 6–14 ч (регламент) / наблюдение p50=9 ч",
                to_be="≤2 ч",
            ),
            KpiDelta(name="Качество MDM «Клиенты»", as_is="72%", to_be="≥90%"),
            KpiDelta(name="Доля HITL на write-деньги", as_is="н/д", to_be="100%"),
        ],
        assumptions=[
            "Пилот охватывает 40% заказов OTC",
            "Качество данных достигает порога до старта пилота",
            "Модели ИИ — on-prem / доверенный контур (без передачи ПДн в облако)",
            "Утверждение выводов владельцами разделов сохраняется",
        ],
    )

    regulatory = [
        RegulatoryCheck(
            id="reg-152",
            title="Локализация ПДн",
            basis="152-ФЗ (ужесточение с 01.07.2025)",
            status="warn",
            detail="В каталоге 8 ПДн-датасетов. Нужна гарантия сбора/обработки на территории РФ.",
        ),
        RegulatoryCheck(
            id="reg-243",
            title="Категория модели ИИ",
            basis="243-ФЗ",
            status="warn",
            detail="Для пилота зафиксировать использование суверенной/национальной модели или on-prem.",
        ),
        RegulatoryCheck(
            id="reg-cloud",
            title="Запрет облачных ИИ на чувствительные данные",
            basis="Требования по чувствительным данным / ФСТЭК с 01.03.2026",
            status="pass",
            detail="В дорожной карте заложен on-prem контур; облачные LLM на ПДн не планируются.",
        ),
        RegulatoryCheck(
            id="reg-hitl",
            title="Human-in-the-loop",
            basis="Внутренняя политика + лучшие практики",
            status="pass",
            detail="Кейсы с деньгами/договорами/ПДн требуют HITL; автономный write-лимит отклонён.",
        ),
        RegulatoryCheck(
            id="reg-resp",
            title="Распределение ответственности",
            basis="ст. 1064 ГК РФ",
            status="block",
            detail="До пилота не зафиксированы владелец, разработчик и оператор агента.",
        ),
        RegulatoryCheck(
            id="reg-kii",
            title="Реестр российского ПО (КИИ/ГИС)",
            basis="С 01.03.2026 для КИИ/ГИС",
            status="warn",
            detail="Профиль «обычный бизнес» — мониторинг. При статусе КИИ/ГИС — обязательный фильтр ПО.",
        ),
    ]

    model_nodes = [
        EnterpriseNode(
            id="org-ceo",
            type="org",
            label="CEO / Стратегия",
            meta="Риск-аппетит: умеренный",
            linked_ids=["kpi-ebitda", "proc-otc"],
        ),
        EnterpriseNode(
            id="org-cdo",
            type="org",
            label="CDO",
            meta="Владелец данных",
            linked_ids=["data-clients", "sys-mdm"],
        ),
        EnterpriseNode(
            id="proc-otc",
            type="process",
            label="Заказ → Отгрузка",
            meta="Цикл 3.2 дня",
            linked_ids=["agent-credit", "sys-1c", "kpi-otc"],
        ),
        EnterpriseNode(
            id="sys-1c",
            type="system",
            label="1С:УХ",
            meta="ERP",
            linked_ids=["proc-otc", "data-clients"],
        ),
        EnterpriseNode(
            id="sys-mdm",
            type="system",
            label="MDM (пилот)",
            meta="Качество клиентов 72%",
            linked_ids=["data-clients"],
        ),
        EnterpriseNode(
            id="data-clients",
            type="data",
            label="Мастер-данные «Клиенты»",
            meta="ПДн, качество 72%",
            linked_ids=["agent-credit", "agent-rag"],
        ),
        EnterpriseNode(
            id="agent-credit",
            type="agent",
            label="Агент кредитного контроля",
            meta="Ур. автономии 3 · HITL",
            linked_ids=["proc-otc", "data-clients", "sys-1c"],
        ),
        EnterpriseNode(
            id="agent-rag",
            type="agent",
            label="RAG-ассистент поддержки",
            meta="Ур. автономии 2 · on-prem",
            linked_ids=["data-clients"],
        ),
        EnterpriseNode(
            id="kpi-ebitda",
            type="kpi",
            label="EBITDA +12% к 2027",
            linked_ids=["org-ceo"],
        ),
        EnterpriseNode(
            id="kpi-otc",
            type="kpi",
            label="Цикл OTC → 2.2 дня",
            linked_ids=["proc-otc", "agent-credit"],
        ),
    ]

    overall = sum(c.score for c in coverage) / len(coverage)

    overview = ProjectOverview(
        project_name="Агентная трансформация СеверПром",
        company_name="СеверПром",
        industry="Промышленный холдинг / дистрибуция",
        coverage_threshold=COVERAGE_THRESHOLD_DEFAULT,
        version="MVP 0.1",
        mvp_layers=[LayerId.STRATEGY, LayerId.PROCESSES, LayerId.DATA],
        open_questions_count=sum(1 for q in questions if q.status == "open"),
        approved_insights_count=sum(
            1 for i in insights if i.approval == ApprovalStatus.APPROVED
        ),
        blocked_cases_count=sum(1 for o in opportunities if not o.admissible)
        + sum(1 for r in regulatory if r.status == "block"),
        overall_coverage=round(overall, 2),
    )

    return PlatformSnapshot(
        overview=overview,
        layers=LAYERS,
        documents=docs,
        facts=facts,
        coverage=coverage,
        questions=questions,
        insights=insights,
        opportunities=opportunities,
        roadmap=roadmap,
        roi=roi,
        regulatory=regulatory,
        model_nodes=model_nodes,
        engine_metrics=EngineMetrics(
            extraction_accuracy=0.86,
            hallucination_rate=0.04,
            coverage_completeness=overall,
        ),
    )


# keep import used for typing side-effects in tests
SEED_GENERATED_AT = _now()
