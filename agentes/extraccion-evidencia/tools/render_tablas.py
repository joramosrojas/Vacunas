#!/usr/bin/env python3
"""Genera las filas de Tablas_capa_1 (columnas A:K) desde registros validados.

Uso:  python3 tools/render_tablas.py registro.json [--fecha 2026-10-28] > filas.json
Salida: JSON con una lista de filas (11 valores cada una), lista para append_values.
Solo effectiveness y seguridad (comparativa / no comparativa). Los textos libres en español
vienen del registro (campo 'es'); el resto se deriva por código.
"""
import argparse
import datetime
import json
import sys

from common import LISTS, age_es, es_num, fecha_es, num

COMP_ES = {
    "Vaccinated versus unvaccinated": "vacunados versus no vacunados",
    "Pre-vaccination period versus post-vaccination period": "período prevacunación versus período posvacunación",
    "NA": "",
}
UNIT_EN = {"Cases": "cases", "Controls": "controls", "Vaccinated": "vaccinated",
           "Unvaccinated": "unvaccinated", "Doses administered": "doses administered", "NA": ""}
UNIT_ES = {"Cases": ("caso", "casos"), "Controls": ("control", "controles"),
           "Vaccinated": ("vacunado", "vacunados"), "Unvaccinated": ("no vacunado", "no vacunados"),
           "Doses administered": ("dosis administrada", "dosis administradas")}


def cap(s):
    return s[:1].upper() + s[1:]


def n_es(n):
    return es_num(n)


def fmt_est(e):
    p, lo, hi = num(e.get("point")), num(e.get("lo")), num(e.get("hi"))
    if not p:
        return ""
    pct = "%"
    ci = f"(95% CI: {lo} - {hi})" if lo and hi else "(95% CI: Not reported)"
    return f"{p}{pct} {ci}"


def results_en(o, kind):
    if o.get("results_text"):
        return o["results_text"]
    measure = o.get("measure", "")
    d1, d2 = o.get("dose1", {}), o.get("dose2", {})
    e1, e2 = fmt_est(d1), fmt_est(d2)
    lead = "VE" if kind == "effectiveness" and measure == "VE" else measure
    if e1 and e2:
        return f"{lead}:\n1 dose: {e1}\n2 doses: {e2}"
    return f"{lead}: {e1 or e2}"


def results_es(o, kind):
    if o.get("results_text"):
        return o["results_text_es"]
    s = results_en(o, kind)
    s = s.replace("VE:", "EV:").replace("1 dose:", "1 dosis:").replace("2 doses:", "2 dosis:")
    s = s.replace("95% CI", "IC del 95%").replace("Not reported", "no reportado")
    return es_num(s)


def design_block_en(rec):
    lines = [cap(rec["design"])]
    if rec.get("comparison"):
        lines += ["", f"Comparison: {rec['comparison'][0].lower() + rec['comparison'][1:]}"]
    lines += ["", f"[{rec['ref']}]", f"[{rec['episte_id']}]", ""]
    n, age = rec.get("n_participants", ""), rec.get("age", "")
    if rec.get("population_en"):
        lines.append(rec["population_en"])
    else:
        lines.append(f"{n} individuals aged {age}" if n and age else
                     (f"{n} individuals" if n else (f"Individuals of {age}" if age else "")))
    groups = []
    for n_, u in ((rec.get("n_intervention"), rec.get("unit_intervention")), (rec.get("n_control"), rec.get("unit_control"))):
        if n_ and u and u != "NA":
            groups.append(f"{n_} {UNIT_EN[u]}")
    if groups:
        lines += [""] + groups
    return "\n".join(lines)


