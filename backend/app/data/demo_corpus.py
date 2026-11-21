"""Расширенный синтетический корпус для демо-прогона полного цикла (СеверПром)."""

from __future__ import annotations

from app.models.schemas import (
    ApprovalStatus,
    ClarifyingQuestion,
    Confidence,
    CoverageStatus,
    DocFormat,
    DocumentRecord,
    EnterpriseNode,
    Fact,
    Insight,
    LayerCoverage,
    LayerId,
    Opportunity,
    RoadmapPhase,
    SourceRef,
)

DEMO_BANNER = (
    "ДЕМО-ВЕРСИЯ · все данные синтетические (холдинг «СеверПром»). "
    "Не являются сведениями реального заказчика и не предназначены для решений."
)


def extra_documents() -> list[DocumentRecord]:
    specs = [
        ("doc-risk-appetite", "Матрица риск-аппетита (синтетика)", DocFormat.XLSX, [LayerId.STRATEGY, LayerId.GOVERNANCE], "Уровни риска по функциям OTC/финансы/сервис."),
        ("doc-org-chart", "Оргструктура ИТ и данных", DocFormat.PDF, [LayerId.GOVERNANCE, LayerId.STRATEGY], "CDO → CEO; владельцы доменов не везде назначены."),
        ("doc-sla-otc", "SLA сервисов OTC", DocFormat.DOCX, [LayerId.PROCESSES], "Нормативы очереди, эскалации, окна обслуживания."),
        ("doc-credit-policy", "Кредитная политика (фрагмент)", DocFormat.PDF, [LayerId.PROCESSES, LayerId.GOVERNANCE], "Лимиты, скоринг, запрет авто-write лимитов."),
        ("doc-mdm-plan", "План MDM «Клиенты» 2025–2026", DocFormat.PPTX, [LayerId.DATA], "Цели качества 85%→90%, роли steward."),
        ("doc-pdn-register", "Реестр обработки ПДн (синтетика)", DocFormat.XLSX, [LayerId.DATA, LayerId.GOVERNANCE], "8 категорий; основания 152-ФЗ частично заполнены."),
        ("doc-api-catalog", "Черновик каталога API", DocFormat.XLSX, [LayerId.TOOLS], "37 endpoint; write-права агентов не размечены."),
        ("doc-kafka-topology", "Топология шины событий", DocFormat.PPTX, [LayerId.TOOLS, LayerId.DATA], "Топики заказов, остатков, кредитных событий."),
        ("doc-incident-ai", "Регламент инцидентов ИИ (черновик)", DocFormat.DOCX, [LayerId.GOVERNANCE], "Эскалация; учения не проводились."),
        ("doc-board-pack", "Материалы для совета (черновик)", DocFormat.PDF, [LayerId.STRATEGY, LayerId.GOVERNANCE], "Статус пилотов агентов; без стандарта осмотрительности."),
        ("doc-support-kb", "База знаний 1-й линии (выдержка)", DocFormat.DOCX, [LayerId.PROCESSES, LayerId.DATA], "420 статей; дубли и устаревшие версии."),
        ("doc-wms-as-is", "AS-IS складской контур", DocFormat.PPTX, [LayerId.PROCESSES, LayerId.TOOLS], "WMS + 1С; ручные корректировки остатков."),
        ("doc-cost-model", "Модель стоимости часа (синтетика)", DocFormat.XLSX, [LayerId.STRATEGY], "Ставки ролей OTC/поддержка/аналитика — для ROI."),
        ("doc-vendor-llm", "Сравнение LLM-контуров (синтетика)", DocFormat.PDF, [LayerId.TOOLS, LayerId.GOVERNANCE], "On-prem vs облако; рекомендация on-prem для ПДн."),
        ("doc-pilot-charter", "Устав пилота OTC-агент", DocFormat.DOCX, [LayerId.STRATEGY, LayerId.PROCESSES], "KPI пилота; HITL; объём 40% заказов."),
    ]
    out: list[DocumentRecord] = []
    for i, (did, title, fmt, layers, summary) in enumerate(specs):
        out.append(
            DocumentRecord(
                id=did,
                title=f"[ДЕМО] {title}",
                format=fmt,
                uploaded_at=f"2025-{(i % 9) + 1:02d}-{(i % 27) + 1:02d}",
                version=1 + (i % 3),
                layers=layers,
                freshness_days=10 + i * 7,
                size_label=f"{0.3 + i * 0.15:.1f} МБ",
                summary=summary,
                status="ready",
                version_status="active",
            )
        )
    # Version-conflict pair is exercised in scripts/run_demo_cycle.py (upload same title),
    # not pre-seeded — a seed-time conflict would block processes.can_infer for the whole demo.
    return out


