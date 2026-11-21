#!/usr/bin/env python3
"""Полный демо-прогон цикла STRATUM на синтетическом корпусе СеверПром.

Запуск из корня репо:
  PYTHONPATH=backend python scripts/run_demo_cycle.py
  PYTHONPATH=backend python scripts/run_demo_cycle.py --write-snapshot
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.store import store  # noqa: E402


def _banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


def run_cycle(*, write_snapshot: bool) -> dict:
    store.reset()
    client = TestClient(app)
    report: dict = {"edition": "demo", "steps": []}

    def step(name: str, ok: bool, detail: dict | str | None = None) -> None:
        entry = {"step": name, "ok": ok}
        if detail is not None:
            entry["detail"] = detail
        report["steps"].append(entry)
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark}] {name}" + (f" — {detail}" if isinstance(detail, str) else ""))

    _banner("1. Health / демо-метка")
    health = client.get("/api/health").json()
    step(
        "health.demo",
        health.get("demo") is True and health.get("edition") == "demo",
        health.get("demo_label", ""),
    )

    _banner("2. Snapshot / объём корпуса")
    snap = client.get("/api/snapshot").json()
    ov = snap["overview"]
    counts = {
        "documents": len(snap["documents"]),
        "facts": len(snap["facts"]),
        "questions": len(snap["questions"]),
        "insights": len(snap["insights"]),
        "opportunities": len(snap["opportunities"]),
        "roadmap": len(snap["roadmap"]),
        "nodes": len(snap["model_nodes"]),
        "coverage_layers": len(snap["coverage"]),
    }
    report["corpus"] = counts
    report["overview"] = {
        "project": ov["project_name"],
        "company": ov["company_name"],
        "version": ov["version"],
        "is_demo": ov.get("is_demo"),
        "overall_coverage": ov["overall_coverage"],
    }
    step(
        "corpus.rich",
        counts["documents"] >= 20 and counts["facts"] >= 25 and ov.get("is_demo") is True,
        counts,
    )

    _banner("3. Upload документа (ingest)")
    up = client.post(
        "/api/documents/upload",
        json={
            "title": "[ДЕМО] Журнал пилота OTC — неделя 1",
            "format": "xlsx",
            "summary": "очередь кредит SLA HITL precision рекомендации процессы",
            "content_hint": "otc pilot week1 synthetic",
        },
    )
    step("documents.upload", up.status_code == 200, f"status={up.status_code}")

    _banner("4. Version conflict + confirm")
    up2 = client.post(
        "/api/documents/upload",
        json={
            "title": "[ДЕМО] Журнал пилота OTC — неделя 1",
            "format": "xlsx",
            "summary": "очередь кредит SLA обновление week1 v2",
            "content_hint": "otc pilot week1 v2",
        },
    )
    ok_conflict = up2.status_code == 200
    new_id = None
    if ok_conflict:
        new_id = up2.json()["document"]["id"]
        conf = client.post(f"/api/documents/{new_id}/confirm-version", json={})
        ok_conflict = conf.status_code == 200
    step("documents.version_confirm", ok_conflict, new_id or "no id")

    _banner("5. Ответ на открытый вопрос")
    open_q = next((q for q in snap["questions"] if q["status"] == "open"), None)
    if open_q:
        ans = client.post(
            f"/api/questions/{open_q['id']}/answer",
            json={"answer": "[ДЕМО] Порог серой зоны для авто-рекомендации — 5% с HITL."},
        )
        step("questions.answer", ans.status_code == 200, open_q["id"])
    else:
        step("questions.answer", False, "нет открытых вопросов")

    _banner("6. Утверждение инсайта")
    pending = next(
        (i for i in snap["insights"] if i["approval"] == "pending"),
        None,
    )
    if pending:
        appr = client.post(
            f"/api/insights/{pending['id']}/approval",
            json={"status": "approved"},
        )
        step("insights.approve", appr.status_code == 200, pending["id"])
    else:
        step("insights.approve", True, "нет pending — пропуск")

    _banner("7. AS-IS / TO-BE")
    as_is = client.get("/api/model/as-is")
    to_be = client.get("/api/model/to-be")
    step(
        "model.as_is_to_be",
        as_is.status_code == 200 and to_be.status_code == 200,
        {
            "as_is_layers": as_is.json().get("layers_ready"),
            "to_be_keys": list(to_be.json().keys())[:6],
        },
    )

    _banner("8. Regulatory screen")
    screen = client.post(
        "/api/regulatory/screen",
        json={
            "id": "opp-demo-screen",
            "title": "[ДЕМО] Авто-write лимита",
            "process": "OTC",
            "autonomy_level": 5,
            "impact": "high",
            "effort": "high",
            "regulatory_flags": ["деньги"],
            "admissible": True,
        },
    )
    step(
        "regulatory.screen",
        screen.status_code == 200 and screen.json().get("admissible") is False,
        f"admissible={screen.json().get('admissible')}",
    )

    _banner("9. ROI compute")
    roi = client.post(
        "/api/roi/compute",
        json={
            "investment": 4_500_000,
            "benefits": [
                {
                    "id": "b-kb",
                    "description": "KB review agent",
                    "opportunity_id": "opp-5",
                    "hours_per_year": 900,
                    "hourly_rate": 2400,
                    "process_step_id": "service.kb_review",
                },
                {
                    "id": "b-wms",
                    "description": "WMS adjust",
                    "opportunity_id": "opp-6",
                    "hours_per_year": 1400,
                    "hourly_rate": 2100,
                    "process_step_id": "wms.adjust",
                },
            ],
        },
    )
    step(
        "roi.compute",
        roi.status_code == 200 and roi.json().get("kind") in {"calculated", "hours_only", "blocked"},
        f"kind={roi.json().get('kind')} monetary={roi.json().get('monetary_roi')}",
    )

    _banner("10. Compare alternatives")
    cmp = client.post("/api/compare/alternatives", json={})
    step(
        "compare.alternatives",
        cmp.status_code == 200 and len(cmp.json().get("cases", [])) >= 1,
        cmp.json().get("summary", "")[:120],
    )

    _banner("11. Maturity")
    mat = client.get("/api/maturity")
    matrix = client.get("/api/maturity/matrix")
    step(
        "maturity.read",
        mat.status_code == 200 and matrix.status_code == 200,
        f"system_level={mat.json().get('system_level')} mode={mat.json().get('max_operating_mode')}",
    )

    _banner("12. Audit log")
    audit = client.get("/api/audit/runs?limit=50")
    actions = [e["action"] for e in audit.json()] if audit.status_code == 200 else []
    step(
        "audit.runs",
        audit.status_code == 200 and "compare.alternatives" in actions and "roi.compute" in actions,
        f"events={len(actions)}",
    )

    final = client.get("/api/snapshot").json()
    report["final_overview"] = {
        "open_questions": final["overview"]["open_questions_count"],
        "approved_insights": final["overview"]["approved_insights_count"],
        "overall_coverage": final["overview"]["overall_coverage"],
        "documents": len(final["documents"]),
        "facts": len(final["facts"]),
    }
    report["all_ok"] = all(s["ok"] for s in report["steps"])

    if write_snapshot:
        # Fresh seed snapshot for static frontend fallback (без мутаций цикла)
        store.reset()
        clean = client.get("/api/snapshot").json()
        out = ROOT / "frontend" / "public" / "demo-snapshot.json"
        out.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["snapshot_path"] = str(out)
        print(f"\nWrote {out}")

    _banner("ИТОГ")
    print(json.dumps({"all_ok": report["all_ok"], "corpus": report["corpus"], "final": report["final_overview"]}, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="STRATUM demo full-cycle run")
    parser.add_argument(
        "--write-snapshot",
        action="store_true",
        help="Rewrite frontend/public/demo-snapshot.json from clean seed",
    )
    args = parser.parse_args()
    print("STRATUM · ДЕМО-ВЕРСИЯ · полный цикл на синтетике СеверПром")
    report = run_cycle(write_snapshot=args.write_snapshot)
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
