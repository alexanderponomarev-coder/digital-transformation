# Один VPS: STRATUM + Klaris (2fromlarec)

> Полный сценарий установки: [INSTALL.md](INSTALL.md) §2.

См. также канон в Klaris: `deploy/COHOST_STRATUM.md` репозитория `alexanderponomarev-coder/2fromlarec`.

## Разделение по доменам (оба на :80)

| | Домен (nginx `server_name`) | HTTP | API (localhost) |
|---|------|------|-----|
| Klaris | `klaris.example.com` (или `_` catch-all) | **80** | **8000** |
| **STRATUM** | **`stratum.example.com`** (обязателен) | **80** | **8001** |

DNS: две A/AAAA-записи на один IP VPS. Публичный порт один — **80** (и 443 после certbot).

## Установка STRATUM рядом с Klaris

```bash
git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```

`/etc/stratum/stratum.env`:

```bash
STRATUM_SERVER_NAME=stratum.example.com
STRATUM_HTTP_PORT=80
STRATUM_API_PORT=8001
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
```

Проверка (по Host или по DNS):

```bash
curl -fsS -H 'Host: stratum.example.com' http://127.0.0.1/api/health
curl -fsS -H 'Host: klaris.example.com' http://127.0.0.1/health
# или:
curl -fsS http://stratum.example.com/api/health
curl -fsS http://klaris.example.com/health
```
