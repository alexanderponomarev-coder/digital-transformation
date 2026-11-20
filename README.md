# STRATUM — Agentic Enterprise Transformation Platform

Платформа для анализа и управления переходом предприятия к агентной модели.

Документы → классификация по 5 слоям методологии → карта покрытия → выводы с атрибуцией → вопросы в слепых зонах → TO-BE / roadmap / ROI → регуляторный фильтр РФ.

## Стек

- **Backend:** Python 3.12, FastAPI
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS
- **Публикация:** Debian VPS — **native (systemd + nginx, без Docker)** или Docker Compose
- **Тесты:** pytest (API + engine)

## Быстрый старт (dev)

```bash
make install
make api    # :8000
make web    # :5173
make test
```

- UI: http://127.0.0.1:5173  
- API docs: http://127.0.0.1:8000/docs  

Демо-проект: холдинг **СеверПром**.

## Публикация на Debian VPS

Подробно: [docs/DEPLOY_DEBIAN.md](docs/DEPLOY_DEBIAN.md)

```bash
# Без Docker (systemd + nginx) — основной вариант
git clone <repo-url> /opt/stratum-src
cd /opt/stratum-src
sudo bash deploy/debian/install.sh

# Автообновление с GitHub (timer каждые ~5 мин)
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
# + webhook на push:
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook

# С Docker
sudo bash deploy/debian/install-docker.sh
```

После деплоя:

```bash
curl -fsS http://YOUR_VPS_IP/api/health
./scripts/smoke-deploy.sh http://YOUR_VPS_IP
```

## Документация

- [Концепция v1.1](docs/CONCEPT.md)
- [ТЗ v1.0](docs/TZ.md)
- [Деплой Debian](docs/DEPLOY_DEBIAN.md)

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
