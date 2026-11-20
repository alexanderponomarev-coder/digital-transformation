# Полная инструкция по установке на VPS (Debian)

Документ описывает установку **с нуля** на чистый Debian 12+ (bookworm / trixie).

Два сценария:

1. **Только STRATUM** — `:80` + API `:8000` (catch-all `server_name`)
2. **Klaris + STRATUM на одном узле** — оба на **`:80`**, разделение по **доменному имени** (`server_name`); API localhost Klaris `:8000`, STRATUM `:8001`

Автообновление с GitHub (timer + опциональный webhook) — в конце каждого сценария.

---

## 0. Что понадобится

| Требование | Значение |
|------------|----------|
| ОС | Debian 12+ (или Ubuntu 22.04/24.04 для Klaris-скриптов) |
| Доступ | `root` или пользователь с `sudo` |
| Сеть | открыт входящий TCP **80** (и **443** после TLS) |
| DNS (cohost) | два имени → один IP, напр. `klaris.example.com` и `stratum.example.com` |
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

**Приватный** репозиторий — токен в env, затем `git clone` без секрета в argv/`git remote`:

```bash
sudo mkdir -p /etc/stratum
sudo tee /etc/stratum/stratum.env >/dev/null <<'EOF'
STRATUM_REPO_URL=https://github.com/alexanderponomarev-coder/digital-transformation-.git
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GITHUB_TOKEN=ghp_xxxxxxxx
EOF
sudo chmod 640 /etc/stratum/stratum.env

# clone: токен читается из env, в origin остаётся публичный URL
sudo bash -c '
  set -a; source /etc/stratum/stratum.env; set +a
  AUTH="https://x-access-token:${STRATUM_GITHUB_TOKEN}@github.com/${STRATUM_REPO_URL#https://github.com/}"
  git clone --branch "${STRATUM_GIT_BRANCH:-main}" "$AUTH" "${STRATUM_GIT_DIR}"
  git -C "${STRATUM_GIT_DIR}" remote set-url origin "${STRATUM_REPO_URL}"
'
cd /opt/stratum-src
```

После первой установки `enable-auto-update.sh` / `auto-update.sh` сами умеют **клонировать**, если `/opt/stratum-src` ещё нет (нужны `STRATUM_GITHUB_TOKEN` + `STRATUM_REPO_URL` в env) — см. §3.1.

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
STRATUM_SERVER_NAME=_
STRATUM_HTTP_PORT=80
STRATUM_API_PORT=8000
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GIT_REMOTE=origin
```

Для **private** auto-update добавьте `STRATUM_GITHUB_TOKEN` (или deploy key) — см. §3.

---

## 2. Сценарий B — Klaris + STRATUM на одном узле (по доменам)

Оба vhost слушают **`:80`**. Разделение — `server_name` (Host / DNS).

| Приложение | Домен | HTTP | API (localhost) | Проверка |
|------------|-------|------|-----------------|----------|
| **Klaris** | `klaris.example.com` | **80** | **8000** | `http://klaris.example.com/health` |
| **STRATUM** | `stratum.example.com` | **80** | **8001** | `http://stratum.example.com/api/health` |

DNS до установки (или сразу после):

```text
klaris.example.com.   A    VPS_IP
stratum.example.com.  A    VPS_IP
```

Firewall (если ufw):

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
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
# домен Klaris (рекомендуется при cohost):
echo 'KLARIS_SERVER_NAME=klaris.example.com' | sudo tee -a /etc/klaris/klaris.env

sudo -E KLARIS_SERVER_NAME=klaris.example.com bash deploy/debian/install.sh
# на Ubuntu: sudo -E KLARIS_SERVER_NAME=klaris.example.com bash deploy/ubuntu/install.sh
```

Проверка Klaris:

```bash
curl -fsS -H 'Host: klaris.example.com' http://127.0.0.1/health
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
# Webhook URL: https://klaris.example.com/hooks/github
# Secret: KLARIS_WEBHOOK_SECRET в /etc/klaris/klaris.env
```

Подробнее: репозиторий Klaris → `deploy/COHOST_STRATUM.md`, `deploy/debian/README.md`.

### 2.2. Установка STRATUM рядом

`install.sh` при наличии Klaris **требует** `STRATUM_SERVER_NAME` (из env-файла или из команды) и ставит API на `:8001`, HTTP на `:80`.

```bash
sudo git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo git checkout main

# вариант 1 — в команде:
sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh /opt/stratum-src

