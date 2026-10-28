#!/usr/bin/env python3
"""Valida un registro de extracción contra las listas de la planilla.

Uso:  python3 tools/validate_record.py registro.json [registro2.json ...]
Salida: una línea por problema. Código de salida 1 si hay errores.
Los errores se corrigen una sola vez en el extractor; las advertencias (WARN) van al reporte.
"""
import json
import re
import sys

from common import LISTS


def validate(rec):
    errs, warns = [], []
    t = rec.get("type")
    kind = "effectiveness" if t == "effectiveness" else "safety"

    def need(field):
        if not rec.get(field):
            errs.append(f"falta '{field}'")

    for f in ("type", "episte_id", "ref", "status"):
        need(f)
    if rec.get("episte_id") and not re.fullmatch(r"[0-9a-f]{40}", rec["episte_id"]):
        errs.append("episte_id debe tener 40 caracteres hexadecimales")

    st = rec.get("status")
    if st and st not in LISTS["agent_allowed_status"]:
        errs.append(f"status '{st}' no permitido al agente (usar {LISTS['agent_allowed_status']})")
    if st in ("Waiting", "Excluded") and not rec.get("status_note"):
        errs.append("status Waiting/Excluded requiere 'status_note'")
    if rec.get("assigned_to") and rec["assigned_to"] not in LISTS["assigned_to"]:
        errs.append(f"assigned_to '{rec['assigned_to']}' fuera de la lista")

    vac = rec.get("vaccine", "")
    if vac and vac not in LISTS["vaccine"]:
        errs.append(f"vaccine '{vac}' no está en la lista (dejar vacío y marcar Excluded)")
    if not vac and st == "Ok":
        errs.append("status Ok requiere vaccine de la lista")

    if rec.get("comparison") and rec["comparison"] not in LISTS["comparison"][kind]:
        errs.append(f"comparison '{rec['comparison']}' fuera de la lista")
    if rec.get("unit_intervention") and rec["unit_intervention"] not in LISTS["unit_intervention"][kind]:
        errs.append(f"unit_intervention '{rec['unit_intervention']}' fuera de la lista")
    if rec.get("unit_control") and rec["unit_control"] not in LISTS["unit_control"][kind]:
        errs.append(f"unit_control '{rec['unit_control']}' fuera de la lista")

    country = rec.get("country", "")
    if country in LISTS["country_fixes"]:
        errs.append(f"country '{country}' -> usar '{LISTS['country_fixes'][country]}'")

    age = rec.get("age", "")
    if age and re.search(r"(?i)\byrs?\b|\byo\b", age):
        warns.append(f"age '{age}': usar 'X years and older' / 'X to Y years' / 'all ages' / 'NR'")

    for i, o in enumerate(rec.get("outcomes", []), 1):
        tag = f"outcome {i}"
        if t == "effectiveness":
            if o.get("kind") not in ("disease", "severe"):
                errs.append(f"{tag}: kind debe ser 'disease' o 'severe'")
            measure_list = LISTS["effect_measure_effectiveness"]
        else:
            if o.get("event") and o["event"] not in LISTS["safety_outcomes"]:
                errs.append(f"{tag}: event '{o['event']}' fuera de la lista (usar NA y describir)")
            measure_list = LISTS["effect_measure_safety"]
        if not o.get("measured_as"):
            errs.append(f"{tag}: falta measured_as")
        has_num = any(o.get(d, {}).get("point") not in (None, "") for d in ("dose1", "dose2"))
        has_text = bool(o.get("results_text"))
        if not (has_num or has_text):
            errs.append(f"{tag}: sin estimador ni results_text")
        if has_num and o.get("measure") not in measure_list:
            errs.append(f"{tag}: measure '{o.get('measure')}' fuera de la lista {measure_list}")
        if has_text and not o.get("results_text_es"):
            errs.append(f"{tag}: results_text requiere results_text_es")
        if not o.get("measured_as_es"):
            warns.append(f"{tag}: falta measured_as_es (se necesita para Tablas_capa_1)")
        for d in ("dose1", "dose2"):
            e = o.get(d, {})
            p = e.get("point")
            if p not in (None, "") and (e.get("lo") in (None, "") or e.get("hi") in (None, "")):
                warns.append(f"{tag}: {d} sin IC -> la tabla dirá '95% CI: Not reported'")
            try:
                lo, hi, pt = (float(e[k]) for k in ("lo", "hi", "point"))
                if not (lo <= pt <= hi):
                    warns.append(f"{tag}: {d} punto {pt} fuera de su IC {lo}-{hi}")
            except (KeyError, TypeError, ValueError):
                pass

    if t == "safety_noncomparative":
        nc = rec.get("noncomparative", {})
        if not nc.get("described") or not nc.get("reported"):
            errs.append("no comparativa: faltan noncomparative.described / reported")
    if t in ("effectiveness", "safety_comparative") and st == "Ok" and not rec.get("outcomes"):
        errs.append("status Ok requiere al menos un outcome")

    if rec.get("text_quality") in ("abstract_only", "none") and st == "Ok":
        errs.append("text_quality incompleto no puede quedar en Ok (usar Waiting con nota)")

    return errs, warns


def main(paths):
    bad = 0
    for p in paths:
        data = json.load(open(p, encoding="utf-8"))
        recs = data if isinstance(data, list) else [data]
        for rec in recs:
            errs, warns = validate(rec)
            name = rec.get("ref", p)
            for e in errs:
                print(f"ERROR {name}: {e}")
            for w in warns:
                print(f"WARN  {name}: {w}")
            bad += bool(errs)
            if not errs and not warns:
                print(f"OK    {name}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
