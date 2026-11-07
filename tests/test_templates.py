"""Regression tests for the template library's content integrity."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = ("Anamnesis", "ConsultationNotes")
TEXT_SUFFIXES = {".txt", ".md"}
EXPLANATION_SUFFIX = "_Açıklama.md"


class TemplateIntegrityTests(unittest.TestCase):
    """Guard the file pairing and references clinicians rely on."""

    def test_template_directories_exist(self):
        for name in TEMPLATE_DIRS:
            with self.subTest(directory=name):
                self.assertTrue((ROOT / name).is_dir())

    def test_every_template_is_non_empty_utf8(self):
        for name in TEMPLATE_DIRS:
            for path in sorted((ROOT / name).iterdir()):
                if path.is_file() and path.suffix in TEXT_SUFFIXES:
                    with self.subTest(template=path.name):
                        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_every_explanation_has_a_template(self):
        for path in sorted((ROOT / "Anamnesis").glob(f"*{EXPLANATION_SUFFIX}")):
            stem = path.name[: -len(EXPLANATION_SUFFIX)]
            with self.subTest(explanation=path.name):
                self.assertTrue((path.parent / f"{stem}.txt").is_file())

    def test_every_template_has_an_explanation(self):
        for path in sorted((ROOT / "Anamnesis").glob("*.txt")):
            with self.subTest(template=path.name):
                self.assertTrue((path.parent / f"{path.stem}{EXPLANATION_SUFFIX}").is_file())

    def test_consultation_notes_documented_in_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for path in sorted((ROOT / "ConsultationNotes").glob("*.txt")):
            with self.subTest(note=path.name):
                self.assertIn(path.name, readme)

    def test_readme_references_existing_files(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        available = {path.name for name in TEMPLATE_DIRS
                     for path in (ROOT / name).iterdir() if path.is_file()}
        referenced = {name for name in re.findall(r"`([^`/]+\.(?:txt|md))`", readme)
                      if not name.startswith(("_", ".")) and name != "README.md"}
        for name in sorted(referenced - {"README.md"}):
            with self.subTest(reference=name):
                self.assertIn(name, available)

    def test_txt_files_end_with_newline_and_no_leading_blank(self):
        for name in TEMPLATE_DIRS:
            for path in sorted((ROOT / name).glob("*.txt")):
                with self.subTest(template=path.name):
                    raw = path.read_bytes()
                    text = raw.decode("utf-8")
                    self.assertTrue(text.endswith("\n"), "missing trailing newline")
                    self.assertFalse(text.startswith((" ", "\n", "\r")),
                                     "leading blank/space")

    def test_no_known_orthography_regressions(self):
        banned = ("SEMBOLLER", "KOAGLÜ", "TEDAVİSİN KESİLMESİ",
                  "C+V", "ALERT OLUNMASI")
        for name in TEMPLATE_DIRS:
            for path in sorted((ROOT / name).glob("*.txt")):
                with self.subTest(template=path.name):
                    text = path.read_text(encoding="utf-8")
                    for token in banned:
                        self.assertNotIn(token, text)

    def test_no_hardcoded_prescription_in_anamnesis(self):
        for path in sorted((ROOT / "Anamnesis").glob("*.txt")):
            with self.subTest(template=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("REÇETE EDİLDİ", text)

    def test_no_double_dash_bullets(self):
        for name in TEMPLATE_DIRS:
            for path in sorted((ROOT / name).glob("*.txt")):
                with self.subTest(template=path.name):
                    for i, line in enumerate(
                            path.read_text(encoding="utf-8").splitlines(), 1):
                        self.assertFalse(line.lstrip().startswith("- -"),
                                         f"{path.name}:{i}")

    def test_every_explanation_lists_sources(self):
        for path in sorted((ROOT / "Anamnesis").glob(f"*{EXPLANATION_SUFFIX}")):
            with self.subTest(explanation=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## KAYNAKLAR", text)
                sources = [line for line in text.splitlines() if line.startswith("* ")]
                self.assertGreaterEqual(len(sources), 2, "at least two key sources")

    def test_lp_note_uses_evidence_based_aftercare(self):
        text = (ROOT / "ConsultationNotes" / "LP-Uygunluk-ve-Öneriler-Notu.txt").read_text(
            encoding="utf-8")
        self.assertNotIn("2–4 SAAT SUPİN", text)
        self.assertIn("ERKEN MOBİLİZASYON", text)
        self.assertIn("EPİDURAL KAN YAMASI", text)

    def test_high_risk_followups_include_safety_fields(self):
        epilepsy = (ROOT / "Anamnesis" / "EpilepsiTakip.txt").read_text(encoding="utf-8")
        self.assertIn("SÜRÜCÜLÜK / İŞ GÜVENLİĞİ", epilepsy)
        self.assertIn("GEBELİK / EMZİRME / GEBELİK PLANI", epilepsy)
        ms = (ROOT / "Anamnesis" / "MultiplSkleroz-OptikNörit-Ön-Tanı.txt").read_text(
            encoding="utf-8")
        self.assertIn("OCT", ms)
        self.assertIn("AQP4-IgG", ms)
        hbs = (ROOT / "Anamnesis" / "HBS.txt").read_text(encoding="utf-8")
        self.assertIn("TRANSFERRİN SATÜRASYONU", hbs)

    def test_clinical_claims_stay_within_evidence(self):
        headache = (ROOT / "Anamnesis" / "BaşAğrısı_Açıklama.md").read_text(encoding="utf-8")
        self.assertNotIn("tanı koydurucu niteliktedir", headache)
        self.assertNotIn("acil ileri tetkik (genellikle beyin görüntülemesi) gerektirir",
                         headache)
        optic = (ROOT / "Anamnesis" /
                 "MultiplSkleroz-OptikNörit-Ön-Tanı_Açıklama.md").read_text(encoding="utf-8")
        self.assertIn("Santral skotom tipik optik nöritte sık görülür", optic)
        tremor = (ROOT / "Anamnesis" / "EsansiyelTremor_Açıklama.md").read_text(
            encoding="utf-8")
        self.assertNotIn("DİDERAL", tremor)


if __name__ == "__main__":
    unittest.main()