def extra_facts() -> list[Fact]:
    rows = [
        ("fx1", "doc-risk-appetite", "Риск-аппетит «умеренный»: автономия >3 на деньгах запрещена без HITL.", "risk", [LayerId.STRATEGY, LayerId.GOVERNANCE], Confidence.HIGH),
        ("fx2", "doc-org-chart", "CDO формально подчиняется CEO; Data Steward назначен только в домене «Клиенты».", "role", [LayerId.GOVERNANCE], Confidence.HIGH),
        ("fx3", "doc-sla-otc", "Норматив эскалации кредитного контроля — 4 ч; факт p90=11 ч (синтетика Q3).", "kpi", [LayerId.PROCESSES], Confidence.MEDIUM, "observed"),
        ("fx4", "doc-credit-policy", "Автоматическое повышение лимита в ERP без подписи контролёра запрещено.", "risk", [LayerId.PROCESSES, LayerId.GOVERNANCE], Confidence.HIGH, "norm"),
        ("fx5", "doc-mdm-plan", "Целевой индекс качества MDM «Клиенты»: 85% к Q1 2026, 90% к Q3 2026.", "kpi", [LayerId.DATA], Confidence.HIGH, "norm"),
        ("fx6", "doc-pdn-register", "Категория «контактные данные B2B» — 1.2 млн записей; трансграничная передача не заявлена.", "data", [LayerId.DATA], Confidence.MEDIUM),
        ("fx7", "doc-api-catalog", "Endpoint /erp/limits допускает write; ACL для сервис-аккаунтов агента не описан.", "system", [LayerId.TOOLS], Confidence.MEDIUM),
        ("fx8", "doc-kafka-topology", "Топик otc.credit.events — источник сигналов для агента-рекомендателя.", "system", [LayerId.TOOLS, LayerId.DATA], Confidence.HIGH),
        ("fx9", "doc-incident-ai", "Класс инцидента «ложное одобрение кредита» — эскалация CDO+COO в течение 2 ч.", "risk", [LayerId.GOVERNANCE], Confidence.MEDIUM, "norm"),
        ("fx10", "doc-board-pack", "Совет запросил ежеквартальный отчёт по пилотам агентов; график ещё не утверждён.", "other", [LayerId.STRATEGY, LayerId.GOVERNANCE], Confidence.LOW),
        ("fx11", "doc-support-kb", "18% статей базы знаний старше 18 месяцев без ревизии (синтетический аудит).", "kpi", [LayerId.DATA, LayerId.PROCESSES], Confidence.MEDIUM, "observed"),
        ("fx12", "doc-wms-as-is", "Корректировки остатков вручную — ~120 операций/нед; кандидат на агента ур.2 с HITL.", "process", [LayerId.PROCESSES], Confidence.MEDIUM, "observed"),
        ("fx13", "doc-cost-model", "Ставка часа кредитного контролёра (синтетика): 2 400 ₽; аналитика данных: 3 100 ₽.", "kpi", [LayerId.STRATEGY], Confidence.MEDIUM),
        ("fx14", "doc-vendor-llm", "Для ПДн рекомендован только on-prem / изолированный контур; облачные LLM — блок.", "risk", [LayerId.TOOLS, LayerId.GOVERNANCE], Confidence.HIGH, "norm"),
        ("fx15", "doc-pilot-charter", "Пилот OTC: 40% заказов, KPI — очередь ≤2 ч и precision рекомендаций ≥90%.", "kpi", [LayerId.STRATEGY, LayerId.PROCESSES], Confidence.HIGH),
        ("fx16", "doc-otc-journal", "Синтетика Q3: 1 840 кейсов кредитного контроля; 12% — серая зона скоринга.", "kpi", [LayerId.PROCESSES], Confidence.HIGH, "observed", "1840", "кейсов"),
        ("fx17", "doc-data-catalog", "Домен «Номенклатура» — качество 88%; домен «Контрагенты» — 72%.", "kpi", [LayerId.DATA], Confidence.HIGH, "observed"),
        ("fx18", "doc-it-landscape", "Bitrix24 ↔ 1С:УХ — 6 интеграций без единого SLA и владельца контракта.", "system", [LayerId.TOOLS], Confidence.MEDIUM),
        ("fx19", "doc-ai-policy-draft", "Черновик требует двух подписей на допуск агента в прод; процедура не пилотировалась.", "risk", [LayerId.GOVERNANCE], Confidence.MEDIUM, "norm"),
        ("fx20", "doc-strategy-2025", "Цифровые каналы должны дать ≥35% прироста заказов к 2027 (синтетическая цель).", "kpi", [LayerId.STRATEGY], Confidence.HIGH, "norm"),
    ]
    facts: list[Fact] = []
    for row in rows:
        fid, doc_id, text, etype, layers, conf = row[0], row[1], row[2], row[3], row[4], row[5]
        evidence = row[6] if len(row) > 6 else "unknown"
        metric_value = row[7] if len(row) > 7 else None
        metric_unit = row[8] if len(row) > 8 else None
        facts.append(
            Fact(
                id=fid,
                text=text,
                entity_type=etype,
                layers=layers,
                source=SourceRef(
                    document_id=doc_id,
                    document_title=f"[ДЕМО] …/{doc_id}",
                    fragment="синтетический фрагмент",
                ),
                confidence=conf,
                evidence_kind=evidence,  # type: ignore[arg-type]
                metric_value=metric_value,
                metric_unit=metric_unit,
                period="2025" if evidence == "observed" else None,
            )
        )
    return facts


