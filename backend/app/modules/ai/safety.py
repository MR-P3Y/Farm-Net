from dataclasses import dataclass


EMERGENCY_TERMS = ("مسموم", "بلعیده", "تنفس سم", "تماس با سم", "سوختگی شیمیایی")
HIGH_RISK_TERMS = (
    "سمپاش",
    "سم پاش",
    "آفت کش",
    "آفت‌کش",
    "حشره کش",
    "حشره‌کش",
    "قارچ کش",
    "قارچ‌کش",
    "علف کش",
    "علف‌کش",
    "دوز سم",
)
UNCERTAINTY_MARKERS = ("ممکن", "احتمال", "عدم قطعیت", "اطلاعات کافی")
HUMAN_MARKERS = ("کارشناس", "مشاور", "متخصص")


@dataclass(frozen=True)
class AISafetyDecision:
    code: str | None
    emergency: bool
    requires_citations: bool
    requires_human_escalation: bool


@dataclass(frozen=True)
class AIOutputValidation:
    usable: bool
    failure_code: str | None = None


class AgriculturalSafetyService:
    @staticmethod
    def triage(content: str) -> AISafetyDecision:
        normalized = " ".join(content.casefold().split())
        if any(term in normalized for term in EMERGENCY_TERMS):
            return AISafetyDecision("EMERGENCY_POISONING", True, False, True)
        if any(term in normalized for term in HIGH_RISK_TERMS):
            return AISafetyDecision("HIGH_RISK_CHEMICAL", False, True, True)
        return AISafetyDecision(None, False, False, False)

    @staticmethod
    def emergency_guidance() -> str:
        return (
            "این وضعیت می‌تواند فوری و خطرناک باشد. تماس با ماده را متوقف کنید، "
            "بدون دستور متخصص فرد را وادار به استفراغ نکنید، برچسب یا بسته ماده را "
            "همراه نگه دارید و فوراً با خدمات اورژانسی یا مرکز درمانی/مسمومیت محلی "
            "تماس بگیرید. برزگر جایگزین درمان فوری نیست."
        )

    @staticmethod
    def validate_output(
        *, content: str, safety_code: str | None, citation_count: int
    ) -> AIOutputValidation:
        output = content.strip()
        if not output:
            return AIOutputValidation(False, "AI_EMPTY_OUTPUT")
        if safety_code != "HIGH_RISK_CHEMICAL":
            return AIOutputValidation(True)
        if citation_count < 1:
            return AIOutputValidation(False, "AI_SAFETY_CITATION_REQUIRED")
        if not any(marker in output for marker in UNCERTAINTY_MARKERS):
            return AIOutputValidation(False, "AI_SAFETY_UNCERTAINTY_REQUIRED")
        if not any(marker in output for marker in HUMAN_MARKERS):
            return AIOutputValidation(False, "AI_SAFETY_HUMAN_REVIEW_REQUIRED")
        return AIOutputValidation(True)
