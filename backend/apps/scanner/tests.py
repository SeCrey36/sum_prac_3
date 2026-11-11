from django.test import TestCase
from apps.scanner.pii_rules import (
    find_pii_in_text,
    luhn_checksum,
    validate_inn,
    validate_snils,
    mask_passport,
    mask_phone,
    mask_email,
    mask_bank_card,
)
from apps.scanner.risk_engine import calculate_risk, RISK_LOW, RISK_MEDIUM, RISK_CRITICAL
from apps.scanner.pdf_export import generate_pdf_report


class PIIRulesTestCase(TestCase):
    def test_luhn_checksum(self):
        # Valid test card (Luhn compliant)
        self.assertTrue(luhn_checksum("4532015112830366"))
        # Invalid card
        self.assertFalse(luhn_checksum("4532015112830367"))

    def test_inn_validation(self):
        # Valid 10-digit INN
        self.assertTrue(validate_inn("7707083893"))
        # Invalid INN
        self.assertFalse(validate_inn("1234567890"))

    def test_snils_validation(self):
        # Valid SNILS
        self.assertTrue(validate_snils("11223344595"))

    def test_scanner_detects_all_types(self):
        sample_text = """
        Договор оказания услуг.
        Паспорт гражданина РФ: 45 08 123456, выдан ОВД г. Москвы.
        ИНН клиента: 7707083893.
        СНИЛС: 112-233-445 95.
        Контактный телефон: +7 (999) 123-45-67.
        Email: auditor@security-corp.ru.
        Оплата произведена по карте: 4532 0151 1283 0366.
        """
        findings = find_pii_in_text(sample_text, page_number=1)
        types_found = {f["pii_type"] for f in findings}

        self.assertIn("PASSPORT", types_found)
        self.assertIn("INN", types_found)
        self.assertIn("SNILS", types_found)
        self.assertIn("PHONE", types_found)
        self.assertIn("EMAIL", types_found)
        self.assertIn("BANK_CARD", types_found)

    def test_risk_engine(self):
        # Empty -> LOW
        risk, _, _ = calculate_risk([])
        self.assertEqual(risk, RISK_LOW)

        # Only email -> LOW
        risk, _, _ = calculate_risk([{"pii_type": "EMAIL"}])
        self.assertEqual(risk, RISK_LOW)

        # Single passport -> MEDIUM
        risk, _, _ = calculate_risk([{"pii_type": "PASSPORT"}])
        self.assertEqual(risk, RISK_MEDIUM)

        # Bank card -> CRITICAL
        risk, _, _ = calculate_risk([{"pii_type": "BANK_CARD"}])
        self.assertEqual(risk, RISK_CRITICAL)

        # Passport + SNILS combo -> CRITICAL
        risk, _, _ = calculate_risk([{"pii_type": "PASSPORT"}, {"pii_type": "SNILS"}])
        self.assertEqual(risk, RISK_CRITICAL)

    def test_pdf_report_generation(self):
        findings = [
            {
                "pii_type": "PASSPORT",
                "type_name": "Паспорт РФ",
                "masked_value": "45** ***456",
                "page_number": 1,
                "context": "серия 45 08 номер 123456",
            }
        ]
        pdf_bytes = generate_pdf_report(
            original_filename="test_doc.pdf",
            file_size_bytes=10240,
            uploaded_at_str="10.11.2026 12:00:00",
            risk_level="MEDIUM",
            risk_summary="Обнаружены паспортные данные.",
            findings=findings,
            file_deleted=False,
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 1000)
