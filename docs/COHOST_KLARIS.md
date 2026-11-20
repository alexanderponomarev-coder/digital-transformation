# Один VPS: STRATUM + Klaris (2fromlarec)

См. также канон в Klaris: `deploy/COHOST_STRATUM.md` репозитория `alexanderponomarev-coder/2fromlarec`.

## Порты

| | HTTP | API |
|---|------|-----|
| Klaris | 80 | 8000 |
| **STRATUM** | **8080** | **8001** |

## Установка STRATUM рядом с Klaris

```bash
git clone https://github.com/alexanderponomarev-coder/digital-transformation-.git /opt/stratum-src
cd /opt/stratum-src
sudo STRATUM_HTTP_PORT=8080 STRATUM_API_PORT=8001 bash deploy/debian/install.sh
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
# webhook (порт nginx 8080):
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```

`/etc/stratum/stratum.env`:

```bash
STRATUM_HTTP_PORT=8080
STRATUM_API_PORT=8001
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_GIT_BRANCH=main
```

Проверка:

```bash
curl -fsS http://127.0.0.1:8080/api/health
curl -fsS http://127.0.0.1/health   # Klaris
```
