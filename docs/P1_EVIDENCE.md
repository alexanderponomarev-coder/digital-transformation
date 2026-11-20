# P1 — Норматив vs наблюдение, версии, partial read

## evidence_kind (TC-02)

| Значение | Смысл |
|----------|--------|
| `norm` | Из утверждённого регламента / политики («как должно») |
| `observed` | Из журнала/выборки с `period` и `sample_size` («как было») |
| `unknown` | Не размечено |

`/api/model/as-is` отдаёт раздельно `norm_facts` и `observed_facts`.

## Конфликт версий (TC-03)

Повторная загрузка с тем же `title`:

- обе редакции → `version_status=conflict`
- `can_infer` на затронутых слоях = false
- действующая выбирается только через  
  `POST /api/documents/{id}/confirm-version`  
  (остальные same-title → `superseded`)

## Ошибка чтения (TC-08)

```json
{ "title": "…", "format": "pdf", "read_error": true, "read_error_detail": "CRC error" }
```

→ `status=failed`, факты не создаются, документ не входит в `coverage.document_ids`, сообщение о неполном охвате.
