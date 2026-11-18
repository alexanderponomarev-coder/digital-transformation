# STRATUM — Agentic Enterprise Transformation Platform

Платформа для анализа и управления переходом предприятия к агентной модели.

Документы → классификация по 5 слоям методологии → карта покрытия → выводы с атрибуцией → вопросы в слепых зонах → TO-BE / roadmap / ROI → регуляторный фильтр РФ.

## Стек

- **Backend:** Python 3.12, FastAPI
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS
- **Тесты:** pytest (API + engine)

## Быстрый старт

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (другой терминал)
cd frontend
npm install
npm run dev
```

- UI: http://127.0.0.1:5173  
- API docs: http://127.0.0.1:8000/docs  

Демо-проект: холдинг **СеверПром**.

## Тесты

```bash
source .venv/bin/activate
cd backend && pytest -q
```

## Документация

- [Концепция v1.1](docs/CONCEPT.md)
- [ТЗ v1.0](docs/TZ.md)

## MVP-модули

| Модуль | Путь UI |
|--------|---------|
| Обзор | `/app` |
| Документы | `/app/documents` |
| Покрытие | `/app/coverage` |
| Методология | `/app/methodology` |
| Вопросы | `/app/questions` |
| Модель | `/app/model` |
| План и ROI | `/app/roadmap` |
| Регуляторика | `/app/regulatory` |
