#!/usr/bin/env python3
"""Copia las secciones de efectos de una síntesis de SK (inglés) a otra síntesis traducida (portugués).

  export  <síntesis EN> <dir>     baja eficacia/seguridad/post-autorización y escribe <dir>/en.json y
                                  <dir>/units.json (textos a traducir, sin repetir, por párrafo)
  apply   <dir>                   arma <dir>/pt.json con <dir>/units_pt.json y valida (misma estructura,
                                  mismas citas, mismos números)
  upload  <síntesis PT> <dir> [--dry-run]
                                  registra las referencias que faltan y crea las 3 secciones (solo si no
                                  existen; nunca reemplaza) y relee para verificar

Token en SK_TOKEN, como en sk_upload.py. Formato de units.json: {"u12": ["texto", "texto"...]}, una lista por
párrafo con los nodos de texto en orden; la traducción conserva el largo de cada lista (los cortes marcan
negritas y enlaces). Las citas (nodos `reference`) y los saltos de línea no se tocan.
"""
import argparse
import copy
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sk_upload as S  # noqa: E402

SECS = {  # clave -> (nombre en inglés, nombre en portugués)
    "efficacy": ("Vaccine efficacy and effectiveness", "Eficácia e efetividade da vacina"),
    "safety": ("Vaccine safety", "Segurança da vacina"),
    "post": ("Post-authorization safety", "Segurança pós-autorização"),
}
INLINE_PARENTS = {"paragraph", "heading"}
LETTER = re.compile(r"[A-Za-z]")
NUM = re.compile(r"\d+(?:[.,]\d+)*")
# número en formato inglés (1,234.5 / 0.25) que no es parte de un código (B.1.1.7, 10.1056/..., v1.0)
EN_NUM = re.compile(r"(?<![A-Za-z0-9_.,/])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+)(?![0-9]|[.,]\d|/)")
SWAP = str.maketrans({",": ".", ".": ","})


def br_numbers(s):
    """1,234.5 -> 1.234,5 (formato brasileño)."""
    return EN_NUM.sub(lambda m: m.group(1).translate(SWAP), s)


def section_ids():
    names = [n for pair in SECS.values() for n in pair]
    d = S.gql("query($n:[String!]!){reports_reports_section(where:{name:{_in:$n}}){id name}}", {"n": names})
    by = {}
    for s in d["reports_reports_section"]:
        by.setdefault(s["name"], []).append(s["id"])
    out = {}
    for k, (en, pt) in SECS.items():
        for lang, n in (("en", en), ("pt", pt)):
            if len(by.get(n, [])) != 1:
                sys.exit(f"La sección «{n}» tiene {len(by.get(n, []))} coincidencias en SK")
            out[(k, lang)] = by[n][0]
    return out


def blocks(node):
    """Nodos con contenido en línea (párrafos y títulos), en orden."""
    if node.get("type") in INLINE_PARENTS:
        yield node
        return
    for c in node.get("content", []) or []:
        yield from blocks(c)


def texts(block):
    return [n for n in block.get("content", []) or [] if n.get("type") == "text"]


def key(strings):
    return json.dumps(strings, ensure_ascii=False)


def fetch(sid):
    d = S.gql("""query($s:uuid!){sk_syntheses_by_pk(id:$s){id name}
      reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){id section_id content updated_at}
      sk_synthesis_references(where:{synthesis_id:{_eq:$s}}){reference_id}}""", {"s": sid})
    if not d["sk_syntheses_by_pk"]:
        sys.exit("La síntesis no existe o no tienes acceso: " + sid)
    return d


