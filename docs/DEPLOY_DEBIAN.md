# Публикация STRATUM на VPS Debian

> **Полная пошаговая установка с нуля:** [INSTALL.md](INSTALL.md)

Два пути:

1. **Native (systemd + nginx) — без Docker** ← основной для обычного VPS
2. **Docker Compose** — если Docker уже принят в инфраструктуре

Требования: Debian 12+ (bookworm), root/sudo, открытый HTTP-порт (80 или `STRATUM_HTTP_PORT`).

---

## Вариант A — Native, без Docker (рекомендуется)

```bash
git clone <repo-url> /opt/stratum-src
cd /opt/stratum-src
sudo bash deploy/debian/install.sh
```

Что ставится:

| Путь | Назначение |
|------|------------|
| `/opt/stratum` | код + Python venv |
| `/var/www/stratum` | статика React (SPA) |
| `/etc/stratum/stratum.env` | env (CORS и др.) |
| `/etc/systemd/system/stratum-api.service` | uvicorn API |
| `/etc/nginx/sites-available/stratum` | SPA + reverse proxy `/api` |

Проверка:

```bash
sudo systemctl status stratum-api nginx
curl -fsS http://127.0.0.1/api/health
curl -fsS -o /dev/null -w "%{http_code}\n" http://127.0.0.1/
curl -fsS -o /dev/null -w "%{http_code}\n" http://127.0.0.1/app
```

Обновление / удаление:

```bash
cd /opt/stratum-src && git pull
sudo bash deploy/debian/update.sh

# полный снос
sudo bash deploy/debian/uninstall.sh
```

### Автообновление с GitHub

Нужен git-клон (обычно `/opt/stratum-src`) с доступом на `git fetch` (deploy key / token для private repo).

**1) Timer (каждые ~5 мин)**

```bash
# после install.sh
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh

# или сразу при установке
sudo STRATUM_AUTO_UPDATE=1 bash deploy/debian/install.sh /opt/stratum-src

sudo systemctl list-timers stratum-auto-update.timer
sudo journalctl -u stratum-auto-update -f
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

**2) Webhook (мгновенно на push в `main`)**

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```

В GitHub → Settings → Webhooks:

| Поле | Значение |
|------|----------|
| Payload URL | `http://YOUR_VPS/hooks/github` |
| Content type | `application/json` |
| Secret | `STRATUM_WEBHOOK_SECRET` из `/etc/stratum/stratum.env` |
| Events | Just the push event |

Параметры в `/etc/stratum/stratum.env`:

```bash
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GIT_REMOTE=origin
STRATUM_WEBHOOK_SECRET=...
```

Для **private** репозитория (токен только в env; скрипт сам сделает `git clone`, если клона нет):

```bash
# /etc/stratum/stratum.env
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_REPO_URL=https://github.com/ORG/REPO.git
STRATUM_GITHUB_TOKEN=ghp_xxx   # Contents: Read

sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
# → git clone … → timer; origin без токена
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

Альтернатива: SSH deploy key. Подробно — [`INSTALL.md`](INSTALL.md) §3.

Домен (вместо catch-all `_`):

```bash
sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh
```

Если на хосте **нет systemd** (редко на VPS, бывает в контейнерах):

```bash
sudo bash deploy/debian/install.sh
sudo bash deploy/debian/run-native.sh
```

Логи:

```bash
sudo journalctl -u stratum-api -f
# или при run-native.sh:
sudo tail -f /var/log/stratum-api.log
sudo tail -f /var/log/nginx/error.log
```

---

## Вариант B — Docker Compose

```bash
git clone <repo-url> /opt/stratum-src
cd /opt/stratum-src
sudo bash deploy/debian/install-docker.sh
```

Или вручную:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable --now docker
cp .env.example .env
# STRATUM_HTTP_PORT=80
sudo docker compose up -d --build
```

Обновление:

```bash
cd /opt/stratum && sudo docker compose up -d --build
```

---

## TLS

После DNS:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d stratum.example.com
```

---

## Smoke

```bash
make test
./scripts/smoke-deploy.sh http://YOUR_VPS_IP
# cohost по домену:
./scripts/smoke-deploy.sh http://stratum.example.com
```

---

## Вместе с Klaris (2fromlarec) на одном VPS

См. [`docs/COHOST_KLARIS.md`](COHOST_KLARIS.md).

```bash
# оба на :80, разные server_name; API STRATUM → :8001
sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh
```

## Регуляторика / хостинг РФ

Для ПДн размещайте VPS на территории РФ; не направляйте чувствительные данные во внешние облачные LLM (см. `docs/CONCEPT.md`).
