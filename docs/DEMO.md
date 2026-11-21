# Демо-версия STRATUM

Стенд с **синтетическим** корпусом холдинга «СеверПром». Данные не относятся к реальному заказчику и не предназначены для управленческих решений.

## Что заполнено

| Объект | Объём (seed) |
|--------|----------------|
| Документы | ≥ 20 |
| Факты | ≥ 25 |
| Вопросы | 12 |
| Инсайты | 10 |
| Возможности | 8 |
| Узлы модели | 17 |
| Дорожная карта | 4 фазы |
| Зрелость | полный профиль 4×3 |

Маркировка: `overview.is_demo`, `overview.demo_label`, баннер в UI, `GET /api/health` → `demo: true`, `edition: "demo"`.

## Полный цикл

```bash
PYTHONPATH=backend python scripts/run_demo_cycle.py
PYTHONPATH=backend python scripts/run_demo_cycle.py --write-snapshot
```

Прогон: health → snapshot → upload → version confirm → ответ на вопрос → approval → AS-IS/TO-BE → regulatory → ROI → compare → maturity → audit.

Статический fallback фронта: `frontend/public/demo-snapshot.json` (обновляется `--write-snapshot`).