def cmd_export(a):
    sid = S.synthesis_id(a.synthesis)
    ids = section_ids()
    d = fetch(sid)
    by = {r["section_id"]: r["content"] for r in d["reports_synthesis_reports"]}
    docs, missing = {}, []
    for k in SECS:
        c = by.get(ids[(k, "en")])
        if c is None:
            missing.append(SECS[k][0])
        else:
            docs[k] = c if isinstance(c, dict) else json.loads(c)
    units, seen = {}, {}
    for k, doc in docs.items():
        for b in blocks(doc):
            strings = [t["text"] for t in texts(b)]
            if not strings or not LETTER.search("".join(strings)):
                continue
            kk = key(strings)
            if kk not in seen:
                seen[kk] = f"u{len(seen) + 1}"
                units[seen[kk]] = strings
    os.makedirs(a.dir, exist_ok=True)
    json.dump({"synthesis": sid, "name": d["sk_syntheses_by_pk"]["name"], "docs": docs,
               "refs": sorted({r["reference_id"] for r in d["sk_synthesis_references"]})},
              open(os.path.join(a.dir, "en.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(units, open(os.path.join(a.dir, "units.json"), "w"), ensure_ascii=False, indent=1)
    words = sum(len(s.split()) for v in units.values() for s in v)
    print(f"{d['sk_syntheses_by_pk']['name']}: secciones {list(docs)}; unidades {len(units)}; palabras {words}")
    if missing:
        print("SIN SECCIÓN en inglés:", ", ".join(missing))


def cited(doc):
    return re.findall(r'"referenceId": "([0-9a-f]{40})"', json.dumps(doc))


def shape(node):
    """Estructura sin texto: para comparar EN y PT."""
    if node.get("type") == "text":
        return ("text", json.dumps(node.get("marks"), sort_keys=True))
    return (node.get("type"), json.dumps(node.get("attrs"), sort_keys=True),
            tuple(shape(c) for c in node.get("content", []) or []))


def nums(s):
    return sorted(x.replace(",", "").replace(".", "") for x in NUM.findall(s))


def cmd_apply(a):
    en = json.load(open(os.path.join(a.dir, "en.json"), encoding="utf-8"))
    units = json.load(open(os.path.join(a.dir, "units.json"), encoding="utf-8"))
    tr = json.load(open(os.path.join(a.dir, "units_pt.json"), encoding="utf-8"))
    lookup, problems, warn = {}, [], []
    for u, src in units.items():
        dst = tr.get(u)
        if dst is None:
            problems.append(f"{u}: sin traducción")
            continue
        if len(dst) != len(src):
            problems.append(f"{u}: {len(src)} trozos en inglés y {len(dst)} en la traducción")
            continue
        if nums("".join(src)) != nums("".join(dst)):
            warn.append(f"{u}: números distintos\n    EN {''.join(src)[:300]}\n    PT {''.join(dst)[:300]}")
        lookup[key(src)] = dst
    out = {}
    for k, doc in en["docs"].items():
        doc2 = copy.deepcopy(doc)
        for b in blocks(doc2):
            tn = texts(b)
            strings = [t["text"] for t in tn]
            if not strings or not LETTER.search("".join(strings)):
                continue
            dst = lookup.get(key(strings))
            if dst is None:
                continue
            for t, s in zip(tn, dst):
                t["text"] = br_numbers(s) if a.numbers == "br" else s
        for b in blocks(doc2):  # el editor no acepta nodos de texto vacíos
            if "content" in b:
                b["content"] = [n for n in b["content"] if not (n.get("type") == "text" and n["text"] == "")]
                if not b["content"]:
                    del b["content"]
        if cited(doc2) != cited(doc):
            problems.append(f"{k}: las citas cambiaron")
        out[k] = doc2
    for w in warn:
        print("AVISO", w)
    if problems:
        print("\n".join("ERROR " + p for p in problems))
        sys.exit(1)
    refs = sorted({r for d in out.values() for r in cited(d)})
    json.dump({"docs": out, "refs": refs}, open(os.path.join(a.dir, "pt.json"), "w"), ensure_ascii=False, indent=1)
    print(f"pt.json listo: secciones {list(out)}, citas {sum(len(cited(d)) for d in out.values())}, "
          f"referencias {len(refs)}, avisos {len(warn)}")


def cmd_upload(a):
    sid = S.synthesis_id(a.synthesis)
    ids = section_ids()
    pt = json.load(open(os.path.join(a.dir, "pt.json"), encoding="utf-8"))
    d = fetch(sid)
    print("Síntesis:", d["sk_syntheses_by_pk"]["name"])
    have_secs = {r["section_id"] for r in d["reports_synthesis_reports"]}
    cur = {r["section_id"]: r for r in d["reports_synthesis_reports"]}
    todo = [k for k in pt["docs"] if ids[(k, "pt")] not in have_secs]
    replace = {}
    if a.replace_if_unchanged:  # solo secciones que siguen idénticas a lo que subió esta herramienta
        prev = json.load(open(a.replace_if_unchanged, encoding="utf-8"))["docs"]
        for k in pt["docs"]:
            r = cur.get(ids[(k, "pt")])
            if r is None or k not in prev:
                continue
            c = r["content"] if isinstance(r["content"], dict) else json.loads(r["content"])
            if c == prev[k]:
                replace[k] = r["id"]
            else:
                print(f"AVISO {SECS[k][1]}: cambió desde la subida anterior (alguien la editó); no se reemplaza")
    skip = [k for k in pt["docs"] if k not in todo and k not in replace]
    have = {r["reference_id"] for r in d["sk_synthesis_references"]}
    new_refs = [r for r in pt["refs"] if r not in have]
    if replace:
        print(f"secciones a reemplazar (sin ediciones desde la subida anterior): {[SECS[k][1] for k in replace]}")
    print(f"secciones a crear: {[SECS[k][1] for k in todo]}; ya existen (no se tocan): {[SECS[k][1] for k in skip]}")
    print(f"referencias nuevas: {len(new_refs)} de {len(pt['refs'])}")
    if a.dry_run:
        print("(dry-run: no se escribió nada)")
        return
    if new_refs:
        S.gql("mutation($o:[sk_synthesis_references_insert_input!]!){insert_sk_synthesis_references(objects:$o)"
              "{affected_rows}}",
              {"o": [{"synthesis_id": sid, "reference_id": r, "type": "references_manager_epistemonikos",
                      "source": "epistemonikos", "type_identifier": r} for r in new_refs]})
    if todo:
        S.gql("mutation($o:[reports_synthesis_reports_insert_input!]!){insert_reports_synthesis_reports(objects:$o)"
              "{affected_rows}}",
              {"o": [{"synthesis_id": sid, "section_id": ids[(k, "pt")], "content": pt["docs"][k]} for k in todo]})
    for k, rid in replace.items():
        S.gql("mutation($id:uuid!,$c:json!){update_reports_synthesis_reports_by_pk(pk_columns:{id:$id},"
              "_set:{content:$c}){id}}", {"id": rid, "c": pt["docs"][k]})
    d2 = fetch(sid)
    got = {r["section_id"]: r["content"] for r in d2["reports_synthesis_reports"]}
    refs2 = {r["reference_id"] for r in d2["sk_synthesis_references"]}
    ok = True
    for k in todo + list(replace):
        c = got.get(ids[(k, "pt")])
        c = json.loads(c) if isinstance(c, str) else c
        good = c is not None and shape(c) == shape(pt["docs"][k])
        ok &= good
        print(("OK    " if good else "ERROR ") + SECS[k][1], S.counts(c) if c else "no está")
    broken = [r for k in pt["docs"] for r in cited(pt["docs"][k]) if r not in refs2]
    if broken:
        ok = False
        print("ERROR citas sin referencia:", sorted(set(broken)))
    dup = [r["reference_id"] for r in d2["sk_synthesis_references"]]
    if len(dup) != len(set(dup)):
        print("AVISO referencias duplicadas en la síntesis")
    print("referencias en la síntesis:", len(refs2))
    if not ok:
        sys.exit("La verificación falló")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(required=True)
    e = sub.add_parser("export")
    e.add_argument("synthesis")
    e.add_argument("dir")
    e.set_defaults(fn=cmd_export)
    ap = sub.add_parser("apply")
    ap.add_argument("dir")
    ap.add_argument("--numbers", choices=["br", "en"], default="br",
                    help="br: 1.234,5 (por defecto); en: deja los números como en inglés")
    ap.set_defaults(fn=cmd_apply)
    u = sub.add_parser("upload")
    u.add_argument("synthesis")
    u.add_argument("dir")
    u.add_argument("--dry-run", action="store_true")
    u.add_argument("--replace-if-unchanged", metavar="PT_ANTERIOR.json",
                   help="Reemplaza las secciones que siguen idénticas a ese pt.json (subida anterior de esta herramienta)")
    u.set_defaults(fn=cmd_upload)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
