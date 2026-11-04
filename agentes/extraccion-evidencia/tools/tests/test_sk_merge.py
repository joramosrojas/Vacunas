import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_merge as M   # noqa: E402
import sk_upload as S  # noqa: E402

V = "Vimkunya chikungunya vaccine"
ID = {k: (str(k) * 40)[:40].replace("1", "a").replace("2", "b").replace("3", "c").replace("4", "d") for k in "1234"}


def e(trial, rid, who):
    return (f"{trial}\nPhase 3 randomized trial\nComparison: vaccinated vs placebo\n[{who}]\n[{rid}]\n\n"
            "100 participants aged 12 years and older\n\n50 vaccine group\n50 placebo group")


def r(section, outcome, group, rid, who, results="RR: 1.1 (95% CI: 0.9 - 1.3)", trial="TRIAL-1", vac=V):
    return [vac, section, outcome, group, e(trial, rid, who), "United States\n\nFollow up: 6 months.\n\nMeasured.", results,
            "", "", "", "28 Octubre 2026"]


def texts(n, out=None):
    out = [] if out is None else out
    if isinstance(n, dict):
        if n.get("type") == "text":
            out.append(n["text"])
        for c in n.get("content", []):
            texts(c, out)
    return out


def tables(doc):
    return [n for n in doc["content"] if n.get("type") == "table"]


A = r("Safety", "Any adverse event", "Overall", ID["1"], "Autor A, 2024")
B = r("Safety", "Serious adverse events", "Overall", ID["1"], "Autor A, 2024")
C = r("Safety", "Any adverse event", "Overall", ID["2"], "Autor B, 2025", trial="TRIAL-2")
NC = [V, "Post-authorization safety", "Non-comparative", "Overall", f"[Autor C, 2025]\n\n[{ID['3']}]",
      "1,000 doses\n\nNon-comparative study\nGermany", "NA", "", "", "", ""]


def existing_from(rows):
    docs, _, _ = S.build(rows, V, "en", trials=[], allow_empty=True)
    docs.pop("trials")
    return docs