def design_block_es(rec):
    es = rec.get("es", {})
    design = es.get("design")
    if not design:
        raise ValueError("falta es.design")
    lines = [cap(design)]
    if rec.get("comparison"):
        lines += ["", f"Comparación: {COMP_ES[rec['comparison']]}"]
    lines += ["", f"[{rec['ref']}]", f"[{rec['episte_id']}]", ""]
    n, age = rec.get("n_participants", ""), rec.get("age", "")
    pop = es.get("population")
    if not pop and rec.get("population_en"):
        raise ValueError("population_en requiere es.population")
    if not pop:
        a = es.get("age") or age_es(age)
        if age and not a:
            raise ValueError(f"falta es.age para '{age}'")
        pop = (f"{n_es(n)} individuos de {a}" if n and age else
               (f"{n_es(n)} individuos" if n else (f"Individuos de {a}" if age else "")))
    lines.append(pop)
    groups = es.get("groups")
    if groups is None:
        groups = []
        for n_, u in ((rec.get("n_intervention"), rec.get("unit_intervention")), (rec.get("n_control"), rec.get("unit_control"))):
            if n_ and u and u != "NA":
                sing, plur = UNIT_ES[u]
                groups.append(f"{n_es(n_)} {plur}")
    if groups:
        lines += [""] + groups
    return "\n".join(lines)


def country_block_en(rec, o):
    verb = "Disease occurrence was measured as" if o.get("ecological") else "Contracting the disease was measured as"
    if rec["type"] != "effectiveness":
        verb = "{} was measured as".format(o.get("event") or "The outcome")
    return (f"{rec['country']}\n\nData from {rec['data_from']}.\n\nObservation period: {rec['period']}.\n\n"
            f"{verb} {o['measured_as']}.")


def country_block_es(rec, o):
    es = rec.get("es", {})
    for k in ("country", "data_from", "period"):
        if not es.get(k):
            raise ValueError(f"falta es.{k}")
    if o.get("ecological"):
        tail = f"La ocurrencia de la enfermedad se midió como {o['measured_as_es']}."
    elif rec["type"] == "effectiveness":
        tail = f"Se consideró que una persona contrajo la enfermedad si presentó {o['measured_as_es']}."
    else:
        tail = f"{o.get('event') or 'El desenlace'} se midió como {o['measured_as_es']}."
    return (f"{es['country']}\n\nDatos de {es['data_from']}.\n\nPeríodo de observación: {es['period']}.\n\n{tail}")


def render(rec, fecha):
    t = rec["type"]
    vac = LISTS["vaccine_display"][rec["vaccine"]]
    rows = []
    if t == "safety_noncomparative":
        nc = rec["noncomparative"]
        n = rec.get("n_participants", "")
        ref = f"[{rec['ref']}]\n\n[{rec['episte_id']}]"
        e = ref
        f = (f"{n} participants\n\nNon-comparative study\n{rec['country']}\n\n"
             f"The study described {nc['described']}\n\nThe study reported {nc['reported']}")
        es = rec.get("es", {})
        h = ref
        i = es.get("noncomparative_f") or (_ for _ in ()).throw(ValueError("falta es.noncomparative_f"))
        rows.append([vac, "Post-authorization safety", "Non-comparative", "Overall", e, f, "NA", h, i, "N / A", fecha])
        return rows
    for o in rec["outcomes"]:
        if t == "effectiveness":
            section = "Effectiveness"
            outcome = "Contracting disease" if o["kind"] == "disease" else "Contracting severe disease"
            group = "Overall"
        else:
            section, outcome, group = "Post-authorization safety", "Comparative", o["event"]
        rows.append([vac, section, outcome, group,
                     design_block_en(rec), country_block_en(rec, o), results_en(o, t),
                     design_block_es(rec), country_block_es(rec, o), results_es(o, t), fecha])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--fecha", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    data = json.load(open(a.path, encoding="utf-8"))
    recs = data if isinstance(data, list) else [data]
    fecha = fecha_es(datetime.date.fromisoformat(a.fecha))
    out = []
    for rec in recs:
        if rec.get("status") != "Ok":
            continue            # solo los Ok pasan a Tablas_capa_1
        out += render(rec, fecha)
    json.dump(out, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
