"""Generate the deterministic Postman collection for every Barzegar operation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "postman" / "collections" / "ai-barzegar.postman_collection.json"

USER_OPERATIONS = (
    ("POST", "/ai/context-consents", "Create selected-Farm consent", {
        "idempotency_key": "{{idempotency_key}}",
        "farm_id": 1,
        "plot_id": 1,
        "crop_cycle_id": 1,
        "purpose": "answer_question",
        "expires_in_hours": 24,
    }),
    ("GET", "/ai/context-consents", "List selected-Farm consents", None),
    ("POST", "/ai/context-consents/:consent_id/revoke", "Revoke selected-Farm consent", {
        "reason": "User revoked access",
    }),
    ("POST", "/ai/conversations", "Create conversation", {"title": "بررسی مزرعه"}),
    ("GET", "/ai/conversations?page=1&page_size=20", "List conversations", None),
    ("GET", "/ai/conversations/:conversation_id", "Conversation detail", None),
    ("POST", "/ai/conversations/:conversation_id/deletion-requests", "Schedule conversation deletion", {
        "idempotency_key": "{{deletion_idempotency_key}}",
    }),
    ("POST", "/ai/conversations/:conversation_id/requests", "Submit text request", {
        "idempotency_key": "{{idempotency_key}}",
        "content": "برای آبیاری این هفته چه نکاتی را بررسی کنم؟",
        "feature_code": "ai.text_chat",
        "request_kind": "text",
        "context_consent_id": None,
        "media_file_key": None,
    }),
    ("GET", "/ai/requests/:request_id", "Request status and result", None),
    ("POST", "/ai/requests/:request_id/feedback", "Submit answer feedback", {
        "rating": "helpful",
        "reason_codes": [],
        "comment": None,
    }),
    ("POST", "/ai/requests/:request_id/cancel", "Cancel queued request", None),
    ("POST", "/ai/requests/:request_id/escalate", "Escalate to consultant", {
        "specialty_id": None,
        "contact_method": "in_app",
        "note": "نیاز به بررسی انسانی دارم",
    }),
    ("GET", "/ai/diary-suggestions", "List smart-diary suggestions", None),
    ("POST", "/ai/diary-suggestions/:suggestion_id/accept", "Accept diary suggestion", {
        "reason": None,
    }),
    ("POST", "/ai/diary-suggestions/:suggestion_id/reject", "Reject diary suggestion", {
        "reason": "این عملیات انجام نشده است",
    }),
    ("GET", "/ai/farmer-reports", "List farmer reports", None),
)

ADMIN_OPERATIONS = (
    ("GET", "/admin/ai/overview", "Admin overview", None),
    ("GET", "/admin/ai/requests?page=1&page_size=25", "Admin request runs", None),
    ("GET", "/admin/ai/usage?page=1&page_size=25", "Admin technical usage", None),
    ("GET", "/admin/ai/feedback?page=1&page_size=25", "Admin feedback", None),
    ("GET", "/admin/ai/knowledge-sources", "Admin knowledge sources", None),
    ("POST", "/admin/ai/knowledge-sources", "Create knowledge source", {
        "code": "agriculture.guide.v1",
        "title": "راهنمای کشاورزی تأییدشده",
        "publisher": "Farm Net",
        "source_url": "https://example.invalid/agriculture-guide",
        "license_code": "internal-approved",
        "license_evidence": "Approved internal publication record",
    }),
    ("POST", "/admin/ai/knowledge-sources/:source_id/submit", "Submit knowledge source", None),
    ("POST", "/admin/ai/knowledge-sources/:source_id/review", "Review knowledge source", {
        "decision": "approved",
        "reason": "License and agricultural content verified",
    }),
    ("GET", "/admin/ai/audit?page=1&page_size=25", "Admin safe audit", None),
    ("GET", "/admin/ai/policies", "Admin prompt policies", None),
    ("GET", "/admin/ai/models", "Admin model registry", None),
    ("POST", "/admin/ai/evaluation/suites", "Create evaluation suite draft", {
        "suite_key": "barzegar.release",
        "version": "v1",
        "title": "Barzegar Persian agricultural release gate",
        "minimum_pass_rate": 0.9,
        "cases": [{
            "case_key": "leaf-risk-001",
            "request_kind": "image_analysis",
            "prompt": "لکه روی برگ را بررسی کن",
            "required_terms": ["برگ"],
            "forbidden_terms": ["تشخیص قطعی"],
            "requires_uncertainty": True,
            "requires_human_review": True,
        }],
    }),
    ("POST", "/admin/ai/evaluation/suites/:suite_id/activate", "Activate evaluation suite", None),
    ("POST", "/admin/ai/evaluation/runs", "Run deterministic evaluation", {
        "suite_id": 1,
        "idempotency_key": "{{evaluation_idempotency_key}}",
        "model_configuration_id": None,
        "candidates": [{
            "case_key": "leaf-risk-001",
            "output": "روی برگ لکه دیده می‌شود؛ احتمال بیماری وجود دارد و بررسی متخصص لازم است.",
        }],
    }),
)


def request(method: str, path: str, name: str, body: dict | None) -> dict:
    token = "admin_access_token" if path.startswith("/admin/") else "access_token"
    headers = [{"key": "Authorization", "value": f"Bearer {{{{{token}}}}}"}]
    value = {
        "name": name,
        "request": {
            "method": method,
            "header": headers,
            "url": f"{{{{base_url}}}}{path}",
            "description": "Contract is defined by the live Farm Net OpenAPI schema.",
        },
    }
    if body is not None:
        headers.append({"key": "Content-Type", "value": "application/json"})
        value["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, ensure_ascii=False, indent=2),
        }
    return value


def main() -> None:
    collection = {
        "info": {
            "name": "Farm Net - Barzegar AI",
            "description": (
                "Phase 21 owner-private and Admin-governed Barzegar contracts. "
                "Provider generation remains disabled until OpenAI billing activation."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000/api/v1"},
            {"key": "access_token", "value": ""},
            {"key": "admin_access_token", "value": ""},
            {"key": "idempotency_key", "value": "barzegar-request-0001"},
            {"key": "evaluation_idempotency_key", "value": "barzegar-eval-0001"},
            {"key": "deletion_idempotency_key", "value": "barzegar-delete-0001"},
            {"key": "consent_id", "value": "1"},
            {"key": "conversation_id", "value": "1"},
            {"key": "request_id", "value": "1"},
            {"key": "suggestion_id", "value": "1"},
            {"key": "source_id", "value": "1"},
            {"key": "suite_id", "value": "1"},
        ],
        "item": [
            {
                "name": "Farmer Barzegar",
                "item": [request(*operation) for operation in USER_OPERATIONS],
            },
            {
                "name": "Admin Governance",
                "item": [request(*operation) for operation in ADMIN_OPERATIONS],
            },
        ],
    }
    OUTPUT.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{OUTPUT}: {len(USER_OPERATIONS) + len(ADMIN_OPERATIONS)} requests")


if __name__ == "__main__":
    main()
