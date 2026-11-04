"""Mezcla incremental: agrega a las secciones que ya existen en SK solo los estudios que faltan.

Principios (ver docs/planillas/sk_platform.md):
  * No se borra ni se reescribe nada de lo que ya está en SK (incluido lo subido antes de este sistema y
    que no está en Tablas_capa_1). Lo único que se quita es la fila de «no hay estudios» de una tabla a la
    que se agrega un estudio.
  * Un estudio ya presente (mismo Episte ID y mismo desenlace/evento/subgrupo en la misma tabla) no se
    vuelve a agregar. Si el Episte ID está en la tabla pero el desenlace no coincide con claridad, la fila
    queda «para revisar» y no se agrega salvo que se pida (include_flagged).
  * Función pura: recibe y devuelve documentos; la red vive en sk_upload.py.
"""
import copy
import json
import re

import sk_upload as S

OUTCOME_ROLES = ("imm", "eff", "effect", "saf", "comp")
SUBGROUP_ROLES = ("eff_sub", "saf_sub")
SECTION_ROLES = {"efficacy": ["imm", "eff", "eff_sub", "effect"], "safety": ["saf", "saf_sub"],
                 "post": ["comp", "nc"]}
PLACEHOLDER = re.compile(r"^(no studies|there are no|no comparative|no non-comparative|no randomized|"
                         r"no se identific|no hay|los datos disponibles|available data)")


# ---------------------------------------------------------------- lectura de tablas existentes
def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip().casefold()


def cell_text(c):
    return " ".join(S.txt(p) for p in c.get("content", []))


def cell_ids(c):
    return re.findall(r'"referenceId": "([0-9a-f]{40})"', json.dumps(c))


def span(c, key="colspan"):
    return (c.get("attrs") or {}).get(key, 1) or 1


def first_par(c):
    ps = c.get("content", [])
    return norm(S.txt(ps[0])) if ps else ""


def classify(table):
    """Función de la tabla según su título: imm, eff, eff_sub, effect, saf, saf_sub, comp, nc (o None)."""
    rows = table.get("content", [])
    if not rows or not rows[0].get("content"):
        return None
    t = norm(cell_text(rows[0]["content"][0]))
    if "booster" in t or "refuerzo" in t:
        return None
    head = norm(cell_text(rows[1]["content"][0])) if len(rows) > 1 and rows[1].get("content") else ""
    sub = ("by subgroup" in t or "por subgrupo" in t
           or head in ("subgroup", "subgrupo", "outcome by subgroup", "outcomes by subgroup", "desenlace por subgrupo"))
    if "post-authorization" in t or "post-autoriz" in t:
        if "non-comparative" in t or "no comparativ" in t:
            return "nc"
        return "comp" if "comparative" in t or "comparativ" in t else None
    if t.startswith(("immunogenicity", "inmunogenicidad")):
        return "imm"
    if t.startswith(("effectiveness", "efectividad")):
        return "effect"
    if t.startswith(("efficacy", "eficacia")):
        return "eff_sub" if sub else "eff"
    if t.startswith(("safety", "seguridad")):
        return "saf_sub" if sub else "saf"
    return None


def scan(table):
    """Una entrada por fila (None para título y encabezado) con el desenlace/subgrupo vigente (rowspan)."""
    rows = table.get("content", [])
    ncols = sum(span(c) for c in rows[1].get("content", [])) if len(rows) > 1 else 4
    out, lead_first, lead_all = [], "", ""
    for i, r in enumerate(rows):
        cs = r.get("content", [])
        if i < 2:
            out.append(None)
            continue
        total = sum(span(c) for c in cs)
        has_lead = bool(cs) and total >= ncols
        if has_lead:
            lead_first, lead_all = first_par(cs[0]), norm(cell_text(cs[0]))
        msg = (len(cs) == 1 and span(cs[0]) == ncols) or (len(cs) == 2 and has_lead and span(cs[1]) == ncols - 1)
        ph = bool(msg and PLACEHOLDER.match(norm(cell_text(cs[-1]))))
        out.append({"i": i, "empty": not cs, "has_lead": has_lead, "lead_first": lead_first,
                    "lead_all": lead_all, "single": len(cs) == 1, "msg": msg, "placeholder": ph,
                    "whole": ph and len(cs) == 1, "ids": [x for c in cs for x in cell_ids(c)],
                    "res_first": first_par(cs[-1]) if cs else "", "text": norm(" ".join(cell_text(c) for c in cs))})
    return {"ncols": ncols, "rows": out}


