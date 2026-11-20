# Полная инструкция по установке на VPS (Debian)

Документ описывает установку **с нуля** на чистый Debian 12+ (bookworm / trixie).

Два сценария:

1. **Только STRATUM** — занимает порты `:80` и `:8000`
2. **Klaris + STRATUM на одном узле** — Klaris `:80`/`:8000`, STRATUM `:8080`/`:8001` (рекомендуется, если уже есть / будет 2fromlarec)

Автообновление с GitHub (timer + опциональный webhook) — в конце каждого сценария.

---

## 0. Что понадобится

| Требование | Значение |
|------------|----------|
| ОС | Debian 12+ (или Ubuntu 22.04/24.04 для Klaris-скриптов) |
| Доступ | `root` или пользователь с `sudo` |
| Сеть | открыты входящие TCP **80** (и **8080**, если cohost) |
| Репозитории | `alexanderponomarev-coder/digital-transformation-` (STRATUM), опционально `…/2fromlarec` (Klaris) |
| Для private GitHub | Personal Access Token с правом **Contents: Read** (или deploy key) |

Проверка ОС:

```bash
cat /etc/os-release
# ID=debian, VERSION_ID=12 или 13
```

Базовые пакеты:

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates
```

---

## 1. Сценарий A — только STRATUM

### 1.1. Клон репозитория

**Публичный** репозиторий:

```bash
sudo mkdir -p /opt
sudo git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo git checkout main
```

**Приватный** репозиторий (токен не сохраняйте в истории shell — лучше сразу в env-файл после установки):

```bash
# одноразово для clone:
sudo git clone https://x-access-token:ВАШ_ТОКЕН@github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
# убрать токен из remote URL:
sudo git -C /opt/stratum-src remote set-url origin https://github.com/alexanderponomarev-coder/digital-transformation-.git
```

### 1.2. Установка (native, без Docker)

```bash
cd /opt/stratum-src
sudo bash deploy/debian/install.sh /opt/stratum-src
```

Скрипт установит: Python venv, Node (при необходимости), nginx, пользователя `stratum`, соберёт фронт, поднимет `stratum-api` через systemd.

Что появится на диске:

| Путь | Назначение |
|------|------------|
| `/opt/stratum` | рабочая копия + `.venv` |
| `/opt/stratum-src` | git-клон для автообновления |
| `/var/www/stratum` | статика SPA |
| `/etc/stratum/stratum.env` | конфигурация |
| `/etc/systemd/system/stratum-api.service` | API |
| `/etc/nginx/sites-available/stratum` | SPA + proxy `/api` |

### 1.3. Проверка

```bash
sudo systemctl status stratum-api nginx --no-pager
curl -fsS http://127.0.0.1/api/health
curl -fsS -o /dev/null -w "ui:%{http_code}\n" http://127.0.0.1/
curl -fsS -o /dev/null -w "app:%{http_code}\n" http://127.0.0.1/app
curl -fsS -o /dev/null -w "docs:%{http_code}\n" http://127.0.0.1/docs
```

Ожидается: health JSON с `"product":"STRATUM"`, UI/app/docs → `200`.

Откройте в браузере: `http://IP_СЕРВЕРА/` → «Смотреть демо СеверПром».

### 1.4. Конфиг

```bash
sudo nano /etc/stratum/stratum.env
sudo systemctl restart stratum-api
```

Минимальный пример:

```bash
STRATUM_CORS_ORIGINS=*
STRATUM_HTTP_PORT=80
STRATUM_API_PORT=8000
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GIT_REMOTE=origin
```

Для private auto-update добавьте доступ к git (см. §3).

---

## 2. Сценарий B — Klaris + STRATUM на одном узле

Порты без конфликта:

| Приложение | HTTP (nginx) | API (uvicorn) | Проверка |
|------------|--------------|---------------|----------|
| **Klaris** | **80** | **8000** | `http://IP/health` |
| **STRATUM** | **8080** | **8001** | `http://IP:8080/api/health` |

Firewall (если ufw):

```bash
sudo ufw allow 80/tcp
sudo ufw allow 8080/tcp
sudo ufw reload
```

### 2.1. Установка Klaris (2fromlarec)

