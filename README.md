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

## Установка на VPS (полная инструкция)

**→ [docs/INSTALL.md](docs/INSTALL.md)** — пошагово с нуля: только STRATUM или Klaris+STRATUM на одном узле, автообновление, TLS, диагностика.

Кратко (только STRATUM):

```bash
sudo git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo bash deploy/debian/install.sh /opt/stratum-src
# private repo: токен только в env (не в git remote)
# echo 'STRATUM_GITHUB_TOKEN=ghp_xxx' | sudo tee -a /etc/stratum/stratum.env
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
curl -fsS http://127.0.0.1/api/health
```

Кратко (рядом с Klaris — по домену, оба на `:80`):

```bash
sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh /opt/stratum-src
curl -fsS -H 'Host: stratum.example.com' http://127.0.0.1/api/health
```

## Документация

- [Полная установка на VPS](docs/INSTALL.md)
- [Концепция v1.1](docs/CONCEPT.md)
- [ТЗ v1.0](docs/TZ.md)
- [Деплой Debian (справка)](docs/DEPLOY_DEBIAN.md)
- [Cohost с Klaris](docs/COHOST_KLARIS.md)
- [Доступ API / ACL (P0)](docs/SECURITY.md)
- [Норматив / версии / partial read (P1)](docs/P1_EVIDENCE.md)
- [ROI engine (P2)](docs/P2_ROI.md)
- [Сравнение альтернатив / audit log (P3)](docs/P3_COMPARE_AUDIT.md)
- [Стенд: lab vs demo + TLS (P4)](docs/P4_STAND.md)
- [Автообновление с `main` (timer ~2 мин)](docs/AUTO_UPDATE.md)

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