def structure_ok(table):
    """Columnas y rowspan de la primera columna cuadran (cada fila tiene `ncols` o `ncols-1` columnas)."""
    rows = table.get("content", [])
    if len(rows) < 3:
        return True
    ncols = sum(span(c) for c in rows[1].get("content", []))
    remaining = 0
    for r in rows[2:]:
        cs = r.get("content", [])
        if not cs:
            remaining = max(0, remaining - 1)
            continue
        total = sum(span(c) for c in cs)
        if remaining > 0:
            if total != ncols - 1:
                return False
            remaining -= 1
        else:
            if total != ncols:
                return False
            remaining = span(cs[0], "rowspan") - 1
    return remaining == 0


def data_end(table, info):
    rows = table["content"]
    end = len(rows)
    while end > 2:
        ri = info["rows"][end - 1]
        if ri and (ri["empty"] or (ri["msg"] and not ri["placeholder"] and ri["single"])):
            end -= 1
        else:
            break
    return end


def remove_row(rows, i):
    """Quita una fila (y las filas vacías que su rowspan dejaba cubiertas)."""
    cs = rows[i].get("content", [])
    extra = max((span(c, "rowspan") for c in cs), default=1) - 1
    del rows[i]
    while extra > 0 and i < len(rows) and not rows[i].get("content"):
        del rows[i]
        extra -= 1


# ---------------------------------------------------------------- filas nuevas por función de tabla
def role_rows(mine, role):
    sec = lambda s: [r for r in mine if r[1] == s]
    gen = lambda s: [r for r in sec(s) if r[3] == "Overall"]
    sub = lambda s: [r for r in sec(s) if r[3] != "Overall"]
    post = sec("Post-authorization safety")
    return {"imm": [r for r in gen("Immunogenicity") if r[2] in ("Antibody response", "Cellular response")],
            "eff": gen("Clinical efficacy"), "eff_sub": sub("Clinical efficacy"), "effect": sec("Effectiveness"),
            "saf": gen("Safety"), "saf_sub": sub("Safety"),
            "comp": [r for r in post if r[2] == "Comparative"],
            "nc": [r for r in post if r[2] == "Non-comparative"]}[role]


def who(r):
    m = re.search(r"\[([^\[\]\n]+, \d{4}[^\[\]\n]*)\]", r[4])
    return m.group(1) if m else (S.ID40.findall(r[4]) or ["?"])[0][:8]


def study_id(r):
    ids = S.ID40.findall(r[4])
    return ids[0] if ids else None


def dedupe_incoming(mine, log):
    """Misma sección, desenlace, grupo y Episte ID dos veces en Tablas_capa_1: se queda la primera."""
    seen, out = set(), []
    for r in mine:
        k = (r[1], r[2], r[3], study_id(r))
        if k in seen:
            log.append(f"AVISO fila repetida en Tablas_capa_1 (se ignora la segunda): {r[1]} / {r[2]} / {r[3]} / {who(r)}")
            continue
        seen.add(k)
        out.append(r)
    return out


STANDARD = {norm(v) for k in ("en", "es") for v in list(S.LANG[k]["outcome"].values())} | {
    "antibody response", "cellular response", "contracting disease", "contracting severe disease",
    "any adverse event", "serious adverse events"}


