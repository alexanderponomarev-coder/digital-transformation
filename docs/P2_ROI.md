# P2 — ROI engine

## Правило аудита

`ROI = (подтверждённые денежные выгоды − совокупные затраты) / совокупные затраты`  
на одном горизонте и валюте. Без положительной базы затрат **денежный ROI не публикуется** (`monetary_roi=null`).

## kind

| kind | Смысл |
|------|--------|
| `illustrative` | Seed/демо-цифры, не доказательство |
| `hours_only` | Есть часы, нет ставки и/или investment |
| `insufficient_inputs` | Недостаточно входов |
| `calculated` | Есть investment > 0 и монетизация; `monetary_roi` задан |

## API

`POST /api/roi/compute`

```json
{
  "investment": 10000000,
  "currency": "RUB",
  "horizon_months": 12,
  "allow_overlap": false,
  "benefits": [
    {
      "id": "b1",
      "description": "Кредитный контроль",
      "process_step_id": "otc.credit_control",
      "hours_per_year": 1000,
      "hourly_rate": 2000
    }
  ]
}
```

Пересечение одного `process_step_id` по часам → вторая линия `included=false` (TC-05), пока `allow_overlap=true`.
