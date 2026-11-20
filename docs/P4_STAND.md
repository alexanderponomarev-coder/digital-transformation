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

1. DNS A/AAAA → IP VPS; порт **80** открыт (для ACME http-01).
2. HTTP уже отвечает по имени:

```bash
curl -fsS -H 'Host: 1-web.ru' http://127.0.0.1/api/health
# или снаружи:
curl -fsS http://1-web.ru/api/health
```

3. Выпуск сертификата:

```bash
sudo bash /opt/stratum/deploy/debian/enable-tls.sh 1-web.ru --email ops@example.com
# или вручную:
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 1-web.ru
```

4. Проверка:

```bash
curl -fsS https://1-web.ru/api/health
echo | openssl s_client -connect 1-web.ru:443 -servername 1-web.ru 2>/dev/null | openssl x509 -noout -dates -subject
```

### «Невозможно установить безопасное соединение»

| Причина | Что сделать |
|---------|-------------|
| Нет сертификата / только :80 | `enable-tls.sh` / certbot |
| DNS ещё не на этот VPS | дождаться пропагации; `dig +short 1-web.ru` |
| Cohost Klaris: чужой cert на :443 | отдельный `server_name` + `certbot -d` **на каждый** домен |
| Смешанный контент / старый HSTS | жёсткий refresh; проверить `X-Forwarded-Proto` в nginx (уже в шаблоне) |
| Firewall режет 443 | `ufw allow 443/tcp` (или security group) |

Обновление: `sudo certbot renew` (timer обычно ставит certbot сам).

## Связанные файлы

- `deploy/debian/enable-tls.sh`
- `deploy/debian/nginx-stratum.conf` (`X-Forwarded-Proto`)
- [INSTALL.md](INSTALL.md) §4, [SECURITY.md](SECURITY.md)
