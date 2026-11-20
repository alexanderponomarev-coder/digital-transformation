# Публикация STRATUM на VPS Debian

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

Другой порт (например 8080):

```bash
sudo STRATUM_HTTP_PORT=8080 bash deploy/debian/install.sh
```

Если на хосте **нет systemd** (редко на VPS, бывает в контейнерах):

```bash
sudo bash deploy/debian/install.sh
sudo bash deploy/debian/run-native.sh 8080
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
# native на нестандартном порту:
./scripts/smoke-deploy.sh http://YOUR_VPS_IP:8080
```

---

## Регуляторика / хостинг РФ

Для ПДн размещайте VPS на территории РФ; не направляйте чувствительные данные во внешние облачные LLM (см. `docs/CONCEPT.md`).
