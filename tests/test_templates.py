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


if __name__ == "__main__":
    unittest.main()
