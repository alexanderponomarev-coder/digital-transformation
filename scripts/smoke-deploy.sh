#!/usr/bin/env bash
# Локальный smoke: pytest + frontend build + API health against running stack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="${1:-http://127.0.0.1:8000}"

echo "== pytest =="
# shellcheck disable=SC1091
source "${ROOT}/.venv/bin/activate"
cd "${ROOT}/backend"
pytest -q

echo "== frontend build =="
cd "${ROOT}/frontend"
npm run build

echo "== API health (${BASE_URL}) =="
curl -fsS "${BASE_URL}/api/health" | tee /tmp/stratum-health.json
echo
python3 - <<'PY'
import json
data = json.load(open("/tmp/stratum-health.json"))
assert data.get("product") == "STRATUM", data
assert data.get("status") == "ok", data
print("health ok")
PY

echo "== snapshot =="
curl -fsS "${BASE_URL}/api/overview" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['company_name']=='СеверПром'; print('overview ok', d['version'])"

echo "SMOKE PASSED"
