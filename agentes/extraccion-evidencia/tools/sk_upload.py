#!/usr/bin/env python3
"""Sube a SK Platform las tablas de efectos de una vacuna, desde filas de Tablas_capa_1.

Subcomandos (solo biblioteca estándar; el token va en la variable de entorno SK_TOKEN):

  build   filas A:K de Tablas_capa_1 (JSON) -> documentos de las 4 secciones (JSON)
  upload  documentos -> síntesis de SK (referencias + reportes), con verificación
  sync    agrega a una síntesis ya poblada SOLO los estudios nuevos (sin borrar nada, sin IDs duplicados)
  check   revisa IDs duplicados y citas rotas de una síntesis (solo lectura)
  inspect muestra nombre, reportes y referencias de una síntesis

Formato y reglas: docs/planillas/sk_platform.md. Uso paso a paso: skills/subir-a-sk/SKILL.md.
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request

API = "https://api.skplatform.org/v1/graphql"
ID40 = re.compile(r"\[([0-9a-f]{40})\]")
REGISTRY = re.compile(r"\[((?:NCT|CTRI|jRCT|ISRCTN|ChiCTR|EudraCT|ACTRN)[^\]]*)\]")

SECTIONS = {  # clave -> nombre de la sección de SK en cada idioma
    "efficacy": {"en": "Vaccine efficacy and effectiveness", "es": "Eficacia y efectividad de la vacuna"},
    "safety": {"en": "Vaccine safety", "es": "Seguridad de la vacuna"},
    "post": {"en": "Post-authorization safety", "es": "Seguridad post-autorización"},
    "trials": {"en": "General characteristics of clinical trials",
               "es": "Características generales de los ensayos clínicos"},
}
SECTION_ORDER = ["trials", "efficacy", "safety", "post"]

EFF_ORDER = ["Contracting disease", "Contracting severe disease"]
SAFETY_ORDER = ["Any adverse event", "Serious adverse events"]

LANG = {
    "en": {
        "lang": "en",
        "cols": (4, 5, 6),
        "hdr": ["Outcome", "Study design and number of participants",
                "Country, follow-up and outcome definition", "Main results"],
        "efficacy_col": "Efficacy*", "sub_outcome": "Outcome by subgroup", "subgroup": "Subgroup",
        "ref": "Reference", "nc_desc": "Study description and main results",
        "outcome": {}, "group": {},
        "h_eff": "Vaccine efficacy", "h_eff_sub": "Vaccine efficacy in subgroups",
        "h_effect": "Vaccine effectiveness", "h_comp": "Comparative studies", "h_nc": "Non-comparative studies",
        "t_imm": "Immunogenicity of the {x}", "t_eff": "Efficacy of the {x}",
        "t_eff_sub": "Efficacy of the {x} by subgroup of interest",
        "t_effect": "Effectiveness of the {x} (comparative studies)",
        "t_saf": "Safety of the {x}", "t_saf_sub": "Safety of the {x} by subgroup of interest",
        "t_comp": "Post-authorization safety of the {x} (comparative studies)",
        "t_nc": "Post-authorization safety of the {x} (non-comparative studies, low-quality evidence)",
        "e_ab": "There are no studies reporting antibody responses against placebo.",
        "e_cell": "There are no studies reporting cellular responses against placebo.",
        "e_eff": "No studies reporting vaccine efficacy against placebo were identified.",
        "e_eff_sub": "No studies reporting vaccine efficacy by subgroup of interest were identified.",
        "e_effect": "No studies reporting vaccine effectiveness were identified.",
        "e_saf": "No studies reporting vaccine safety against placebo were identified.",
        "e_saf_sub": "No studies reporting vaccine safety by subgroup of interest were identified.",
        "e_comp": "No comparative studies reporting post-authorization vaccine safety were identified.",
        "e_nc": "No non-comparative studies reporting post-authorization vaccine safety were identified.",
        "e_trials": "No randomized clinical trials reporting vaccine efficacy and/or safety were identified.",
        "trials_intro": "The following randomized clinical trials have reported vaccine efficacy and/or safety:",
        "trial": "Trial name: ", "registry": "Registry ID: ", "pubs": "Available publications:",
        "phase": "Phase {n}", "phase_na": "Phase not reported",
        "grp_re": r"(Vaccine|Placebo) group:", "gmt": "Geometric mean titre",
    },
    "es": {
        "lang": "es",
        "cols": (7, 8, 9),
        "hdr": ["Desenlace", "Diseño de estudio y número de participantes",
                "País, seguimiento y definición del desenlace", "Principales resultados"],
        "efficacy_col": "Eficacia*", "sub_outcome": "Desenlace por subgrupo", "subgroup": "Subgrupo",
        "ref": "Referencia", "nc_desc": "Descripción del estudio y principales resultados",
        "outcome": {"Antibody response": "Respuesta de anticuerpos", "Cellular response": "Respuesta celular",
                    "Contracting disease": "Contraer la enfermedad",
                    "Contracting severe disease": "Contraer la enfermedad severa",
                    "Any adverse event": "Cualquier evento adverso", "Serious adverse events": "Eventos adversos graves"},
        "group": {"Children and adolescents": "Niños y adolescentes", "Older adults": "Adultos mayores",
                  "Overall": "General"},
        "h_eff": "Eficacia de la vacuna", "h_eff_sub": "Eficacia de la vacuna en subgrupos",
        "h_effect": "Efectividad en estudios comparativos", "h_comp": "Estudios comparativos",
        "h_nc": "Estudios no comparativos",
        "t_imm": "Inmunogenicidad de la vacuna {x}", "t_eff": "Eficacia de la vacuna {x}",
        "t_eff_sub": "Eficacia de la vacuna {x} por subgrupo de interés",
        "t_effect": "Efectividad de la vacuna {x} (estudios comparativos)",
        "t_saf": "Seguridad de la vacuna {x}", "t_saf_sub": "Seguridad de la vacuna {x} por subgrupo de interés",
        "t_comp": "Seguridad post-autorización de la vacuna {x} (estudios comparativos)",
        "t_nc": "Seguridad post-autorización de la vacuna {x} (estudios no comparativos, evidencia de baja calidad)",
        "e_ab": "No hay estudios que informen sobre la respuesta de anticuerpos.",
        "e_cell": "No hay estudios que informen sobre las respuestas celulares.",
        "e_eff": "No se identificaron estudios que reporten la eficacia de la vacuna.",
        "e_eff_sub": "No se identificaron estudios que reporten la eficacia de la vacuna por subgrupo de interés.",
        "e_effect": "No se identificaron estudios que reporten la efectividad de la vacuna.",
        "e_saf": "No se identificaron estudios que reporten seguridad de la vacuna.",
        "e_saf_sub": "No se identificaron estudios que reporten seguridad de la vacuna por subgrupo de interés.",
        "e_comp": "No se identificaron estudios comparativos que informaran sobre la seguridad de la vacuna "
                  "después de su autorización.",
        "e_nc": "No se identificaron estudios no comparativos que informaran sobre la seguridad de la vacuna "
                "después de su autorización.",
        "e_trials": "No se identificaron ensayos clínicos aleatorizados reportando datos de eficacia y/o "
                    "seguridad de la vacuna.",
        "trials_intro": "Los siguientes ensayos clínicos aleatorizados han reportado datos de eficacia y/o "
                        "seguridad de la vacuna:",
        "trial": "Nombre del ensayo: ", "registry": "ID de registro: ", "pubs": "Publicaciones disponibles:",
        "phase": "Fase {n}", "phase_na": "Fase no reportada",
        "grp_re": r"Grupo (vacunado|placebo):", "gmt": "Título medio geométrico",
    },
}


# ---------------------------------------------------------------- nodos del editor de SK (TipTap)
def T(text, *marks):
    n = {"type": "text", "text": text}
    if marks:
        n["marks"] = [{"type": m} for m in marks]
    return n


HB = {"type": "hardBreak"}


def P(*inline):
    return {"type": "paragraph", "content": list(inline)} if inline else {"type": "paragraph"}


def REF(rid):
    return {"type": "reference", "attrs": {"referenceId": rid}}


def cell(content, colspan=1, rowspan=1):
    return {"type": "tableCell", "attrs": {"colspan": colspan, "colwidth": None, "rowspan": rowspan},
            "content": content}


def row(*cells):
    return {"type": "tableRow", "content": list(cells)}


def heading(level, text, bold=False):
    return {"type": "heading", "attrs": {"level": level}, "content": [T(text, "bold") if bold else T(text)]}


def title_row(text, cols=4):
    return row(cell([{"type": "heading", "attrs": {"level": 4}, "content": [T(text, "bold")]}], colspan=cols))


def header_row(*names):
    return row(*[cell([P(T(n, "bold"))]) for n in names])


def empty_row(text, cols=4, first=None):
    if first:
        return row(cell([P(T(first, "bold"))]), cell([P(T(text))], colspan=cols - 1))
    return row(cell([P(T(text))], colspan=cols))


def table(*rows):
    return {"type": "table", "content": list(rows)}


def link(text, href):
    return {"type": "text", "text": text, "marks": [{"type": "link", "attrs": {
        "href": href, "target": "_blank", "rel": "noopener noreferrer nofollow",
        "class": "tw-text-blue-500 tw-underline hover:tw-text-blue-700"}}]}


# ---------------------------------------------------------------- celdas de una fila de Tablas_capa_1
def design_cell(e, where):
    """E/H: encabezado (nombre, diseño, comparación) + cita + participantes."""
    lines = e.split("\n")
    k = next((i for i, l in enumerate(lines) if re.fullmatch(ID40.pattern, l)), None)
    if k is None:
        raise ValueError(f"{where}: no hay [Episte ID] de 40 caracteres en la celda de diseño")
    rid = lines[k].strip("[]")
    head = [l for l in lines[:k - 1] if l.strip()]
    out = [P(T(l)) for l in head] + [P(REF(rid)), P()]
    blank = False
    for l in lines[k + 1:]:
        if l.strip():
            out.append(P(T(l)))
            blank = False
        elif not blank:
            out.append(P())
            blank = True
    while len(out) > 1 and out[-1] == P() and out[-2] == P():
        out.pop()
    return out, rid


def country_cell(f):
    out = []
    for i, chunk in enumerate(f.split("\n\n")):
        if i:
            out.append(P())
        out += [P(T(l)) for l in chunk.replace("Follow up:", "Follow-up:").split("\n")]
    return out


def results_cell(g, L, prefix=None):
    """Etiquetas en negrita: `VE:`, `Grupo vacunado:` (subrayado), líneas que terminan en `:`."""
    out = [P(T(prefix, "bold"))] if prefix else []
    for l in g.split("\n"):
        if not l.strip():
            out.append(P())
        elif re.fullmatch(L["grp_re"], l):
            out.append(P(T(l[:-1], "bold", "underline")))
        else:
            m = re.match(r"^([^:\d][^:]*?): (.+)$", l)
            if m and "(95%" not in m.group(1) and "(IC" not in m.group(1):
                out.append(P(T(m.group(1) + ":", "bold"), T(" " + m.group(2))))
            elif l.endswith(":") or l == L["gmt"]:
                out.append(P(T(l, "bold")))
            else:
                out.append(P(T(l)))
    return out


def study_cells(r, L, where, prefix=None):
    ce, cf, cg = L["cols"]
    d, rid = design_cell(r[ce], where)
    return [cell(d), cell(country_cell(r[cf])), cell(results_cell(r[cg], L, prefix))], rid


EVENT_SENTENCE = re.compile(r"(?:^|\n)([^\n]{3,90}?) se midió como", re.M)


def event_name(L, r):
    """Evento de seguridad comparativa (columna D, en inglés). En español se toma la forma traducida de la
    frase «<evento> se midió como…» de la columna I; si no está, queda el nombre en inglés."""
    if L["lang"] == "es" and len(r) > 8:
        m = EVENT_SENTENCE.search(r[8] or "")
        if m:
            return m.group(1).strip()
    return r[3]


def label(L, kind, value):
    return L[kind].get(value, value)


def ordered(rows, idx, preferred):
    vals = list(dict.fromkeys(r[idx] for r in rows))
    return [v for v in preferred if v in vals] + [v for v in vals if v not in preferred]


def outcome_table(L, title, rows, first_hdr, last_hdr, empty_msg, refs, order=None, subgroup=None):
    """Tabla de estudios agrupados por desenlace (celda con rowspan) o por subgrupo (una fila por estudio)."""
    hdr = header_row(first_hdr, *L["hdr"][1:3], last_hdr)
    if not rows:
        return table(title_row(title), hdr, empty_row(empty_msg))
    out = [title_row(title), hdr]
    if subgroup:
        for r in rows:
            cs, rid = study_cells(r, L, f"{r[0]}/{r[1]}/{r[2]}",
                                   label(L, "outcome", r[2]) if subgroup == "prefix" else None)
            refs.append(rid)
            lead = ([P(T(label(L, "group", r[3]), "bold"))] if subgroup == "prefix"
                    else [P(T(label(L, "outcome", r[2]), "bold")), P(T(label(L, "group", r[3])))])
            out.append(row(cell(lead), *cs))
        return table(*out)
    for oc in order:
        sub = [r for r in rows if r[2] == oc]
        for i, r in enumerate(sub):
            cs, rid = study_cells(r, L, f"{r[0]}/{r[1]}/{r[2]}")
            refs.append(rid)
            lead = [P(T(label(L, "outcome", oc), "bold"))]
            if r[3] not in ("Overall",) and subgroup is None and i == 0 and len(set(x[3] for x in sub)) == 1:
                lead.append(P(T(label(L, "group", r[3]))))
            out.append(row(*([cell(lead, rowspan=len(sub))] if i == 0 else []), *cs))
    return table(*out)


def noncomparative_table(L, title, rows, refs):
    out = [title_row(title, 2), header_row(L["ref"], L["nc_desc"])]
    if not rows:
        out.append(empty_row(L["e_nc"], 2))
    ce, cf, _ = L["cols"]
    for r in rows:
        ids = ID40.findall(r[ce])
        if not ids:
            raise ValueError(f"{r[0]}/{r[1]}: no hay [Episte ID] en la celda de referencia")
        refs.append(ids[0])
        inline = []
        for i, l in enumerate(r[cf].split("\n")):
            if i:
                inline.append(HB)
            if l.strip():
                inline.append(T(l))
        out.append(row(cell([P(REF(ids[0]))]), cell([P(*inline)])))
    return table(*out)


def comparative_table(L, title, rows, refs):
    hdr = header_row(*L["hdr"])
    if not rows:
        return table(title_row(title), hdr, empty_row(L["e_comp"]))
    out = [title_row(title), hdr]
    for ev in ordered(rows, 3, []):  # D = nombre del evento
        sub = [r for r in rows if r[3] == ev]
        for i, r in enumerate(sub):
            cs, rid = study_cells(r, L, f"{r[0]}/{r[1]}/{ev}")
            refs.append(rid)
            out.append(row(*([cell([P(T(event_name(L, sub[0]), "bold"))], rowspan=len(sub))] if i == 0 else []), *cs))
    return table(*out)


# ---------------------------------------------------------------- ensayos (características generales)
def derive_trials(rows, L):
    """Nombre, fase, registro y publicaciones desde la columna E (inglés) de las filas de ensayos."""
    found = {}
    for r in rows:
        if r[1] not in ("Clinical efficacy", "Safety", "Immunogenicity"):
            continue
        e = r[4]
        name = e.split("\n")[0].strip()
        t = found.setdefault(name, {"phase": None, "name": name, "registry": None, "refs": []})
        m = re.search(r"Phase (\d(?:/\d)?)", e)
        if m:
            t["phase"] = m.group(1)
        m = REGISTRY.search(e)
        if m:
            t["registry"] = m.group(1)
        for i in ID40.findall(e):
            if i not in t["refs"]:
                t["refs"].append(i)
    return list(found.values())


def trial_block(L, t):
    """Párrafos de un ensayo: nombre, registro y publicaciones."""
    c = [P(T(L["trial"] + t["name"]))]
    if t.get("registry"):
        reg = t["registry"]
        c.append(P(T(L["registry"]), link(reg, "https://clinicaltrials.gov/study/" + reg)
                   if reg.startswith("NCT") else T(reg), T(".")))
    if t.get("refs"):
        inline = [T(L["pubs"])]
        for j, rid in enumerate(t["refs"]):
            if j:
                inline.append(T(";"))
            inline.append(REF(rid))
        inline.append(T("."))
        c.append(P(*inline))
    return c


def trials_doc(L, trials):
    if not trials:
        return {"type": "doc", "content": [P(T(L["e_trials"]))]}
    c = [P(T(L["trials_intro"]))]
    phases = list(dict.fromkeys(t.get("phase") for t in trials))
    phases.sort(key=lambda p: (p is None, str(p)))
    for ph in phases:
        c.append(heading(3, L["phase"].format(n=ph) if ph else L["phase_na"], bold=True))
        for i, t in enumerate(t for t in trials if t.get("phase") == ph):
            if i:
                c.append(P())
            c += trial_block(L, t)
    return {"type": "doc", "content": c}


# ---------------------------------------------------------------- armado de las cuatro secciones
def build(rows, vaccine, lang="en", name=None, trials=None, allow_empty=False):
    """rows: filas A:K de Tablas_capa_1. Devuelve ({clave_sección: doc}, [ids de referencia], [avisos])."""
    L = LANG[lang]
    x = name or vaccine
    warn, refs = [], []
    mine = [list(r) + [""] * (11 - len(r)) for r in rows if r and r[0] == vaccine]
    if not mine and not allow_empty:
        names = sorted({r[0] for r in rows if r})
        raise ValueError(f"No hay filas de «{vaccine}». Nombres en las filas: {names}. "
                         "Si es correcto que no tenga estudios, usa --allow-empty")
    if not mine:
        warn.append("Sin filas: todas las tablas llevan el texto estándar de «no hay estudios»")
    skipped = sorted({r[1] for r in mine if r[1] not in
                      ("Effectiveness", "Clinical efficacy", "Safety", "Immunogenicity", "Post-authorization safety")})
    if skipped:
        warn.append(f"Secciones sin tabla en SK (no se suben): {', '.join(skipped)}")
    S = lambda sec: [r for r in mine if r[1] == sec]
    general = lambda sec: [r for r in S(sec) if r[3] == "Overall"]
    subgrp = lambda sec: [r for r in S(sec) if r[3] != "Overall"]
    post = S("Post-authorization safety")
    if lang == "es" and not any(r[7] for r in mine):
        warn.append("Las columnas H:J (español) están vacías")

    imm = general("Immunogenicity")
    ab = [r for r in imm if r[2] == "Antibody response"]
    cellr = [r for r in imm if r[2] == "Cellular response"]
    imm_t = table(title_row(L["t_imm"].format(x=x)), header_row(*L["hdr"]))
    for oc, rs, msg in (("Antibody response", ab, L["e_ab"]), ("Cellular response", cellr, L["e_cell"])):
        if rs:
            imm_t["content"] += outcome_table(L, "", rs, "", "", None, refs, order=[oc])["content"][2:]
        else:
            imm_t["content"].append(empty_row(msg, first=label(L, "outcome", oc)))

    eff = general("Clinical efficacy")
    effect = S("Effectiveness")
    saf = general("Safety")
    docs = {
        "efficacy": {"type": "doc", "content": [
            heading(3, L["h_eff"]), imm_t,
            outcome_table(L, L["t_eff"].format(x=x), eff, L["hdr"][0], L["efficacy_col"], L["e_eff"], refs,
                          order=ordered(eff, 2, EFF_ORDER)),
            heading(3, L["h_eff_sub"]),
            outcome_table(L, L["t_eff_sub"].format(x=x), subgrp("Clinical efficacy"), L["sub_outcome"],
                          L["efficacy_col"], L["e_eff_sub"], refs, subgroup="outcome"),
            heading(3, L["h_effect"]),
            outcome_table(L, L["t_effect"].format(x=x), effect, L["hdr"][0], L["hdr"][3], L["e_effect"], refs,
                          order=ordered(effect, 2, EFF_ORDER))]},
        "safety": {"type": "doc", "content": [
            outcome_table(L, L["t_saf"].format(x=x), saf, L["hdr"][0], L["hdr"][3], L["e_saf"], refs,
                          order=ordered(saf, 2, SAFETY_ORDER)),
            outcome_table(L, L["t_saf_sub"].format(x=x), subgrp("Safety"), L["subgroup"], L["hdr"][3],
                          L["e_saf_sub"], refs, subgroup="prefix")]},
        "post": {"type": "doc", "content": [
            heading(3, L["h_comp"]),
            comparative_table(L, L["t_comp"].format(x=x), [r for r in post if r[2] == "Comparative"], refs),
            heading(3, L["h_nc"]),
            noncomparative_table(L, L["t_nc"].format(x=x), [r for r in post if r[2] == "Non-comparative"], refs)]},
    }
    if trials is None:
        trials = derive_trials(mine, L)
        for t in trials:
            if not t["registry"]:
                warn.append(f"Ensayo «{t['name']}» sin registro (NCT): agregarlo con --trials desde las columnas "
                            "NCT de Efficacy/Immunogenicity")
            if not t["phase"]:
                warn.append(f"Ensayo «{t['name']}» sin fase: sale como «{L['phase_na']}»")
    docs["trials"] = trials_doc(L, trials)
    return docs, list(dict.fromkeys(refs + [i for t in trials for i in t.get("refs", [])])), warn


# ---------------------------------------------------------------- utilidades de lectura
def txt(n):
    t = n.get("type")
    if t == "text":
        return n["text"]
    if t == "hardBreak":
        return " / "
    if t == "reference":
        return "<REF>"
    return "".join(txt(c) for c in n.get("content", []))


def counts(doc):
    s = json.dumps(doc)
    return {"tablas": s.count('"type": "table"'), "citas": s.count('"type": "reference"'),
            "sin_estudios": len(re.findall(
                r'"text": "(?:No studies|No comparative|No non-comparative|There are no|No se identificaron|No hay)', s))}


def preview(docs, width=100):
    for k in SECTION_ORDER:
        print(f"== {k}")
        for n in docs[k]["content"]:
            if n["type"] == "table":
                for r in n["content"]:
                    print("   |", " || ".join(
                        ((str(c['attrs']['rowspan']) + "r ") if c["attrs"]["rowspan"] > 1 else "")
                        + " ¶ ".join(txt(p) for p in c.get("content", []))[:width] for c in r.get("content", [])))
                print()
            else:
                print(n["type"], txt(n)[:width])


# ---------------------------------------------------------------- API de SK
def token():
    t = os.environ.get("SK_TOKEN", "").strip()
    if not t:
        sys.exit("Falta SK_TOKEN (valor de la cookie `sk:token` de una sesión abierta en skplatform.org).")
    try:
        exp = json.loads(base64.urlsafe_b64decode(t.split(".")[1] + "==")).get("exp", 0)
        if exp and exp < time.time():
            sys.exit("El token de SK expiró: abre sesión de nuevo y copia otra vez la cookie `sk:token`.")
    except (IndexError, ValueError):
        pass
    return t


def gql(query, variables=None):
    req = urllib.request.Request(
        API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"content-type": "application/json", "authorization": "Bearer " + token()})
    out = json.load(urllib.request.urlopen(req, timeout=60))
    if "errors" in out:
        raise RuntimeError(json.dumps(out["errors"])[:400])
    return out["data"]


def synthesis_id(arg):
    m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", arg)
    if not m:
        sys.exit("No encuentro el ID de la síntesis (UUID) en: " + arg)
    return m.group(0)


def section_ids(lang):
    names = [SECTIONS[k][lang] for k in SECTION_ORDER]
    d = gql("query($n:[String!]!){reports_reports_section(where:{name:{_in:$n}}){id name}}", {"n": names})
    out = {}
    for k in SECTION_ORDER:
        hit = [s["id"] for s in d["reports_reports_section"] if s["name"] == SECTIONS[k][lang]]
        if len(hit) != 1:
            sys.exit(f"La sección «{SECTIONS[k][lang]}» tiene {len(hit)} coincidencias en SK (se esperaba 1)")
        out[k] = hit[0]
    return out


def state(sid, sec_ids):
    d = gql("""query($s:uuid!){sk_syntheses_by_pk(id:$s){id name}
      reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){id section_id updated_at}
      sk_synthesis_references(where:{synthesis_id:{_eq:$s}}){reference_id}}""", {"s": sid})
    if not d["sk_syntheses_by_pk"]:
        sys.exit("La síntesis no existe o no tienes acceso")
    return d


def cmd_inspect(a):
    sid = synthesis_id(a.synthesis)
    names = {s["id"]: s["name"] for s in gql("{reports_reports_section{id name}}")["reports_reports_section"]}
    d = state(sid, None)
    print(d["sk_syntheses_by_pk"]["name"], "|", sid)
    for r in sorted(d["reports_synthesis_reports"], key=lambda r: names.get(r["section_id"], "")):
        print("  ", names.get(r["section_id"], r["section_id"]), r["updated_at"][:10])
    print("   referencias:", len(d["sk_synthesis_references"]))


def cmd_build(a):
    rows = json.load(open(a.rows, encoding="utf-8"))
    trials = json.load(open(a.trials, encoding="utf-8")) if a.trials else None
    if a.lang == "es" and not a.name:
        sys.exit("En español hace falta --name, p. ej. «Vimkunya contra chikungunya» (como en las síntesis de referencia)")
    try:
        docs, refs, warn = build(rows, a.vaccine, a.lang, a.name, trials, a.allow_empty)
    except ValueError as e:
        sys.exit(str(e))
    json.dump({"vaccine": a.vaccine, "lang": a.lang, "docs": docs, "refs": refs},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    if a.preview:
        preview(docs)
    for k in SECTION_ORDER:
        print(f"{k:9}", counts(docs[k]))
    print("referencias:", len(refs))
    for w in warn:
        print("AVISO:", w)
    print("->", a.out)


def cmd_upload(a):
    payload = json.load(open(a.docs, encoding="utf-8"))
    lang, docs, refs = payload["lang"], payload["docs"], payload["refs"]
    sid = synthesis_id(a.synthesis)
    secs = section_ids(lang)
    only = [k.strip() for k in a.only.split(",")] if a.only else SECTION_ORDER
    if not set(only) <= set(SECTION_ORDER):
        sys.exit("--only acepta: " + ", ".join(SECTION_ORDER))
    d = state(sid, secs)
    print("Síntesis:", d["sk_syntheses_by_pk"]["name"])
    existing = {r["section_id"]: r["id"] for r in d["reports_synthesis_reports"]}
    clash = [k for k in only if secs[k] in existing]
    if clash and not a.replace:
        sys.exit("Ya existen reportes en: " + ", ".join(SECTIONS[k][lang] for k in clash) +
                 ". No se sobrescribe sin --replace (revisa antes con `inspect`).")
    have = {r["reference_id"] for r in d["sk_synthesis_references"]}
    new_refs = [r for r in refs if r not in have]
    print(f"Referencias nuevas: {len(new_refs)} de {len(refs)}; reportes a crear: "
          f"{len(only) - len(clash)}, a reemplazar: {len(clash)}")
    if a.dry_run:
        print("(dry-run: no se escribió nada)")
        return
    if new_refs:
        gql("mutation($o:[sk_synthesis_references_insert_input!]!){insert_sk_synthesis_references(objects:$o){affected_rows}}",
            {"o": [{"synthesis_id": sid, "reference_id": r, "type": "references_manager_epistemonikos",
                    "source": "epistemonikos", "type_identifier": r} for r in new_refs]})
    for k in clash:
        gql("mutation($id:uuid!,$c:json!){update_reports_synthesis_reports_by_pk(pk_columns:{id:$id},_set:{content:$c}){id}}",
            {"id": existing[secs[k]], "c": docs[k]})
    todo = [k for k in only if k not in clash]
    if todo:
        gql("mutation($o:[reports_synthesis_reports_insert_input!]!){insert_reports_synthesis_reports(objects:$o){affected_rows}}",
            {"o": [{"synthesis_id": sid, "section_id": secs[k], "content": docs[k]} for k in todo]})
    # verificación: releer y comparar tablas y citas
    d2 = gql("""query($s:uuid!){reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){section_id content}
      sk_synthesis_references_aggregate(where:{synthesis_id:{_eq:$s}}){aggregate{count}}}""", {"s": sid})
    got = {r["section_id"]: counts(r["content"]) for r in d2["reports_synthesis_reports"]}
    ok = True
    for k in only:
        want, have_c = counts(docs[k]), got.get(secs[k])
        flag = "OK " if have_c and have_c["tablas"] == want["tablas"] and have_c["citas"] == want["citas"] else "ERROR"
        ok &= flag == "OK "
        print(f"{flag} {SECTIONS[k][lang]}: {have_c}")
    n_refs = d2["sk_synthesis_references_aggregate"]["aggregate"]["count"]
    print("referencias en la síntesis:", n_refs)
    if not ok:
        sys.exit("La verificación falló: revisa la síntesis antes de dar la carga por buena")

def merge_module():
    """sk_merge vive al lado de este archivo; con `python3 -I` el directorio del script no está en sys.path."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    sys.modules.setdefault("sk_upload", sys.modules[__name__])
    import sk_merge
    return sk_merge


