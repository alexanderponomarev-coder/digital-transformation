# Автообновление с ветки `main`

VPS каждые **~2 минуты** делает `git fetch` ветки `main`; при новом коммите — `update.sh` (pip, сборка фронта, restart API).

Webhook **не нужен** (по умолчанию выключен).

## Включение на сервере (1-web.ru)

```bash
# один раз подтянуть скрипты, если ещё нет этого коммита
cd /opt/stratum-src && sudo git fetch origin && sudo git checkout main && sudo git pull --ff-only origin main
sudo bash /opt/stratum-src/deploy/debian/update.sh /opt/stratum-src

# timer ~2 мин
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh
sudo bash /opt/stratum/deploy/debian/auto-update-status.sh
```

В `/etc/stratum/stratum.env`:

```bash
STRATUM_GIT_BRANCH=main
STRATUM_GIT_DIR=/opt/stratum-src
STRATUM_REPO_URL=https://github.com/alexanderponomarev-coder/digital-transformation-.git
STRATUM_GITHUB_TOKEN=ghp_xxx   # для private repo
STRATUM_AUTO_UPDATE=1
```

## Проверка

```bash
systemctl list-timers stratum-auto-update.timer --no-pager
sudo journalctl -u stratum-auto-update -f
# ручной прогон:
sudo bash /opt/stratum/deploy/debian/auto-update.sh --force
```

## Отключить

```bash
sudo systemctl disable --now stratum-auto-update.timer
```

## Опционально: webhook

Только если нужен push без ожидания timer:

```bash
sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh --webhook
```