```bash
sudo git clone https://github.com/alexanderponomarev-coder/2fromlarec.git /opt/klaris-src
# private: используйте x-access-token:TOKEN@… как выше, затем remote set-url без токена
cd /opt/klaris-src
sudo git checkout main

# токен для последующих git fetch (private):
sudo mkdir -p /etc/klaris
echo 'KLARIS_GITHUB_TOKEN=ghp_xxx' | sudo tee -a /etc/klaris/klaris.env
echo 'KLARIS_REPO_URL=https://github.com/alexanderponomarev-coder/2fromlarec.git' | sudo tee -a /etc/klaris/klaris.env
echo 'KLARIS_BRANCH=main' | sudo tee -a /etc/klaris/klaris.env

sudo -E bash deploy/debian/install.sh
# на Ubuntu: sudo -E bash deploy/ubuntu/install.sh
```

Проверка Klaris:

```bash
curl -fsS http://127.0.0.1/health
curl -fsS http://127.0.0.1:8000/health
sudo systemctl status klaris-api nginx --no-pager
```

Допишите LLM-ключи в `/etc/klaris/klaris.env`, затем:

```bash
sudo systemctl restart klaris-api
```

Автообновление Klaris (timer обычно уже включается install; webhook — по желанию):

```bash
sudo bash /opt/klaris/deploy/debian/enable-auto-update.sh
sudo bash /opt/klaris/deploy/debian/enable-auto-update.sh --webhook
# Webhook URL: http://IP/hooks/github
# Secret: KLARIS_WEBHOOK_SECRET в /etc/klaris/klaris.env
```

Подробнее: репозиторий Klaris → `deploy/COHOST_STRATUM.md`, `deploy/debian/README.md`.

### 2.2. Установка STRATUM рядом

```bash
sudo git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo git checkout main

# Явно задайте порты (если Klaris уже стоит, install.sh сам сдвинет на 8080/8001)
sudo STRATUM_HTTP_PORT=8080 STRATUM_API_PORT=8001 bash deploy/debian/install.sh /opt/stratum-src
```

Проверка STRATUM:

```bash
curl -fsS http://127.0.0.1:8080/api/health
curl -fsS -o /dev/null -w "ui:%{http_code}\n" http://127.0.0.1:8080/
sudo systemctl status stratum-api --no-pager
ss -lntp | grep -E ':80 |:8080 |:8000 |:8001 '
```

Оба сервиса:

```bash
curl -fsS http://127.0.0.1/health          # Klaris
curl -fsS http://127.0.0.1:8080/api/health # STRATUM
```

---

## 3. Автообновление STRATUM с GitHub

Нужен git-клон `/opt/stratum-src` с рабочим `git fetch`.

### 3.1. Доступ к private repo

Вариант A — токен только в памяти скрипта через `GIT_ASKPASS` / URL при fetch (предпочтительно не писать токен в `git remote`).

Практичный вариант для VPS — **deploy key** (readonly):

```bash
sudo -u root ssh-keygen -t ed25519 -f /root/.ssh/stratum_deploy -N ""
# Добавьте /root/.ssh/stratum_deploy.pub в GitHub → Repo → Settings → Deploy keys (Read-only)
sudo git -C /opt/stratum-src remote set-url origin git@github.com:alexanderponomarev-coder/digital-transformation-.git
# ~/.ssh/config для root:
# Host github.com
#   IdentityFile /root/.ssh/stratum_deploy
#   IdentitiesOnly yes
sudo git -C /opt/stratum-src fetch origin
```

Вариант B — HTTPS с токеном в helper (не коммитьте `.env` в git):

```bash
# пример (токен живёт только на сервере):
sudo git -C /opt/stratum-src remote set-url origin \
  https://x-access-token:ghp_xxx@github.com/alexanderponomarev-coder/digital-transformation-.git
```

Пропишите в `/etc/stratum/stratum.env`:

```bash
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GIT_REMOTE=origin
```

### 3.2. Timer (~каждые 5 минут)

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
sudo systemctl list-timers stratum-auto-update.timer --no-pager
sudo journalctl -u stratum-auto-update -n 50 --no-pager
```

Ручной прогон:

```bash
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