def similar(a, b):
    """Eventos casi iguales (p. ej. «guillain-barré» y «guillain-barré syndrome»)."""
    wa, wb = set(re.findall(r"\w+", a)), set(re.findall(r"\w+", b))
    return bool(a and b and (a in b or b in a or len(wa & wb) / max(1, len(wa | wb)) >= 0.5))


def row_status(info, role, r, L):
    """'new', 'dup' (ya está) o 'flag' (hay algo parecido que no puedo interpretar con certeza).

    Un mismo estudio puede estar en varias filas de una tabla con desenlaces o eventos distintos: eso es
    normal. Es duplicado cuando coinciden Episte ID y desenlace/evento (y subgrupo). Solo se pide revisión si
    el estudio ya está con una etiqueta que no es de las estándar (tablas hechas a mano) o con un evento muy
    parecido.
    """
    sid = study_id(r)
    hits = [ri for ri in info["rows"] if ri and not ri["placeholder"] and sid in ri["ids"]]
    if not hits:
        return "new"
    if role == "nc":
        return "dup"
    oc = norm(r[3] if role == "comp" else S.label(L, "outcome", r[2]))
    grp = norm(S.label(L, "group", r[3]))
    for ri in hits:
        if role in OUTCOME_ROLES:
            match = ri["lead_first"] == oc
        elif role == "eff_sub":
            match = ri["lead_first"] == oc and grp in ri["lead_all"]
        else:  # saf_sub: el grupo va en la primera columna y el desenlace encabeza los resultados
            match = ri["lead_first"] == grp and ri["res_first"] == oc
        if match:
            if role in ("effect", "saf", "eff") and r[3] not in ("Overall",) and grp not in ri["text"]:
                return "flag"
            return "dup"
    if role == "comp":
        return "flag" if any(similar(ri["lead_first"], oc) for ri in hits) else "new"
    if role in SUBGROUP_ROLES:
        return "new"
    return "new" if all(ri["lead_first"] in STANDARD for ri in hits) else "flag"


def render_groups(role, rows, L, refs):
    """Filas de datos recién armadas (sin título ni encabezado), en grupos [(clave, [filas])]."""
    cut = lambda t: t["content"][2:]
    if role in ("eff", "effect", "saf", "imm"):
        pref = {"eff": S.EFF_ORDER, "effect": S.EFF_ORDER, "saf": S.SAFETY_ORDER,
                "imm": ["Antibody response", "Cellular response"]}[role]
        return [(norm(S.label(L, "outcome", oc)),
                 cut(S.outcome_table(L, "", [r for r in rows if r[2] == oc], "", "", None, refs, order=[oc])))
                for oc in S.ordered(rows, 2, pref)]
    if role == "comp":
        return [(norm(ev), cut(S.comparative_table(L, "", [r for r in rows if r[3] == ev], refs)))
                for ev in S.ordered(rows, 3, [])]
    if role in SUBGROUP_ROLES:
        t = cut(S.outcome_table(L, "", rows, "", "", None, refs, subgroup="outcome" if role == "eff_sub" else "prefix"))
        return [(norm(S.label(L, "group", r[3])), [tr]) for r, tr in zip(rows, t)]
    return [(None, [tr]) for tr in cut(S.noncomparative_table(L, "", rows, refs))]