def extra_questions() -> list[ClarifyingQuestion]:
    return [
        ClarifyingQuestion(
            id="q6",
            layer_id=LayerId.PROCESSES,
            to_role="Кредитный контролёр",
            question="Какой % серой зоны скоринга допустим для авто-рекомендации без эскалации?",
            why="Журнал OTC показывает 12% серой зоны; порог не зафиксирован.",
        ),
        ClarifyingQuestion(
            id="q7",
            layer_id=LayerId.DATA,
            to_role="Data Steward «Клиенты»",
            question="Когда будет закрыт план качества MDM до 85%?",
            why="Пилот OTC завязан на порог качества данных.",
            status="answered",
            answer="Целевой срок — конец Q1 2026; промежуточный контроль ежемесячно.",
            answered_at="2025-11-15",
        ),
        ClarifyingQuestion(
            id="q8",
            layer_id=LayerId.TOOLS,
            to_role="Архитектор интеграций",
            question="Какие топики Kafka разрешены агенту на чтение в пилоте?",
            why="Топология есть, матрица tool-прав — нет.",
        ),
        ClarifyingQuestion(
            id="q9",
            layer_id=LayerId.GOVERNANCE,
            to_role="CDO",
            question="Кто подписывает допуск агента кредитного контроля в прод (две роли)?",
            why="Черновик политики требует две подписи; роли не названы.",
        ),
        ClarifyingQuestion(
            id="q10",
            layer_id=LayerId.STRATEGY,
            to_role="Куратор совета",
            question="Какой график отчётности по пилотам агентов утверждён советом?",
            why="Board-pack запросил отчётность без утверждённого календаря.",
        ),
        ClarifyingQuestion(
            id="q11",
            layer_id=LayerId.PROCESSES,
            to_role="Владелец складского контура",
            question="Допустима ли рекомендация агента по корректировке остатков с HITL кладовщика?",
            why="AS-IS WMS показывает высокий объём ручных правок.",
        ),
        ClarifyingQuestion(
            id="q12",
            layer_id=LayerId.GOVERNANCE,
            to_role="ИБ / ФСТЭК-контур",
            question="Есть ли аттестация контура для on-prem LLM с ПДн?",
            why="Сравнение LLM-контуров требует доверенной среды.",
            status="answered",
            answer="Аттестация в плане на H1 2026; до этого — изолированный lab-контур без прод-ПДн.",
            answered_at="2025-11-18",
        ),
    ]


