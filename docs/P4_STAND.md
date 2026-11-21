# P4 — стенд: lab vs demo и TLS

## Режимы

| `STRATUM_DEPLOY_MODE` | Назначение | Рекомендации |
|----------------------|------------|--------------|
| `lab` (по умолчанию) | продукт-лаборатория, локалка, открытый API | `STRATUM_API_TOKEN` пуст, reset разрешён |
| `demo` | shared-стенд (напр. `1-web.ru`) | токен + `STRATUM_DISABLE_RESET=1` |

`GET /api/health` (без auth) отдаёт:

```json
{
  "status": "ok",
  "deploy_mode": "demo",
  "persistence": "in_memory",
  "auth_enabled": true,
  "reset_disabled": true,
  "disclaimer": "Данные только в RAM…"
}
```

В `overview` snapshot те же поля: `deploy_mode`, `persistence`, `storage_disclaimer`.

**Персистентности нет:** in-memory store — бэкап не нужен и не делается. UI показывает дисклеймер.

Пример `/etc/stratum/stratum.env` для demo:

```bash
STRATUM_DEPLOY_MODE=demo
STRATUM_API_TOKEN=change-me-long-random
STRATUM_DISABLE_RESET=1
STRATUM_SERVER_NAME=1-web.ru
STRATUM_CORS_ORIGINS=https://1-web.ru
```

После правки env: `sudo systemctl restart stratum-api`.

## TLS на стенде (`1-web.ru`)

### Важно (cohost с Klaris)

Если на `:443` есть только cert `klaris.1-web.ru`, браузер на `https://1-web.ru` показывает ошибку сертификата и может открыть **Klaris**.

`update.sh` / auto-update раньше затирал SSL-блок STRATUM. Теперь `render_stratum_nginx.py` **сохраняет** LE-cert для `STRATUM_SERVER_NAME` при каждом обновлении.

1. DNS A/AAAA → IP VPS; порт **80** открыт (для ACME http-01).
2. Выпуск / восстановление:

```bash
cd /opt/stratum-src && sudo git pull --ff-only origin main
sudo bash /opt/stratum-src/deploy/debian/update.sh /opt/stratum-src
sudo bash /opt/stratum/deploy/debian/enable-tls.sh 1-web.ru --email ops@example.com
```

3. Проверка (должно быть STRATUM, CN=`1-web.ru`):

```bash
echo | openssl s_client -connect 1-web.ru:443 -servername 1-web.ru 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName
curl -fsS https://1-web.ru/api/health   # product=STRATUM
curl -fsS https://klaris.1-web.ru/health  # app=Klaris
sudo nginx -T 2>/dev/null | grep -E 'server_name|listen .*443|ssl_certificate'
```

### «Невозможно установить безопасное соединение» / открывается Klaris

| Причина | Что сделать |
|---------|-------------|
| Cert только на `klaris.1-web.ru` | `enable-tls.sh 1-web.ru` |
| После auto-update пропал SSL STRATUM | обновить код (≥ этот фикс) + снова `enable-tls.sh` |
| DNS / HSTS | `dig +short 1-web.ru`; жёсткий refresh |
| Firewall режет 443 | `ufw allow 443/tcp` |

Обновление cert: `sudo certbot renew` (nginx конфиг STRATUM пересоберёт `update.sh` с тем же cert).

## Связанные файлы

- `deploy/debian/enable-tls.sh`
- `deploy/debian/nginx-stratum.conf` (`X-Forwarded-Proto`)
- [INSTALL.md](INSTALL.md) §4, [SECURITY.md](SECURITY.md)
