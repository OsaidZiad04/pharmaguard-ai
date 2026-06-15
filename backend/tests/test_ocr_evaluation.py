from app.ocr.evaluation import (
    character_error_rate,
    load_ocr_eval_cases,
    medication_detection_hit,
    privacy_warning_match,
    run_ocr_evaluation,
    token_overlap_score,
    word_error_rate,
)


def test_character_error_rate_exact_and_noisy_text() -> None:
    assert character_error_rate("Paracetamol", "Paracetamol") == 0.0
    assert character_error_rate("Paracetamol", "Paracetmol") > 0


def test_word_error_rate_exact_and_noisy_text() -> None:
    assert word_error_rate("rx paracetamol tablets", "rx paracetamol tablets") == 0.0
    assert word_error_rate("rx paracetamol tablets", "rx paracetmol tabiets") > 0


def test_token_overlap_score_is_deterministic() -> None:
    first = token_overlap_score("rx paracetamol tablets", "rx paracetmol tablets")
    second = token_overlap_score("rx paracetamol tablets", "rx paracetmol tablets")

    assert first == second
    assert 0 < first < 1


def test_medication_detection_hit_checks_expected_terms() -> None:
    assert medication_detection_hit(["paracetamol"], "Rx: Paracetamol tablets.")
    assert medication_detection_hit(["xyzmed"], "Rx: Xyzmed tablets.")
    assert medication_detection_hit([], "No medication readable.")
    assert not medication_detection_hit(["ibuprofen"], "Rx: Paracetamol tablets.")


def test_privacy_warning_match_uses_identifier_categories() -> None:
    assert privacy_warning_match(["patient_name_label"], ["patient_name_label"])
    assert not privacy_warning_match(["patient_name_label"], ["clinic_label"])


def test_ocr_evaluation_dataset_and_runner_pass() -> None:
    cases = load_ocr_eval_cases()
    report = run_ocr_evaluation()

    assert len(cases) >= 10
    assert len(cases) >= 18
    assert report["total_cases"] == len(cases)
    assert report["fixture_backed_cases"] >= 10
    assert report["text_only_cases"] + report["fixture_backed_cases"] == len(cases)
    assert "synthetic_fixture_phase_2c" in report["provider_used"]
    assert report["failed_cases"] == 0
    assert report["medication_detection_summary"]["failed"] == 0
    assert report["privacy_warning_summary"]["failed"] == 0
    assert report["quality_gate_summary"]["failed"] == 0
    assert "mock_ocr_phase_2a" in report["provider_summaries"]
    assert "synthetic_fixture_phase_2c" in report["provider_summaries"]