def insert_groups(table, role, groups):
    for key, new in groups:
        info = scan(table)
        rows = table["content"]
        whole = next((ri for ri in info["rows"] if ri and ri["whole"]), None)
        if whole:
            remove_row(rows, whole["i"])
            info = scan(table)
        if role in OUTCOME_ROLES:
            hit = next((ri for ri in info["rows"] if ri and ri["has_lead"] and not ri["empty"]
                        and ri["lead_first"] == key), None)
            if hit and hit["placeholder"]:           # fila «no hay estudios» de ese desenlace (inmunogenicidad)
                remove_row(rows, hit["i"])
                rows[hit["i"]:hit["i"]] = new
            elif hit:                                 # el desenlace ya existe: se agregan filas a su grupo
                end = hit["i"]
                for ri in info["rows"][hit["i"] + 1:]:
                    if ri and not ri["has_lead"] and not ri["empty"]:
                        end = ri["i"]
                    else:
                        break
                new[0]["content"] = new[0]["content"][1:]
                rows[end + 1:end + 1] = new
                rows[hit["i"]]["content"][0].setdefault("attrs", {})["rowspan"] = end - hit["i"] + 1 + len(new)
            else:
                at = data_end(table, info)
                rows[at:at] = new
            continue
        ph = next((ri for ri in info["rows"] if ri and ri["placeholder"] and ri["has_lead"] and not ri["whole"]
                   and key and key in ri["lead_all"]), None) if role in SUBGROUP_ROLES else None
        if ph:
            remove_row(rows, ph["i"])
            rows[ph["i"]:ph["i"]] = new
        else:
            at = data_end(table, info)
            rows[at:at] = new


def merge_role(table, role, rows_new, L, include_flagged, refs, log, label):
    info = scan(table)
    new, dup, flag = [], [], []
    for r in rows_new:
        st = row_status(info, role, r, L)
        (new if st == "new" else dup if st == "dup" else flag).append(r)
    add = new + (flag if include_flagged else [])
    if add:
        insert_groups(table, role, render_groups(role, add, L, refs))
    parts = [f"+{len(add)}" if add else "sin cambios"]
    if dup:
        parts.append(f"{len(dup)} ya estaban")
    log.append(f"  {label}: " + ", ".join(parts))
    for r in add:
        log.append(f"      + {r[2] if role != 'comp' else r[3]} · {who(r)}")
    for r in dup:
        log.append(f"      = ya estaba: {r[2] if role != 'comp' else r[3]} · {who(r)}")
    for r in flag:
        log.append(f"      ? PARA REVISAR ({'se agrega' if include_flagged else 'no se agrega'}): "
                   f"{r[2] if role != 'comp' else r[3]} · {who(r)} — el estudio ya está en la tabla con otro "
                   "desenlace o grupo; revisa a mano")
    return bool(add)


# ---------------------------------------------------------------- ensayos
def phase_key(text):
    m = re.search(r"(\d)", text)
    return int(m.group(1)) if m else 99


def merge_trials(doc, trials, L, log):
    if not trials:
        return False
    body = doc["content"]
    flat = norm(" ".join(S.txt(n) for n in body))
    ids = set(re.findall(r'"referenceId": "([0-9a-f]{40})"', json.dumps(doc)))
    if len(body) <= 1 and PLACEHOLDER.match(flat):            # solo la frase «no hay ensayos»
        doc["content"] = S.trials_doc(L, trials)["content"]
        log.append(f"  ensayos: +{len(trials)} (reemplaza la frase «no hay ensayos»)")
        return True
    changed = False
    for t in trials:
        dup = ((t.get("registry") and norm(t["registry"]) in flat) or norm(t["name"]) in flat
               or (t.get("refs") and all(i in ids for i in t["refs"])))
        if dup:
            log.append(f"  ensayos: = ya estaba: {t['name']}")
            continue
        head = L["phase"].format(n=t["phase"]) if t.get("phase") else L["phase_na"]
        block = S.trial_block(L, t)
        pos = next((i for i, n in enumerate(body) if n["type"] == "heading" and norm(S.txt(n)) == norm(head)), None)
        if pos is not None:
            end = pos + 1
            while end < len(body) and body[end]["type"] != "heading":
                end += 1
            body[end:end] = [S.P()] + block if end > pos + 1 else block
        else:
            k = phase_key(head)
            at = next((i for i, n in enumerate(body) if n["type"] == "heading"
                       and re.match(r"^(phase|fase) ", norm(S.txt(n))) and phase_key(S.txt(n)) > k), len(body))
            body[at:at] = [S.heading(3, head, bold=True)] + block
        log.append(f"  ensayos: + {t['name']} ({head})")
        changed = True
    return changed