def read_state(sid, secs):
    d = gql("""query($s:uuid!){sk_syntheses_by_pk(id:$s){id name}
      reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){id section_id updated_at content}
      sk_synthesis_references(where:{synthesis_id:{_eq:$s}}){reference_id}}""", {"s": sid})
    if not d["sk_syntheses_by_pk"]:
        sys.exit("La síntesis no existe o no tienes acceso")
    by = {r["section_id"]: r for r in d["reports_synthesis_reports"]}
    return d, by, {k: (by[secs[k]]["content"] if secs[k] in by else None) for k in SECTION_ORDER}


def cmd_sync(a):
    """Agrega a la síntesis solo lo nuevo de Tablas_capa_1, sin borrar nada de lo que ya está."""
    M = merge_module()
    rows = json.load(open(a.rows, encoding="utf-8"))
    trials = json.load(open(a.trials, encoding="utf-8")) if a.trials else None
    if a.lang == "es" and not a.name:
        sys.exit("En español hace falta --name, p. ej. «Vimkunya contra chikungunya»")
    sid, secs = synthesis_id(a.synthesis), section_ids(a.lang)
    d, by, existing = read_state(sid, secs)
    try:
        out, log, refs, warn = M.sync_plan(rows, a.vaccine, a.lang, a.name, trials, existing,
                                           a.include_flagged, a.add_missing_tables, a.allow_empty)
    except ValueError as e:
        sys.exit(str(e))
    print("Síntesis:", d["sk_syntheses_by_pk"]["name"])
    print("\n".join(log))
    for w in warn:
        print("AVISO:", w)
    have = {r["reference_id"] for r in d["sk_synthesis_references"]}
    new_refs = [r for r in refs if r not in have]
    print(f"\nSecciones a escribir: {len(out)}; referencias nuevas: {len(new_refs)}")
    if not out:
        print("Nada nuevo: la síntesis ya tiene todo lo que hay en las filas.")
        return
    if a.dry_run:
        print("(dry-run: no se escribió nada)")
        return
    os.makedirs(a.backup_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for k in out:
        if existing[k] is not None:
            path = os.path.join(a.backup_dir, f"sk_{sid[:8]}_{k}_{a.lang}_{stamp}.json")
            json.dump(existing[k], open(path, "w", encoding="utf-8"), ensure_ascii=False)
            print("copia de seguridad:", path)
    if new_refs:
        gql("mutation($o:[sk_synthesis_references_insert_input!]!){insert_sk_synthesis_references(objects:$o){affected_rows}}",
            {"o": [{"synthesis_id": sid, "reference_id": r, "type": "references_manager_epistemonikos",
                    "source": "epistemonikos", "type_identifier": r} for r in new_refs]})
    failed = []
    for k, doc in out.items():
        if existing[k] is None:
            gql("mutation($o:[reports_synthesis_reports_insert_input!]!){insert_reports_synthesis_reports(objects:$o){affected_rows}}",
                {"o": [{"synthesis_id": sid, "section_id": secs[k], "content": doc}]})
            continue
        r = by[secs[k]]
        n = gql("""mutation($id:uuid!,$ts:timestamptz!,$c:json!){update_reports_synthesis_reports(
          where:{id:{_eq:$id},updated_at:{_eq:$ts}},_set:{content:$c}){affected_rows}}""",
                {"id": r["id"], "ts": r["updated_at"], "c": doc})["update_reports_synthesis_reports"]["affected_rows"]
        if n != 1:
            failed.append(SECTIONS[k][a.lang])
    if failed:
        print("CONFLICTO: alguien editó estas secciones mientras tanto y no se tocaron:", ", ".join(failed),
              "(vuelve a correr sync)")
    # verificación: nada de lo anterior se perdió y lo nuevo está
    d2, by2, after = read_state(sid, secs)
    ok = not failed
    for k, doc in out.items():
        if SECTIONS[k][a.lang] in failed:
            continue
        got, before = after[k], existing[k]
        lost = set(M.collect_refs(before or {})) - set(M.collect_refs(got or {}))
        missing = set(M.collect_refs(doc)) - set(M.collect_refs(got or {}))
        flag = "OK " if got and not lost and not missing and counts(got)["tablas"] >= counts(before or {})["tablas"] else "ERROR"
        ok &= flag == "OK "
        print(f"{flag} {SECTIONS[k][a.lang]}: {counts(got) if got else None}")
        for rl, lead, sid_ in M.find_duplicates(got or {}):
            print(f"AVISO ID duplicado en tabla {rl}: «{lead}» {sid_}")
    if not ok:
        sys.exit("La verificación falló: revisa la síntesis (hay copia de seguridad en " + a.backup_dir + ")")


def cmd_check(a):
    """Revisa IDs duplicados y citas rotas de una síntesis (solo lectura)."""
    M = merge_module()
    sid = synthesis_id(a.synthesis)
    names = {s["id"]: s["name"] for s in gql("{reports_reports_section{id name}}")["reports_reports_section"]}
    d = gql("""query($s:uuid!){sk_syntheses_by_pk(id:$s){name}
      reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){section_id content}
      sk_synthesis_references(where:{synthesis_id:{_eq:$s}}){reference_id}}""", {"s": sid})
    print(d["sk_syntheses_by_pk"]["name"])
    regs = [r["reference_id"] for r in d["sk_synthesis_references"]]
    dup_regs = sorted({r for r in regs if regs.count(r) > 1})
    cited, problems = set(), 0
    for r in d["reports_synthesis_reports"]:
        cited |= set(M.collect_refs(r["content"]))
        for role, lead, rid in M.find_duplicates(r["content"]):
            problems += 1
            what = "" if role == "nc" else f"«{lead}» "
            print(f"  DUPLICADO en «{names.get(r['section_id'], r['section_id'])}» ({role}): {what}{rid}")
    for r in dup_regs:
        problems += 1
        print(f"  DUPLICADO en las referencias de la síntesis: {r} ({regs.count(r)} veces)")
    for r in sorted(cited - set(regs)):
        problems += 1
        print(f"  CITA ROTA (no está en las referencias de la síntesis): {r}")
    unused = sorted(set(regs) - cited)
    print(f"  referencias registradas: {len(set(regs))}; citadas en reportes: {len(cited & set(regs))}; "
          f"sin citar: {len(unused)}")
    print("  Sin problemas." if not problems else f"  {problems} problema(s).")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--rows", required=True, help="JSON con las filas A:K de Tablas_capa_1")
    b.add_argument("--vaccine", required=True, help="Nombre exacto de la columna A, p. ej. «Gardasil 4 HPV vaccine»")
    b.add_argument("--lang", choices=["en", "es"], default="en")
    b.add_argument("--name", help="Nombre en los títulos (obligatorio en español): «Vimkunya contra chikungunya»")
    b.add_argument("--trials", help="JSON [{phase,name,registry,refs}] si no sale de las filas")
    b.add_argument("--out", required=True)
    b.add_argument("--allow-empty", action="store_true", help="Vacuna sin filas: tablas estándar de «no hay estudios»")
    b.add_argument("--preview", action="store_true")
    b.set_defaults(fn=cmd_build)
    u = sub.add_parser("upload")
    u.add_argument("--docs", required=True, help="Salida de build")
    u.add_argument("--synthesis", required=True, help="URL o UUID de la síntesis de SK")
    u.add_argument("--replace", action="store_true", help="Reemplaza reportes existentes de esas secciones")
    u.add_argument("--only", help="Solo estas secciones, separadas por coma: trials,efficacy,safety,post")
    u.add_argument("--dry-run", action="store_true")
    u.set_defaults(fn=cmd_upload)
    sy = sub.add_parser("sync", help="Agrega solo lo nuevo a una síntesis ya poblada, sin borrar nada")
    sy.add_argument("--rows", required=True)
    sy.add_argument("--vaccine", required=True)
    sy.add_argument("--lang", choices=["en", "es"], default="en")
    sy.add_argument("--name")
    sy.add_argument("--trials")
    sy.add_argument("--synthesis", required=True)
    sy.add_argument("--allow-empty", action="store_true")
    sy.add_argument("--include-flagged", action="store_true", help="Agrega también las filas «para revisar»")
    sy.add_argument("--add-missing-tables", action="store_true",
                    help="Si la sección no tiene una tabla del tipo, agrega la tabla estándar")
    sy.add_argument("--backup-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "backups"))
    sy.add_argument("--dry-run", action="store_true")
    sy.set_defaults(fn=cmd_sync)
    ck = sub.add_parser("check", help="IDs duplicados y citas rotas de una síntesis (solo lectura)")
    ck.add_argument("synthesis")
    ck.set_defaults(fn=cmd_check)
    i = sub.add_parser("inspect")
    i.add_argument("synthesis")
    i.set_defaults(fn=cmd_inspect)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