### 3.3. Webhook (мгновенно на push в `main`)

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```

В GitHub → **Settings → Webhooks → Add webhook**:

| Поле | Только STRATUM | Cohost (рядом с Klaris) |
|------|----------------|-------------------------|
| Payload URL | `http://IP/hooks/github` | `http://IP:8080/hooks/github` |
| Content type | `application/json` | то же |
| Secret | `STRATUM_WEBHOOK_SECRET` из `/etc/stratum/stratum.env` | то же |
| Events | Just the **push** event | то же |

Проверка:

```bash
curl -fsS http://127.0.0.1:9000/health || curl -fsS http://127.0.0.1:8080/hooks/github/health
sudo systemctl status stratum-webhook --no-pager
```

---

## 4. HTTPS (опционально)

После DNS A-записи на IP сервера:

```bash
sudo apt-get install -y certbot python3-certbot-nginx

# только STRATUM на :80
sudo certbot --nginx -d stratum.example.com

# cohost: отдельный server_name для Klaris на :80;
# для STRATUM на :8080 — либо отдельный домен с proxy_pass на 8080, либо TLS-терминация снаружи
```

---

## 5. Обновление и удаление вручную

```bash
# STRATUM
cd /opt/stratum-src && sudo git pull --ff-only
sudo bash /opt/stratum/deploy/debian/update.sh /opt/stratum-src

# полный снос STRATUM (git-клон /opt/stratum-src не удаляется)
sudo bash /opt/stratum/deploy/debian/uninstall.sh

# Klaris
sudo env KLARIS_UPDATE_FORCE=1 bash /opt/klaris/deploy/ubuntu/klaris-update.sh
sudo bash /opt/klaris/deploy/debian/uninstall.sh
```

---

## 6. Логи и диагностика

```bash
# STRATUM
sudo journalctl -u stratum-api -f
sudo journalctl -u stratum-auto-update -n 100 --no-pager
sudo journalctl -u stratum-webhook -n 50 --no-pager
sudo tail -f /var/log/nginx/error.log

# Klaris
sudo journalctl -u klaris-api -f
sudo bash /opt/klaris/deploy/ubuntu/doctor.sh --no-restart

# порты
ss -lntp | grep -E ':80 |:8080 |:8000 |:8001 |:9000 |:9001 '
```

Типичные проблемы:

| Симптом | Что проверить |
|---------|----------------|
| `502` / `504` на `/api/` | `systemctl status stratum-api`, порт `STRATUM_API_PORT` совпадает с nginx |
| `git fetch` fails | токен / deploy key, `STRATUM_GIT_DIR` |
| конфликт порта 80 | Klaris уже слушает 80 → ставьте STRATUM на 8080 |
| nginx не стартует | `nginx -t`, два `default_server` на одном порту |
| API не поднимается без systemd | `sudo bash /opt/stratum/deploy/debian/run-native.sh 8080` |

---

## 7. Локальная разработка (не VPS)

```bash
git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git
cd digital-transformation-
make install
make api    # :8000
make web    # :5173
make test
```

UI: http://127.0.0.1:5173 · API docs: http://127.0.0.1:8000/docs

---

## 8. Docker Compose (альтернатива, только STRATUM)

```bash
cd /opt/stratum-src
sudo bash deploy/debian/install-docker.sh
# или:
cp .env.example .env
# STRATUM_HTTP_PORT=80
sudo docker compose up -d --build
curl -fsS http://127.0.0.1/api/health
```

На одном узле с Klaris native Docker на `:80` конфликтует — используйте native cohost (§2) или другой `STRATUM_HTTP_PORT`.

---

## 9. Чеклист «готово»

- [ ] `curl` health STRATUM (и Klaris, если cohost) → OK  
- [ ] UI открывается в браузере  
- [ ] `/etc/stratum/stratum.env` заполнен, порты верные  
- [ ] `stratum-auto-update.timer` active (и webhook, если нужен)  
- [ ] Private git: `sudo git -C /opt/stratum-src fetch` проходит  
- [ ] (Опционально) TLS / firewall / webhook в GitHub  

Связанные документы: [DEPLOY_DEBIAN.md](DEPLOY_DEBIAN.md), [COHOST_KLARIS.md](COHOST_KLARIS.md), [CONCEPT.md](CONCEPT.md).