def extra_insights() -> list[Insight]:
    return [
        Insight(
            id="i5",
            layer_id=LayerId.GOVERNANCE,
            kind="finding",
            title="[ДЕМО] Пробел применения правил при наличии черновика политики",
            body="Политика ИИ есть как документ, но допуск в прод и учения по остановке не проводились — аспект «применение правил» слабее технологии.",
            sources=[SourceRef(document_id="doc-ai-policy-draft", document_title="Черновик политики ИИ", fragment="§3")],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.APPROVED,
            owner_role="CDO",
        ),
        Insight(
            id="i6",
            layer_id=LayerId.TOOLS,
            kind="proposal",
            title="[ДЕМО] Завести ACL write для сервис-аккаунта агента до пилота",
            body="Без матрицы прав /erp/limits пилот либо заблокирован, либо идёт с теневым доступом.",
            sources=[SourceRef(document_id="doc-api-catalog", document_title="Каталог API", fragment="limits")],
            confidence=Confidence.MEDIUM,
            approval=ApprovalStatus.PENDING,
            owner_role="CIO",
        ),
        Insight(
            id="i7",
            layer_id=LayerId.PROCESSES,
            kind="proposal",
            title="[ДЕМО] Агент рекомендаций по остаткам WMS (ур. 2 + HITL)",
            body="Синтетика: 120 ручных правок/нед. Кандидат после OTC-пилота, не параллельно.",
            sources=[SourceRef(document_id="doc-wms-as-is", document_title="AS-IS WMS", fragment="корректировки")],
            confidence=Confidence.MEDIUM,
            approval=ApprovalStatus.HYPOTHESIS,
            owner_role="Владелец склада",
        ),
        Insight(
            id="i8",
            layer_id=LayerId.DATA,
            kind="finding",
            title="[ДЕМО] Домен «Клиенты» — узкое место для всех агентных сценариев",
            body="Качество 72% и дубли ограничивают и OTC, и RAG поддержки. Фундамент дорожной карты.",
            sources=[SourceRef(document_id="doc-data-catalog", document_title="Каталог данных", fragment="Клиенты")],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.APPROVED,
            owner_role="CDO",
        ),
        Insight(
            id="i9",
            layer_id=LayerId.STRATEGY,
            kind="finding",
            title="[ДЕМО] Пилот OTC согласован со стратегией EBITDA",
            body="Устав пилота и стратегия совпадают по приоритету операционной эффективности.",
            sources=[
                SourceRef(document_id="doc-pilot-charter", document_title="Устав пилота", fragment="KPI"),
                SourceRef(document_id="doc-strategy-2025", document_title="Стратегия", fragment="2.1"),
            ],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.APPROVED,
            owner_role="Директор по стратегии",
        ),
        Insight(
            id="i10",
            layer_id=LayerId.GOVERNANCE,
            kind="proposal",
            title="[ДЕМО] Утвердить календарь отчётности совету до старта пилота",
            body="Без графика надзора режим организации останется ситуативным.",
            sources=[SourceRef(document_id="doc-board-pack", document_title="Board pack", fragment="отчётность")],
            confidence=Confidence.MEDIUM,
            approval=ApprovalStatus.PENDING,
            owner_role="Куратор совета",
        ),
    ]


def extra_opportunities() -> list[Opportunity]:
    return [
        Opportunity(
            id="opp-5",
            title="[ДЕМО] Агент ревизии базы знаний поддержки",
            process="Клиентский сервис / KB",
            autonomy_level=2,
            impact="medium",
            effort="low",
            regulatory_flags=["HITL на публикацию статей"],
            admissible=True,
            roi_hint="Снижение устаревших статей; −15% повторных обращений",
            process_step_id="service.kb_review",
            hours_per_year=900,
        ),
        Opportunity(
            id="opp-6",
            title="[ДЕМО] Агент-рекомендатель корректировок WMS",
            process="Склад / остатки",
            autonomy_level=2,
            impact="medium",
            effort="medium",
            regulatory_flags=["HITL кладовщика"],
            admissible=True,
            roi_hint="Меньше ручных правок; точнее доступность",
            process_step_id="wms.adjust",
            hours_per_year=1400,
        ),
        Opportunity(
            id="opp-7",
            title="[ДЕМО] Авто-списание ПДн без HITL",
            process="Данные / retention",
            autonomy_level=4,
            impact="high",
            effort="medium",
            regulatory_flags=["Блок: ПДн без HITL"],
            admissible=False,
            roi_hint="Отклонён регуляторным фильтром",
            process_step_id="data.retention",
            hours_per_year=0,
        ),
        Opportunity(
            id="opp-8",
            title="[ДЕМО] Мониторинг дрейфа скоринга OTC",
            process="Риск / модели",
            autonomy_level=2,
            impact="medium",
            effort="medium",
            regulatory_flags=["Аудит модели"],
            admissible=True,
            roi_hint="Раннее обнаружение деградации precision",
            process_step_id="risk.model_monitor",
            hours_per_year=600,
        ),
    ]


