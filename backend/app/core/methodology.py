from __future__ import annotations

from app.models.schemas import LayerId, MethodologyLayer

COVERAGE_THRESHOLD_DEFAULT = 0.55

LAYERS: list[MethodologyLayer] = [
    MethodologyLayer(
        id=LayerId.STRATEGY,
        number=1,
        title="Стратегия и аппетит к автономии",
        short_title="Стратегия",
        description=(
            "Бизнес-цели, приоритетные функции, допустимый риск и граница автономии агентов. "
            "Автономия растёт только вместе с доказанной управляемостью."
        ),
        practices=["TOGAF Strategy", "Business Capability Mapping"],
        mvp=True,
        blind_spot_hints=[
            "Целевой уровень автономии по функциям",
            "Риск-аппетит руководства",
            "Приоритетные P&L-функции",
        ],
    ),
    MethodologyLayer(
        id=LayerId.PROCESSES,
        number=2,
        title="Процессы и точки решений",
        short_title="Процессы",
        description=(
            "Карта процессов, decision points, текущий уровень автоматизации "
            "по шкале Parasuraman (уровни 1–5)."
        ),
        practices=["Parasuraman et al., 2000", "BPMN / Process Mining"],
        mvp=True,
        blind_spot_hints=[
            "Критические decision points без владельца",
            "Фактический уровень автоматизации",
            "Боли и узкие места процессов",
        ],
    ),
    MethodologyLayer(
        id=LayerId.DATA,
        number=3,
        title="Данные и знания",
        short_title="Данные",
        description=(
            "Источники для RAG, права доступа, качество, метаданные и пригодность данных "
            "для агентных сценариев."
        ),
        practices=["DAMA-DMBOK", "Data Quality & Catalog"],
        mvp=True,
        blind_spot_hints=[
            "Качество и свежесть ключевых датасетов",
            "Права на использование в ИИ",
            "Локализация ПДн (152-ФЗ)",
        ],
    ),
    MethodologyLayer(
        id=LayerId.TOOLS,
        number=4,
        title="Инструменты и интеграции",
        short_title="Инструменты",
        description="API, корпоративные системы, действия агента и паттерны tool use.",
        practices=["TOGAF Application/Technology", "Tool-use patterns"],
        mvp=False,
        blind_spot_hints=[
            "Каталог API и SLA",
            "Права на write-действия агентов",
            "Реестр российского ПО (КИИ/ГИС)",
        ],
    ),
    MethodologyLayer(
        id=LayerId.GOVERNANCE,
        number=5,
        title="Управление и надзор",
        short_title="Надзор",
        description=(
            "Guardrails, human-in-the-loop, аудит, классификация рисков, "
            "распределение ответственности."
        ),
        practices=["NIST AI RMF", "ISO/IEC 42001", "ЦБ РФ Кодекс этики ИИ"],
        mvp=False,
        blind_spot_hints=[
            "HITL для денег, договоров, доступов, ПДн",
            "Владелец / разработчик / оператор агента",
            "Аудит действий и инцидентов",
        ],
    ),
]

LAYER_BY_ID = {layer.id: layer for layer in LAYERS}

# Keywords used by the deterministic classifier (MVP stand-in for LLM extraction).
LAYER_KEYWORDS: dict[LayerId, list[str]] = {
    LayerId.STRATEGY: [
        "стратег",
        "цел",
        "kpi",
        "окр",
        "риск-аппетит",
        "приоритет",
        "трансформац",
        "автономи",
        "миссия",
        "видение",
    ],
    LayerId.PROCESSES: [
        "процесс",
        "bpmn",
        "регламент",
        "decision",
        "согласован",
        "workflow",
        "операц",
        "узк",
        "sla",
        "маршрут",
    ],
    LayerId.DATA: [
        "данн",
        "catalog",
        "хранил",
        "пдн",
        "персональн",
        "качество",
        "метаданн",
        "rag",
        "источник",
        "mdm",
    ],
    LayerId.TOOLS: [
        "api",
        "интеграц",
        "erp",
        "crm",
        "1с",
        "сервис",
        "система",
        "tool",
        "эндпоинт",
        "шина",
    ],
    LayerId.GOVERNANCE: [
        "политик",
        "надзор",
        "аудит",
        "guardrail",
        "hitl",
        "ответственн",
        "комплаенс",
        "инцидент",
        "роль",
        "доступ",
    ],
}