# вариант 2 — заранее в /etc/stratum/stratum.env:
#   STRATUM_SERVER_NAME=stratum.example.com
# затем:
# sudo bash deploy/debian/install.sh /opt/stratum-src
```

Проверка STRATUM:

```bash
curl -fsS -H 'Host: stratum.example.com' http://127.0.0.1/api/health
curl -fsS -H 'Host: stratum.example.com' -o /dev/null -w "ui:%{http_code}\n" http://127.0.0.1/
sudo systemctl status stratum-api --no-pager
ss -lntp | grep -E ':80 |:8000 |:8001 '
```

Оба сервиса:

```bash
curl -fsS http://klaris.example.com/health
curl -fsS http://stratum.example.com/api/health
```

---

## 3. Автообновление STRATUM с GitHub (в т.ч. private repo)

Нужен git-клон `/opt/stratum-src` и рабочий `git fetch` (публичный репозиторий — без токена; **private — нужен токен или deploy key**).

### 3.1. Private repo — рекомендуемый способ: PAT в `stratum.env`

Токен **не** пишется в `git remote` и не попадает в `.git/config`. `auto-update.sh` подставляет его только на время `git fetch` (как `KLARIS_GITHUB_TOKEN` у Klaris).

**1) Создайте токен в GitHub**

| Тип | Настройки |
|-----|-----------|
| **Fine-grained PAT** (предпочтительно) | Resource owner = владелец репо; Repository access = только `digital-transformation-`; Permissions → **Contents: Read-only** |
| Classic PAT | scope `repo` (полный доступ к private — шире, чем нужно) |

Срок жизни — по политике безопасности; после истечения обновите значение в env.

**2) Пропишите токен и URL в env (до clone)**

```bash
sudo mkdir -p /etc/stratum
sudo tee /etc/stratum/stratum.env >/dev/null <<'EOF'
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
STRATUM_GIT_REMOTE=origin
STRATUM_REPO_URL=https://github.com/alexanderponomarev-coder/digital-transformation-.git
STRATUM_GITHUB_TOKEN=ghp_xxxxxxxx
EOF
sudo chown root:stratum /etc/stratum/stratum.env 2>/dev/null || true
sudo chmod 640 /etc/stratum/stratum.env
```

**3) `git clone` — два способа**

**A. Скрипт сам клонирует** (если `/opt/stratum-src` ещё нет; токен только из env):

```bash
# после install.sh (скрипты уже в /opt/stratum):
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
# или:
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

В логе будет `git clone https://github.com/… → /opt/stratum-src`, затем `origin` **без** токена.

**B. Вручную** (токен из env, не в истории как argv):

```bash
sudo bash -c '
  set -a; source /etc/stratum/stratum.env; set +a
  AUTH="https://x-access-token:${STRATUM_GITHUB_TOKEN}@github.com/${STRATUM_REPO_URL#https://github.com/}"
  git clone --branch "${STRATUM_GIT_BRANCH:-main}" "$AUTH" "${STRATUM_GIT_DIR}"
  git -C "${STRATUM_GIT_DIR}" remote set-url origin "${STRATUM_REPO_URL}"
'
```

Не оставляйте `https://x-access-token:…@…` в `git remote -v`.

**4) Проверка fetch**

```bash
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
sudo git -C /opt/stratum-src remote -v
# origin → https://github.com/...  БЕЗ токена в URL
```

### 3.2. Альтернатива — SSH deploy key (readonly)

Если не хотите PAT:

```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/stratum_deploy -N ""
# Добавьте /root/.ssh/stratum_deploy.pub → GitHub → Repo → Settings → Deploy keys → Allow read access

sudo tee /root/.ssh/config >/dev/null <<'EOF'
Host github.com
  IdentityFile /root/.ssh/stratum_deploy
  IdentitiesOnly yes
EOF
sudo chmod 600 /root/.ssh/config /root/.ssh/stratum_deploy

sudo git -C /opt/stratum-src remote set-url origin \
  git@github.com:alexanderponomarev-coder/digital-transformation-.git
sudo git -C /opt/stratum-src fetch origin
```

При SSH `STRATUM_GITHUB_TOKEN` не нужен. Не смешивайте токенный HTTPS и SSH на одном remote без нужды.

### 3.3. Что не делать

- Не оставляйте `https://x-access-token:…@github.com/…` в `git remote` надолго (токен в `git remote -v`, бэкапах, логах).
- Не коммитьте `stratum.env` / токен в репозиторий.
- Не давайте токену права шире **Contents: Read**, если достаточно auto-update.

### 3.4. Timer (~каждые 5 минут)

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
sudo systemctl list-timers stratum-auto-update.timer --no-pager
sudo journalctl -u stratum-auto-update -n 50 --no-pager
```

Ручной прогон:

```bash
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

Если в логе `hint: private repo — добавьте STRATUM_GITHUB_TOKEN` — вернитесь к §3.1.

### 3.5. Webhook (мгновенно на push в `main`)

