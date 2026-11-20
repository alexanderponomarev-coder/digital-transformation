# Доступ и ACL (P0)

## Bearer-токен

| Режим | `STRATUM_API_TOKEN` | Поведение |
|-------|---------------------|-----------|
| Lab / local | пусто | API открыт; ACL по заголовку `X-Stratum-User` всё равно работает |
| Shared / VPS | задан | Все `/api/*` кроме `/api/health` требуют `Authorization: Bearer <token>` |

Сброс демо:

```bash
STRATUM_DISABLE_RESET=1   # POST /api/reset → 403 (рекомендуется на 1-web.ru)
```

## Идентичность для ACL

Заголовок `X-Stratum-User: alice` (если токен включён и заголовок пуст → `operator`).

Правила документа:

- `acl_readers == []` — читают все (после auth, если включён)
- иначе — только `owner_id` и пользователи из `acl_readers`
- после отзыва A не видит документ в snapshot / GET (ответ **404**, без утечки существования)

## UI

```js
sessionStorage.setItem('STRATUM_API_TOKEN', '…')
sessionStorage.setItem('STRATUM_USER', 'alice')
location.reload()
```

Либо `VITE_STRATUM_API_TOKEN` / `VITE_STRATUM_USER` на этапе `npm run build`.

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| PATCH | `/api/documents/{id}/acl` | смена `acl_readers` / `owner_id` (только владелец) |
| GET | `/api/documents/{id}` | документ + facts при праве чтения |
