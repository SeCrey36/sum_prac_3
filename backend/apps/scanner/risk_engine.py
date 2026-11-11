from typing import List, Dict, Any, Tuple


RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_CRITICAL = "CRITICAL"

RISK_LABELS = {
    RISK_LOW: "Низкий",
    RISK_MEDIUM: "Средний",
    RISK_CRITICAL: "Критический",
}


def calculate_risk(findings: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, int]]:
    """
    Evaluates the overall risk level of the document based on the types and frequency of PII found.
    Returns: (risk_level, risk_summary, type_counts)
    """
    type_counts: Dict[str, int] = {}
    for f in findings:
        t = f["pii_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    total_findings = len(findings)
    has_card = type_counts.get("BANK_CARD", 0) > 0
    has_passport = type_counts.get("PASSPORT", 0) > 0
    has_snils = type_counts.get("SNILS", 0) > 0
    has_inn = type_counts.get("INN", 0) > 0
    has_identity_combo = has_passport and (has_snils or has_inn)

    if total_findings == 0:
        return RISK_LOW, "Персональные данные не обнаружены.", type_counts

    # Critical risk conditions
    if has_card:
        return (
            RISK_CRITICAL,
            "Обнаружены платёжные реквизиты (номера банковских карт). Высокий финансовый риск компрометации.",
            type_counts,
        )
    if has_identity_combo:
        return (
            RISK_CRITICAL,
            "Обнаружена критическая комбинация данных (Паспорт + СНИЛС/ИНН), достаточная для кражи личности или мошеннических действий.",
            type_counts,
        )
    if (type_counts.get("PASSPORT", 0) + type_counts.get("SNILS", 0) + type_counts.get("INN", 0)) >= 3:
        return (
            RISK_CRITICAL,
            "Высокая концентрация паспортных данных и идентификаторов личности в документе.",
            type_counts,
        )

    # Medium risk conditions
    if has_passport or has_snils or has_inn:
        return (
            RISK_MEDIUM,
            "Обнаружены государственные идентификаторы личности (паспорт, СНИЛС или ИНН). Требуется ограничение доступа.",
            type_counts,
        )
    if total_findings > 3:
        return (
            RISK_MEDIUM,
            f"Обнаружено несколько контактов ({total_findings} находок: телефоны/email). Умеренный риск раскрытия контактных данных.",
            type_counts,
        )

    # Low risk
    return (
        RISK_LOW,
        "Обнаружены единичные открытые контактные данные (телефон или e-mail). Минимальный уровень угрозы.",
        type_counts,
    )