Работает и для private: GitHub шлёт событие на ваш URL; на сервере обновление всё равно идёт через `git fetch` с токеном/ключом из §3.1–3.2.

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```

В GitHub → **Settings → Webhooks → Add webhook**:

| Поле | Только STRATUM | Cohost (по домену) |
|------|----------------|---------------------|
| Payload URL | `http://IP/hooks/github` | `https://stratum.example.com/hooks/github` |
| Content type | `application/json` | то же |
| Secret | `STRATUM_WEBHOOK_SECRET` из `/etc/stratum/stratum.env` | то же |
| Events | Just the **push** event | то же |

Проверка:

```bash
curl -fsS http://127.0.0.1:9000/health \
  || curl -fsS -H 'Host: stratum.example.com' http://127.0.0.1/hooks/github/health
sudo systemctl status stratum-webhook --no-pager
```

### 3.6. Чеклист private auto-update

- [ ] `STRATUM_GITHUB_TOKEN` + `STRATUM_REPO_URL` в `/etc/stratum/stratum.env` **или** SSH deploy key
- [ ] клон есть: `/opt/stratum-src/.git` (создал `enable-auto-update` / `auto-update` или ручной clone)
- [ ] `origin` без токена: `git -C /opt/stratum-src remote -v`
- [ ] `sudo bash …/auto-update.sh --force` → успех
- [ ] `stratum-auto-update.timer` active
- [ ] (Опционально) webhook + секрет

---

## 4. HTTPS (стенд / TLS)

После DNS A-записи на IP сервера и рабочего HTTP (`curl -H 'Host: …' http://127.0.0.1/api/health`):

```bash
# рекомендуемый helper (preflight + certbot --nginx + redirect)
sudo bash /opt/stratum/deploy/debian/enable-tls.sh stratum.example.com --email ops@example.com

# или вручную:
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d stratum.example.com

# cohost: отдельный сертификат на каждый server_name
sudo certbot --nginx -d klaris.example.com
sudo bash /opt/stratum/deploy/debian/enable-tls.sh stratum.example.com
```

Стенд `1-web.ru`: см. [P4_STAND.md](P4_STAND.md) (lab vs demo, troubleshooting «безопасное соединение»).

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
ss -lntp | grep -E ':80 |:8000 |:8001 |:9000 |:9001 '
```

Типичные проблемы:

| Симптом | Что проверить |
|---------|----------------|
| `502` / `504` на `/api/` | `systemctl status stratum-api`, порт `STRATUM_API_PORT` совпадает с nginx |
| открывается Klaris вместо STRATUM | Host/DNS: нужен `STRATUM_SERVER_NAME`, curl с `-H 'Host: …'` |
| `git fetch` fails / hint про токен | `STRATUM_GITHUB_TOKEN` в `/etc/stratum/stratum.env` (§3.1) или deploy key (§3.2); `STRATUM_GIT_DIR` |
| токен виден в `git remote -v` | `remote set-url` на публичный HTTPS; токен только в env |
| `ERROR: рядом с Klaris нужен домен` | задайте `STRATUM_SERVER_NAME=stratum.example.com` |
| nginx не стартует | `nginx -t`, два `default_server` на одном порту |
| `nodejs` Conflicts `npm` при apt | Debian `npm` + NodeSource `nodejs` — перезапустите свежий `install.sh` (ставит только NodeSource) или: `sudo apt-get remove -y npm && sudo apt-get install -y nodejs` |
| API не поднимается без systemd | `sudo STRATUM_SERVER_NAME=… bash /opt/stratum/deploy/debian/run-native.sh` |

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

На одном узле с Klaris native Docker на `:80` конфликтует — используйте native cohost по доменам (§2).

---

## 9. Чеклист «готово»

- [ ] `curl` health STRATUM (и Klaris, если cohost) → OK  
- [ ] UI открывается в браузере по своему домену  
- [ ] `/etc/stratum/stratum.env`: `STRATUM_SERVER_NAME` и порты верные  
- [ ] `stratum-auto-update.timer` active (и webhook, если нужен)  
- [ ] Private: `STRATUM_GITHUB_TOKEN` (или deploy key) + `auto-update.sh --force` OK  
- [ ] Shared-стенд: `STRATUM_DEPLOY_MODE=demo` + `STRATUM_API_TOKEN` + `STRATUM_DISABLE_RESET=1` ([P4_STAND.md](P4_STAND.md), [SECURITY.md](SECURITY.md))  
- [ ] TLS: `https://…/api/health` OK / firewall 443 / webhook в GitHub  

Связанные документы: [DEPLOY_DEBIAN.md](DEPLOY_DEBIAN.md), [COHOST_KLARIS.md](COHOST_KLARIS.md), [P4_STAND.md](P4_STAND.md), [CONCEPT.md](CONCEPT.md).
