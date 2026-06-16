from fastapi.testclient import TestClient

from app.main import app


def test_prescription_analysis_returns_safety_rule_findings() -> None:
    client = TestClient(app)

    response = client.post(
        "/prescriptions/analyze-text",
        json={"raw_text": "Medication: Ibuprofen. Directions: Take as directed."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pharmacist_review_required"] is True
    assert "safety_findings" in payload
    rule_ids = {finding["rule_id"] for finding in payload["safety_findings"]}
    assert "missing_dose" in rule_ids
    assert "pharmacist_review_required" in rule_ids
    assert all(
        finding["patient_facing_allowed"] is False
        for finding in payload["safety_findings"]
    )
