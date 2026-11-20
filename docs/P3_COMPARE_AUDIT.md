# P3 — сравнение альтернатив и журнал запусков

## Сравнение AS-IS / правила / агент+HITL

`POST /api/compare/alternatives`

Тело (опционально):

```json
{
  "process_step_id": "otc.credit_control",
  "cases": [
    {
      "id": "c-low-risk",
      "credit_score": 82,
      "debt_ratio": 0.3,
      "overdue_days": 0,
      "queue_hours_as_is": 6.0
    }
  ]
}
```

Пустой `cases` → встроенный OTC-набор СеверПром (низкий риск / серая зона / высокий риск).

Ответ:

| Поле | Смысл |
|------|--------|
| `cases[].as_is` | ручная очередь (`manual_review`, HITL) |
| `cases[].rules_engine` | детерминированные пороги; может писать в ERP |
| `cases[].agent_hitl` | рекомендация + **обязательный HITL**, `writes_to_erp=false` |
| `rules_agent_agree` | совпала ли рекомендация агента с правилом |
| `agreement_rate` | доля согласованных кейсов |
| `summary` | текстовый итог |

## Журнал аудита

`GET /api/audit/runs?limit=100` → список `AuditEvent`:

| Поле | Назначение |
|------|------------|
| `id`, `ts` | идентификатор и время |
| `actor` | `X-Stratum-User` / lab |
| `action` | `documents.upload`, `compare.alternatives`, `roi.compute`, `store.reset`, … |
| `resource` | id документа / process_step / kind |
| `tools_invoked` | список tool-calls (**всегда `[]` в MVP**) |
| `allowed` | прошла ли операция |
| `detail` | краткий комментарий |

Буфер in-memory, очищается на `POST /api/reset` (после clear пишется событие `store.reset`).

## TC-07 (injection)

Текст вида «игнорируй правила / exfiltrate» в upload **не** порождает tool-calls: в журнале `tools_invoked=[]`, в `detail` — явное указание, что инструкция проигнорирована.

## Связанные тесты

`backend/tests/test_p3_compare_audit.py`