class Merge(unittest.TestCase):
    def sync(self, rows, existing, **kw):
        ex = dict(existing)
        ex.setdefault("trials", None)
        return M.sync_plan(rows, V, "en", None, kw.pop("trials", []), ex, **kw)

    def test_idempotent(self):
        rows = [A, B, C, NC]
        out, log, refs, _ = self.sync(rows, existing_from(rows))
        self.assertEqual(out, {"trials": out.get("trials")} if "trials" in out else {})
        self.assertEqual(refs, [] if not out else refs)

    def test_adds_only_new_study_to_existing_outcome_group(self):
        existing = existing_from([A, B])
        out, log, refs, _ = self.sync([A, B, C], existing)
        self.assertEqual(refs, [ID["2"]])
        t = tables(out["safety"])[0]
        self.assertEqual(M.scan(t)["rows"][2]["lead_first"], "any adverse event")
        self.assertEqual(t["content"][2]["content"][0]["attrs"]["rowspan"], 2)   # grupo creció de 1 a 2
        self.assertTrue(M.structure_ok(t))
        self.assertEqual(sum(1 for x in log if "+ Any adverse event" in x), 1)
        # lo existente quedó idéntico
        self.assertEqual(tables(existing["safety"])[1], tables(out["safety"])[1])

    def test_second_pass_adds_nothing(self):
        existing = existing_from([A])
        out, *_ = self.sync([A, B, C], existing)
        again, *_ = self.sync([A, B, C], {**existing, **out})
        self.assertNotIn("safety", again)

    def test_placeholder_is_replaced_and_new_outcome_appended(self):
        existing = existing_from([NC])
        out, *_ = self.sync([NC, A], existing)
        flat = " ".join(texts(out["safety"]))
        self.assertNotIn("No studies reporting vaccine safety against placebo", flat.split("by subgroup")[0])
        self.assertTrue(M.structure_ok(tables(out["safety"])[0]))

    def test_duplicate_id_and_outcome_not_added(self):
        existing = existing_from([A])
        dup = copy.deepcopy(A)
        dup[6] = "RR: 9.9 (95% CI: 9 - 10)"                       # mismo estudio y desenlace, otros números
        out, log, *_ = self.sync([dup], existing)
        self.assertNotIn("safety", out)
        self.assertTrue(any("ya estaba" in x for x in log))

    def test_same_study_other_outcome_is_new(self):
        out, log, refs, _ = self.sync([A, B], existing_from([A]))
        self.assertIn("safety", out)
        self.assertEqual(refs, [ID["1"]])   # candidata; sync la omite si la síntesis ya la tiene registrada
        self.assertEqual(tables(out["safety"])[0]["content"][-1]["content"][0]["content"][0]["content"][0]["text"],
                         "Serious adverse events")

    def test_handmade_label_is_flagged_not_added(self):
        existing = existing_from([A])
        t = tables(existing["safety"])[0]
        t["content"][2]["content"][0]["content"][0]["content"][0]["text"] = "Adverse events (all)"  # etiqueta manual
        out, log, *_ = self.sync([B], existing)
        self.assertNotIn("safety", out)
        self.assertTrue(any("PARA REVISAR" in x for x in log))
        forced, *_ = self.sync([B], existing, include_flagged=True)
        self.assertIn("safety", forced)

    def test_comparative_events(self):
        c1 = [V, "Post-authorization safety", "Comparative", "Anaphylaxis", e("VSD", ID["4"], "Autor D, 2019"),
              "United States\n\nObservation period: 2015.\n\nMeasured.", "RR 0", "", "", "", ""]
        c2 = copy.deepcopy(c1)
        c2[3] = "Pancreatitis"
        c3 = copy.deepcopy(c1)
        c3[3] = "Anaphylaxis (severe)"
        existing = existing_from([c1])
        out, log, *_ = self.sync([c1, c2], existing)
        self.assertEqual(sum(1 for x in log if x.strip().startswith("+ Pancreatitis")), 1)
        flagged, log2, *_ = self.sync([c3], existing)
        self.assertNotIn("post", flagged)
        self.assertTrue(any("PARA REVISAR" in x for x in log2))

    def test_spanish_event_label_and_match_with_english_leads(self):
        c = [V, "Post-authorization safety", "Comparative", "Anaphylaxis", e("VSD", ID["4"], "Autor D, 2019"),
             "United States\n\nObservation period: 2015.\n\nAnaphylaxis was measured as X.", "RR 0",
             e("VSD", ID["4"], "Autor D, 2019"), "Estados Unidos\n\nPeríodo: 2015.\n\nAnafilaxia se midió como X.",
             "RR 0", ""]
        L = S.LANG["es"]
        self.assertEqual(S.event_name(L, c), "Anafilaxia")
        self.assertEqual(S.event_name(S.LANG["en"], c), "Anaphylaxis")
        docs, *_ = S.build([c], V, "es", "X", trials=[])
        self.assertEqual(M.scan(tables(docs["post"])[0])["rows"][2]["lead_first"], "anafilaxia")
        # una síntesis subida antes con el evento en inglés no se duplica ni se parte en dos grupos
        old = copy.deepcopy(docs)
        lead = tables(old["post"])[0]["content"][2]["content"][0]["content"][0]["content"][0]
        lead["text"] = "Anaphylaxis"
        out, log, *_ = M.sync_plan([c], V, "es", "X", [], {**old, "trials": None})
        self.assertNotIn("post", out)

    def test_noncomparative_by_id(self):
        existing = existing_from([NC])
        out, *_ = self.sync([NC], existing)
        self.assertNotIn("post", out)
        other = copy.deepcopy(NC)
        other[4] = f"[Autor E, 2026]\n\n[{ID['4']}]"
        out2, _, refs, _ = self.sync([NC, other], existing)
        self.assertEqual(refs, [ID["4"]])
        self.assertTrue(M.structure_ok(tables(out2["post"])[1]))

    def test_incoming_duplicates_are_ignored(self):
        out, log, refs, _ = self.sync([A, copy.deepcopy(A)], existing_from([C]))
        self.assertEqual(sum(1 for x in log if "fila repetida" in x), 1)
        self.assertEqual(sum(1 for x in log if x.strip().startswith("+ Any adverse event")), 1)

    def test_handmade_content_is_preserved(self):
        existing = existing_from([A])
        note = S.P(S.T("Nota escrita a mano que no está en Tablas_capa_1"))
        existing["safety"]["content"].insert(0, note)
        manual = S.row(*[S.cell([S.P(S.T(x))]) for x in ("Estudio manual", "diseño", "país", "resultado")])
        tables(existing["safety"])[0]["content"].append(manual)
        out, *_ = self.sync([A, C], existing)
        flat = " ".join(texts(out["safety"]))
        self.assertIn("Nota escrita a mano", flat)
        self.assertIn("Estudio manual", flat)
        self.assertEqual(M.find_duplicates(out["safety"]), [])

    def test_trials_merge(self):
        t1 = {"phase": "3", "name": "TRIAL-1", "registry": "NCT00000001", "refs": [ID["1"]]}
        t2 = {"phase": "3", "name": "TRIAL-2", "registry": "NCT00000002", "refs": [ID["2"]]}
        t3 = {"phase": "2", "name": "TRIAL-3", "registry": "NCT00000003", "refs": [ID["3"]]}
        base = S.trials_doc(S.LANG["en"], [t1])
        ex = {"trials": base}
        out, log, *_ = M.sync_plan([A], V, "en", None, [t1, t2, t3], {**ex, "efficacy": None, "safety": None, "post": None})
        flat = " ".join(texts(out["trials"]))
        self.assertIn("TRIAL-2", flat)
        self.assertIn("TRIAL-3", flat)
        self.assertEqual(flat.count("TRIAL-1"), 1)                     # el existente no se repite
        heads = [" ".join(texts(n)) for n in out["trials"]["content"] if n["type"] == "heading"]
        self.assertEqual(heads, ["Phase 2", "Phase 3"])                # fase nueva en su lugar
        again, *_ = M.sync_plan([A], V, "en", None, [t1, t2, t3], {**ex, "trials": out["trials"],
                                                                    "efficacy": None, "safety": None, "post": None})
        self.assertNotIn("trials", again)

    def test_classify_and_structure(self):
        docs = existing_from([A])
        self.assertEqual([M.classify(t) for t in tables(docs["safety"])], ["saf", "saf_sub"])
        self.assertEqual([M.classify(t) for t in tables(docs["efficacy"])], ["imm", "eff", "eff_sub", "effect"])
        legacy = copy.deepcopy(tables(docs["safety"])[0])
        legacy["content"][1]["content"][0]["content"][0]["content"][0]["text"] = "Subgroup"
        self.assertEqual(M.classify(legacy), "saf_sub")                   # título repetido, encabezado distingue
        booster = copy.deepcopy(tables(docs["efficacy"])[1])
        booster["content"][0]["content"][0]["content"][0]["content"][0]["text"] = "Efficacy of the booster dose"
        self.assertIsNone(M.classify(booster))
        broken = copy.deepcopy(tables(existing_from([A, C])["safety"])[0])
        broken["content"][2]["content"][0]["attrs"]["rowspan"] = 5
        self.assertFalse(M.structure_ok(broken))

    def test_spanish_existing_tables_are_recognized(self):
        es = [V, "Safety", "Any adverse event", "Overall", e("T", ID["1"], "Autor A, 2024"),
              "United States\n\nFollow up: 6 months.\n\nMeasured.", "RR: 1.1", e("T", ID["1"], "Autor A, 2024"),
              "Estados Unidos\n\nSeguimiento: 6 meses.\n\nSe midió.", "RR: 1,1", ""]
        docs, _, _ = S.build([es], V, "es", "Vimkunya contra chikungunya", trials=[])
        self.assertEqual([M.classify(t) for t in tables(docs["safety"])], ["saf", "saf_sub"])
        out, *_ = M.sync_plan([es], V, "es", "Vimkunya contra chikungunya", [], {**docs, "trials": None})
        self.assertNotIn("safety", out)


if __name__ == "__main__":
    unittest.main()
