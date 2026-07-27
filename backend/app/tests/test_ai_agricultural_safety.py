from app.modules.ai.safety import AgriculturalSafetyService


def test_emergency_poisoning_is_identified_before_paid_execution() -> None:
    decision = AgriculturalSafetyService.triage("کودک سم را بلعیده و حالش بد شده")
    assert decision.emergency is True
    assert decision.code == "EMERGENCY_POISONING"
    guidance = AgriculturalSafetyService.emergency_guidance()
    assert "فوراً" in guidance
    assert "استفراغ" in guidance
    assert "برزگر جایگزین درمان فوری نیست" in guidance


def test_high_risk_output_requires_evidence_uncertainty_and_human_review() -> None:
    decision = AgriculturalSafetyService.triage("دوز سمپاشی آفت‌کش را بگو")
    assert decision.code == "HIGH_RISK_CHEMICAL"
    assert (
        AgriculturalSafetyService.validate_output(
            content="این کار را انجام بده",
            safety_code=decision.code,
            citation_count=0,
        ).failure_code
        == "AI_SAFETY_CITATION_REQUIRED"
    )
    assert (
        AgriculturalSafetyService.validate_output(
            content="طبق منبع این مقدار قطعی است",
            safety_code=decision.code,
            citation_count=1,
        ).failure_code
        == "AI_SAFETY_UNCERTAINTY_REQUIRED"
    )
    assert AgriculturalSafetyService.validate_output(
        content="احتمال دارد؛ پیش از اقدام با کارشناس بررسی کنید.",
        safety_code=decision.code,
        citation_count=1,
    ).usable


def test_general_agricultural_answer_is_not_high_risk() -> None:
    decision = AgriculturalSafetyService.triage("بهترین زمان آبیاری گندم چیست؟")
    assert decision.code is None


def test_image_diagnosis_requires_visible_evidence_uncertainty_and_human_review() -> None:
    assert (
        AgriculturalSafetyService.validate_output(
            content="این بیماری قطعی است",
            safety_code="IMAGE_EVIDENCE_GATED",
            citation_count=0,
        ).failure_code
        == "AI_IMAGE_VISIBLE_EVIDENCE_REQUIRED"
    )
    assert AgriculturalSafetyService.validate_output(
        content="در تصویر لکه‌هایی مشاهده می‌شود؛ احتمال بیماری وجود دارد و متخصص باید بررسی کند.",
        safety_code="IMAGE_EVIDENCE_GATED",
        citation_count=0,
    ).usable
