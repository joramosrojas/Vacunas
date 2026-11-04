import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import sk_upload as S  # noqa: E402

ID_A = "f05ddea660b4ad4581fd993d91b739400ff8ed05"
ID_B = "3a4082d0697af15051a9be4fb26884da94557a8a"
V = "Vimkunya chikungunya vaccine"
E = ("EBSI-CV-317-004\nPhase 3 randomized trial\nComparison: vaccinated vs placebo\n[Richardson JS, 2024]\n"
     f"[{ID_A}]\n\n3,258 participants aged 12 years and older\n\n2,794 vaccine group\n464 placebo group")
H = E.replace("Phase 3 randomized trial", "Ensayo aleatorizado de fase 3").replace("Comparison", "Comparación")
F = "United States\n\nFollow up: 183 days after vaccination.\n\nAny adverse event was measured."
FE = "Estados Unidos\n\nSeguimiento: 183 días después de la vacunación.\n\nSe midió cualquier evento adverso."
G = "Any adverse event: 1,257/2,790 (vaccine group) vs 161/464 (placebo group)"
J = "Cualquier evento adverso: 1.257/2.790 (grupo vacunado) vs. 161/464 (grupo placebo)"
ROWS = [
    [V, "Safety", "Any adverse event", "Overall", E, F, G, H, FE, J, "28 Octubre 2026"],
    [V, "Post-authorization safety", "Non-comparative", "Overall", f"[Simone B, 2025]\n\n[{ID_B}]",
     "12,816 doses\n\nNon-comparative study\nGermany", "NA",
     f"[Simone B, 2025]\n\n[{ID_B}]", "12.816 dosis\n\nEstudio no comparativo\nAlemania", "N / A", "28 Octubre 2026"],
]


def texts(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get("type") == "text":
            out.append(node["text"])
        for c in node.get("content", []):
            texts(c, out)
    return out


class SkUpload(unittest.TestCase):
    def test_english_structure(self):
        docs, refs, _ = S.build(ROWS, V, "en", trials=[])
        self.assertEqual({k: S.counts(docs[k])["tablas"] for k in ("efficacy", "safety", "post")},
                         {"efficacy": 4, "safety": 2, "post": 2})
        self.assertEqual(refs, [ID_A, ID_B])
        flat = " ".join(texts(docs["efficacy"]))
        for msg in ("No studies reporting vaccine efficacy against placebo were identified.",
                    "There are no studies reporting antibody responses against placebo.",
                    "No studies reporting vaccine effectiveness were identified."):
            self.assertIn(msg, flat)
        self.assertIn("No randomized clinical trials", " ".join(texts(docs["trials"])))
        self.assertIn("No comparative studies reporting post-authorization", " ".join(texts(docs["post"])))

    def test_spanish_uses_columns_h_j_and_reference_terms(self):
        docs, _, _ = S.build(ROWS, V, "es", "Vimkunya contra chikungunya", trials=[])
        flat = " ".join(texts(docs["safety"]))
        self.assertIn("Seguridad de la vacuna Vimkunya contra chikungunya", flat)
        self.assertIn("Cualquier evento adverso", flat)
        self.assertIn("1.257/2.790", flat)
        self.assertNotIn("1,257/2,790", flat)
        self.assertIn("No se identificaron estudios que reporten seguridad de la vacuna por subgrupo de interés.", flat)
        self.assertIn("Estudios no comparativos", " ".join(texts(docs["post"])))

    def test_noncomparative_row_and_citation(self):
        docs, _, _ = S.build(ROWS, V, "en", trials=[])
        s = json.dumps(docs["post"])
        self.assertIn(ID_B, s)
        self.assertIn("Non-comparative study", s)
        self.assertNotIn("No non-comparative studies", s)

    def test_rowspan_groups_studies_by_outcome(self):
        rows = [ROWS[0], list(ROWS[0])]
        rows[1][4] = E.replace("004", "005").replace(ID_A, ID_B)
        docs, _, _ = S.build(rows, V, "en", trials=[])
        first = docs["safety"]["content"][0]["content"]
        self.assertEqual(first[2]["content"][0]["attrs"]["rowspan"], 2)
        self.assertEqual(len(first[3]["content"]), 3)

    def test_subgroup_rows_go_to_subgroup_table(self):
        sub = list(ROWS[0])
        sub[3] = "Children and adolescents"
        docs, _, _ = S.build([sub], V, "en", trials=[])
        general, subgroup = docs["safety"]["content"]
        self.assertIn("No studies reporting vaccine safety against placebo", " ".join(texts(general)))
        self.assertIn("Children and adolescents", " ".join(texts(subgroup)))

    def test_trials_derived_from_rows(self):
        docs, refs, warn = S.build(ROWS, V, "en")
        flat = " ".join(texts(docs["trials"]))
        self.assertIn("Trial name: EBSI-CV-317-004", flat)
        self.assertIn("Phase 3", flat)
        self.assertTrue(any("sin registro" in w for w in warn))

    def test_trials_override_adds_registry_link(self):
        t = [{"phase": "3", "name": "EBSI-CV-317-004", "registry": "NCT05072080", "refs": [ID_A]}]
        docs, _, warn = S.build(ROWS, V, "es", "Vimkunya contra chikungunya", trials=t)
        flat = "".join(texts(docs["trials"]))
        self.assertIn("ID de registro: NCT05072080", flat)
        self.assertIn("Fase 3", flat)
        self.assertEqual(warn, [])

    def test_unknown_vaccine_requires_allow_empty(self):
        with self.assertRaises(ValueError):
            S.build(ROWS, "SKYVaricella varicella vaccine", "en")
        docs, refs, warn = S.build(ROWS, "SKYVaricella varicella vaccine", "en", allow_empty=True)
        self.assertEqual(refs, [])
        self.assertEqual(S.counts(docs["efficacy"])["citas"], 0)

    def test_missing_episte_id_is_an_error(self):
        bad = list(ROWS[0])
        bad[4] = E.replace(f"[{ID_A}]", "[sin id]")
        with self.assertRaises(ValueError):
            S.build([bad], V, "en", trials=[])

    def test_label_formatting(self):
        cell = S.results_cell("VE: 79% (95% CI: 66 - 88)\n1 dose: 85% (95% CI: 80 - 88)", S.LANG["en"])
        self.assertEqual(cell[0]["content"][0]["marks"], [{"type": "bold"}])
        self.assertEqual(cell[0]["content"][0]["text"], "VE:")
        self.assertNotIn("marks", cell[1]["content"][0])


if __name__ == "__main__":
    unittest.main()