# ---------------------------------------------------------------- plan completo
def collect_refs(doc):
    return list(dict.fromkeys(re.findall(r'"referenceId": "([0-9a-f]{40})"', json.dumps(doc))))


def find_duplicates(doc):
    """Pares (desenlace, Episte ID) repetidos dentro de una misma tabla."""
    out = []
    for n in doc.get("content", []):
        role = classify(n) if n.get("type") == "table" else None
        if not role:
            continue
        seen = set()
        for ri in scan(n)["rows"]:
            if not ri or ri["placeholder"]:
                continue
            for sid in dict.fromkeys(ri["ids"]):
                key = (sid,) if role == "nc" else (ri["lead_first"] or ri["lead_all"], ri["lead_all"], sid)
                if key in seen:
                    out.append((role, ri["lead_first"], sid))
                seen.add(key)
    return out


def sync_plan(rows, vaccine, lang, name, trials, existing, include_flagged=False, add_missing=False,
              allow_empty=False):
    """existing: {clave_sección: doc existente o None}. Devuelve (docs a escribir, informe, refs nuevas, avisos)."""
    full, _, warn = S.build(rows, vaccine, lang, name, trials, allow_empty)
    L = S.LANG[lang]
    log = []
    mine = [list(r) + [""] * (11 - len(r)) for r in rows if r and r[0] == vaccine]
    mine = dedupe_incoming(mine, log)
    if trials is None:
        trials = S.derive_trials(mine, L)
    out, refs = {}, []
    for key in S.SECTION_ORDER:
        label = S.SECTIONS[key][lang]
        ex = existing.get(key)
        if ex is None:
            out[key] = full[key]
            refs += collect_refs(full[key])
            log.append(f"{label}: sección NUEVA {S.counts(full[key])}")
            continue
        log.append(f"{label}: sección existente (se agrega solo lo nuevo)")
        doc, changed = copy.deepcopy(ex), False
        before = set(collect_refs(doc))
        if key == "trials":
            changed = merge_trials(doc, trials, L, log)
        else:
            tables = {}
            for n in doc.get("content", []):
                role = classify(n) if n.get("type") == "table" else None
                if role:
                    tables.setdefault(role, []).append(n)
            for role in SECTION_ROLES[key]:
                new_rows = role_rows(mine, role)
                if not new_rows:
                    continue
                nodes = tables.get(role)
                if not nodes:
                    if add_missing:
                        std = next(n for n in full[key]["content"] if n.get("type") == "table" and classify(n) == role)
                        doc["content"].append(copy.deepcopy(std))
                        refs += collect_refs(std)
                        log.append(f"  {role}: tabla estándar agregada (no existía): +{len(new_rows)}")
                        changed = True
                    else:
                        log.append(f"  {role}: NO hay una tabla reconocible en la sección; no se agregan "
                                   f"{len(new_rows)} filas (usa --add-missing-tables o agrégalas a mano)")
                    continue
                if len(nodes) > 1:
                    log.append(f"  {role}: hay {len(nodes)} tablas del mismo tipo; se usa la primera")
                changed |= merge_role(nodes[0], role, new_rows, L, include_flagged, refs, log,
                                      S.txt(nodes[0]["content"][0]["content"][0])[:70])
        if changed:
            bad = [i for i, (a, b) in enumerate(zip([n for n in ex["content"] if n.get("type") == "table"],
                                                    [n for n in doc["content"] if n.get("type") == "table"]))
                   if structure_ok(a) and not structure_ok(b)]
            if bad:
                log.append(f"  ERROR: la mezcla dejó mal la estructura de una tabla de «{label}»; "
                           "la sección NO se modifica (agrega esas filas a mano)")
                continue
            out[key] = doc
            refs += [i for i in collect_refs(doc) if i not in before]
    return out, log, list(dict.fromkeys(refs)), warn