def extra_roadmap() -> list[RoadmapPhase]:
    return [
        RoadmapPhase(
            id="ph-3",
            name="[ДЕМО] Надзор и страхование риска",
            horizon="12–18 мес",
            items=[
                "Календарь отчётности совету",
                "Учения по остановке агента",
                "Пакет для оценки страхового покрытия (синтетика)",
            ],
            investment_mln=6.5,
        ),
    ]


def extra_nodes() -> list[EnterpriseNode]:
    return [
        EnterpriseNode(id="org-coo", type="org", label="COO", meta="Совместное управление с CDO", linked_ids=["proc-otc", "org-cdo"]),
        EnterpriseNode(id="org-board", type="org", label="Совет директоров", meta="Куратор пилотов (не утверждён)", linked_ids=["org-ceo"]),
        EnterpriseNode(id="sys-kafka", type="system", label="Kafka", meta="Шина событий", linked_ids=["proc-otc", "agent-credit"]),
        EnterpriseNode(id="sys-wms", type="system", label="WMS", meta="Склад", linked_ids=["proc-wms"]),
        EnterpriseNode(id="proc-wms", type="process", label="Складские корректировки", meta="~120 ручных/нед", linked_ids=["sys-wms", "agent-wms"]),
        EnterpriseNode(id="agent-wms", type="agent", label="Агент рекомендаций WMS", meta="Ур. 2 · HITL · демо", linked_ids=["proc-wms"]),
        EnterpriseNode(id="kpi-queue", type="kpi", label="Очередь кредита ≤2 ч", meta="Цель пилота", linked_ids=["agent-credit", "proc-otc"]),
    ]


def merge_coverage(
    base: list[LayerCoverage],
    extra_doc_ids: dict[LayerId, list[str]],
) -> list[LayerCoverage]:
    """Attach extra document ids into existing layer coverage (demo richness)."""
    out: list[LayerCoverage] = []
    for c in base:
        docs = list(c.document_ids) + extra_doc_ids.get(c.layer_id, [])
        # slight score bump for demo fullness but keep can_infer rules
        score = min(0.92, round(c.score + 0.04, 2))
        status = c.status
        if score >= 0.75 and c.layer_id in (LayerId.STRATEGY, LayerId.PROCESSES):
            status = CoverageStatus.PARTIAL
        out.append(
            c.model_copy(
                update={
                    "document_ids": list(dict.fromkeys(docs)),
                    "score": score,
                    "status": status,
                }
            )
        )
    return out


def coverage_doc_map() -> dict[LayerId, list[str]]:
    return {
        LayerId.STRATEGY: ["doc-risk-appetite", "doc-board-pack", "doc-pilot-charter", "doc-cost-model"],
        LayerId.PROCESSES: ["doc-sla-otc", "doc-credit-policy", "doc-wms-as-is", "doc-support-kb", "doc-pilot-charter"],
        LayerId.DATA: ["doc-mdm-plan", "doc-pdn-register", "doc-kafka-topology", "doc-support-kb"],
        LayerId.TOOLS: ["doc-api-catalog", "doc-kafka-topology", "doc-vendor-llm", "doc-wms-as-is"],
        LayerId.GOVERNANCE: [
            "doc-org-chart",
            "doc-risk-appetite",
            "doc-credit-policy",
            "doc-pdn-register",
            "doc-incident-ai",
            "doc-board-pack",
            "doc-vendor-llm",
        ],
    }
