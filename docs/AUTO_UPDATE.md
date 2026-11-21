# Автообновление с ветки `main`

При пуше/merge в `main` VPS сам подтягивает код, собирает фронт и перезапускает API.

## Каналы

| Канал | Как | Задержка |
|-------|-----|----------|
| **GitHub Webhook** | push → `POST /hooks/github` → `auto-update.sh` | секунды |
| **systemd timer** | polling `git fetch` каждые ~2 мин | до ~2 мин |

Оба включают одной командой.

## Включение на сервере (1-web.ru)

```bash
# 1) актуальные скрипты (если auto-update ещё не тянул этот коммит)
cd /opt/stratum-src && sudo git fetch origin && sudo git checkout main && sudo git pull --ff-only origin main
sudo bash /opt/stratum-src/deploy/debian/update.sh /opt/stratum-src

# 2) timer + webhook
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh

# 3) статус
sudo bash /opt/stratum/deploy/debian/auto-update-status.sh
```

В `/etc/stratum/stratum.env` должно быть:

```bash
STRATUM_GIT_BRANCH=main
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_REPO_URL=https://github.com/alexanderponomarev-coder/digital-transformation-.git
STRATUM_GITHUB_TOKEN=ghp_xxx          # private repo
STRATUM_SERVER_NAME=1-web.ru
STRATUM_WEBHOOK_SECRET=…              # сгенерирует enable-скрипт
```

## GitHub → Webhooks

| Поле | Значение |
|------|----------|
| Payload URL | `https://1-web.ru/hooks/github` |
| Content type | `application/json` |
| Secret | тот же, что `STRATUM_WEBHOOK_SECRET` |
| SSL verify | Enable |
| Events | Just the **push** event |

Скрипт принимает только `refs/heads/main` (или `STRATUM_GIT_BRANCH`).

Проверка доставки:

```bash
curl -fsS http://127.0.0.1:9000/health
curl -fsS https://1-web.ru/hooks/github/health
# в GitHub webhook → Recent deliveries: 202 / ping 200
sudo journalctl -u stratum-webhook -u stratum-auto-update -f
```

## Типичные сбои

| Симптом | Причина | Фикс |
|---------|---------|------|
| `https://…/hooks/github` → **502** | `stratum-webhook` не запущен | `sudo systemctl enable --now stratum-webhook` |
| fetch failed | нет токена / deploy key | `STRATUM_GITHUB_TOKEN` в env |
| webhook 401 | неверный Secret | сверить с `stratum.env` |
| push в другую ветку | ignored_ref | мержить в `main` |
| после certbot пропал `/hooks/github` | certbot переписал server | `sudo bash enable-auto-update.sh` или `python3 …/patch-webhook-nginx.py` |

## Отключить

```bash
sudo systemctl disable --now stratum-webhook
sudo systemctl disable --now stratum-auto-update.timer
```
