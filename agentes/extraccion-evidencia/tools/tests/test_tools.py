import datetime
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import render_tablas as R          # noqa: E402
import validate_record as V        # noqa: E402
from common import es_num, age_es, fecha_es  # noqa: E402

FIX = Path(__file__).resolve().parent


class Tools(unittest.TestCase):
    def setUp(self):
        self.rec = json.load(open(FIX / "galil_648.json", encoding="utf-8"))

    def test_fixture_is_valid(self):
        errs, _ = V.validate(self.rec)
        self.assertEqual(errs, [])

    def test_render_matches_published_rows(self):
        # Texto idéntico al que ya está cargado en Tablas_capa_1 (filas Galil 2002, hoja 2026).
        rows = R.render(self.rec, fecha_es(datetime.date(2026, 10, 28)))
        self.assertEqual(len(rows), 2)
        r = rows[0]
        self.assertEqual(r[:4], ["Varivax varicella vaccine", "Effectiveness", "Contracting disease", "Overall"])
        self.assertEqual(r[4], "Outbreak investigation cohort study\n\nComparison: vaccinated versus unvaccinated\n\n"
                               "[Galil K, 2002]\n[773fa108b71437d5fa1208e023ec847e98b5f3cb]\n\n"
                               "115 individuals aged 12 months and older\n\n80 vaccinated\n20 unvaccinated")
        self.assertEqual(r[6], "VE: 79% (95% CI: 66 - 88)")
        self.assertEqual(r[9], "EV: 79% (IC del 95%: 66 - 88)")
        self.assertEqual(r[10], "28 Octubre 2026")
        self.assertEqual(rows[1][2], "Contracting severe disease")
        self.assertTrue(rows[1][5].endswith("measured as moderate or severe varicella (more than 50 lesions or serious complications)."))

    def test_validator_catches_list_violations(self):
        bad = dict(self.rec, vaccine="Varilrix", country="USA", comparison="Foo")
        errs, _ = V.validate(bad)
        self.assertTrue(any("Varilrix" in e for e in errs))
        self.assertTrue(any("United States" in e for e in errs))
        self.assertTrue(any("comparison" in e for e in errs))

    def test_excluded_needs_note(self):
        rec = dict(self.rec, status="Excluded")
        errs, _ = V.validate(rec)
        self.assertTrue(any("status_note" in e for e in errs))

    def test_abstract_only_cannot_be_ok(self):
        rec = dict(self.rec, text_quality="abstract_only")
        errs, _ = V.validate(rec)
        self.assertTrue(any("text_quality" in e for e in errs))

    def test_number_and_age_helpers(self):
        self.assertEqual(es_num("85.4% (95% CI: 80.8 - 88.9)"), "85,4% (95% CI: 80,8 - 88,9)")
        self.assertEqual(es_num("85,050 individuals"), "85.050 individuals")
        self.assertEqual(age_es("5 years or younger"), "5 años o menos")
        self.assertEqual(age_es("18 to 65 years"), "18 a 65 años")

    def test_noncomparative_row(self):
        rec = {"type": "safety_noncomparative", "episte_id": "ca8c2d8f7693e3a4b1b1255252bcc5c1b242cb49",
               "ref": "Moro PL, 2022", "status": "Ok", "vaccine": "Varivax", "country": "United States",
               "n_participants": "132,763,998",
               "noncomparative": {"participants_label": "doses distributed", "described": "a study.", "reported": "40,684 reports"},
               "es": {"noncomparative_f": "texto en español"}}
        row = R.render(rec, "28 Octubre 2026")[0]
        self.assertEqual(row[2:4], ["Non-comparative", "Overall"])
        self.assertTrue(row[5].startswith("132,763,998 doses distributed\n\nNon-comparative study\nUnited States"))
        self.assertEqual((row[6], row[9]), ("NA", "N / A"))

    def test_only_ok_rows_are_rendered(self):
        import subprocess
        p = FIX / "_excluded_tmp.json"
        json.dump(dict(self.rec, status="Waiting", status_note="x"), open(p, "w"))
        try:
            out = subprocess.run([sys.executable, str(FIX.parent / "render_tablas.py"), str(p)],
                                 capture_output=True, text=True, check=True).stdout
        finally:
            p.unlink()
        self.assertEqual(json.loads(out), [])


if __name__ == "__main__":
    unittest.main()
