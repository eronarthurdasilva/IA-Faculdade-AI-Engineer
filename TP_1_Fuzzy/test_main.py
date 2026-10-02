import re
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from main import (
    _evaluate_violet_vitality,
    calculate_credit_risk,
    calculate_insurance_premium,
    calculate_tip,
    calculate_violet_vitality,
    generate_results_pdf,
    main,
    triangular_membership,
)


class MembershipTests(unittest.TestCase):
    def test_triangle_and_shoulders(self):
        self.assertEqual(triangular_membership(5.0, (0.0, 5.0, 10.0)), 1.0)
        self.assertEqual(triangular_membership(2.5, (0.0, 5.0, 10.0)), 0.5)
        self.assertEqual(triangular_membership(0.0, (0.0, 0.0, 10.0)), 1.0)
        self.assertEqual(triangular_membership(10.0, (0.0, 10.0, 10.0)), 1.0)


class AssignmentTests(unittest.TestCase):
    def test_violet_reference_example_from_assignment(self):
        self.assertAlmostEqual(calculate_violet_vitality(40.0, 60.0), 0.625, delta=0.01)

    def test_violet_requested_example_is_in_range(self):
        self.assertAlmostEqual(calculate_violet_vitality(45.0, 50.0), 0.084, places=2)

    def test_credit_example_produces_risk_in_output_domain(self):
        self.assertAlmostEqual(calculate_credit_risk(2.0, 230.0, 90.0), 187.80, places=2)

    def test_tip_example_produces_value_in_output_domain(self):
        self.assertAlmostEqual(calculate_tip(6.5, 9.8), 19.77, places=2)

    def test_premium_example_produces_value_in_output_domain(self):
        self.assertAlmostEqual(calculate_insurance_premium(32.0, 0.7), 37.50, places=2)

    def test_interactive_mode_calculates_user_inputs(self):
        output = StringIO()
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "resultados.pdf"
            with (
                patch("builtins.input", side_effect=["a", "45", "50", "q"]),
                patch("sys.stdout", output),
                patch("main.RESULTS_PDF", report_path),
            ):
                main(["--interativo"])
            self.assertTrue(report_path.is_file())
        self.assertIn("Vitalidade calculada: 0.084 / 1", output.getvalue())
        self.assertIn("Relatório e gráfico salvos em:", output.getvalue())

    def test_pdf_contains_one_page_per_report(self):
        inference = _evaluate_violet_vitality(45.0, 50.0)
        reports = [
            ("Violeta", {"Água (ml)": 45.0}, inference),
            ("Violeta", {"Água (ml)": 45.0}, inference),
        ]
        with tempfile.TemporaryDirectory() as directory:
            report_path = generate_results_pdf(
                reports, Path(directory) / "resultados.pdf"
            )
            pdf_content = report_path.read_bytes()

        self.assertTrue(pdf_content.startswith(b"%PDF-"))
        self.assertTrue(pdf_content.rstrip().endswith(b"%%EOF"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", pdf_content)), 2)


if __name__ == "__main__":
    unittest.main()
