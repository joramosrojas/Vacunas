#!/usr/bin/env python3
"""Corrige texto puntual en secciones ya publicadas de síntesis de SK, sin tocar nada más.

  python3 tools/sk_fix.py <edits.json> [--dry-run] [--backup-dir DIR]

edits.json: lista de ediciones
  {"synthesis": "<uuid>", "section": "<nombre de la sección en SK>", "op": "replace",
   "old": "texto exacto", "new": "texto nuevo", "count": 2}      # count = ocurrencias esperadas (por defecto, >=1)
  Cualquier edición acepta "within": "<texto>" para actuar solo en la celda que contiene ese texto.
  {"synthesis": ..., "section": ..., "op": "drop_paragraph", "text": "texto completo del párrafo", "count": 1}
  {"synthesis": ..., "section": ..., "op": "text_to_ref", "id": "<Episte ID>", "count": 1}
      el nodo de texto «[<id>]» (cita escrita como texto) pasa a ser una cita real; registra la referencia si falta

Los reemplazos se hacen dentro de un mismo nodo de texto (no cruzan negritas ni citas). Si una edición no encuentra
exactamente `count` ocurrencias, NO se escribe nada de esa sección. Copia previa en work/backups/; la escritura se
condiciona a que la sección no haya cambiado desde que se leyó; después se relee y se verifica.
Token en SK_TOKEN.
"""
import argparse
import copy
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sk_upload as S  # noqa: E402


def text_nodes(node):
    if node.get("type") == "text":
        yield node
    for c in node.get("content", []) or []:
        yield from text_nodes(c)


def paragraphs(node, parent=None):
    if node.get("type") in ("paragraph", "heading"):
        yield node, parent
        return
    for c in node.get("content", []) or []:
        yield from paragraphs(c, node)


def ptext(p):
    return "".join(n.get("text", "") for n in p.get("content", []) or [] if n.get("type") == "text")


def full_text(node):
    if node.get("type") == "text":
        return node["text"]
    return "".join(full_text(c) for c in node.get("content", []) or [])


def cells_within(doc, needle):
    """Celdas de tabla (o párrafos fuera de tablas) cuyo texto contiene `needle`."""
    out = []

    def walk(n, in_cell):
        if n.get("type") in ("tableCell", "tableHeader"):
            if needle in full_text(n):
                out.append(n)
            return
        if n.get("type") in ("paragraph", "heading") and not in_cell:
            if needle in full_text(n):
                out.append(n)
            return
        for c in n.get("content", []) or []:
            walk(c, in_cell)
    walk(doc, False)
    return out


def apply(doc, e):
    """Aplica una edición a doc (in situ). Devuelve el número de ocurrencias tratadas.
    Con "within": "<texto>", solo dentro de las celdas (o párrafos sueltos) que contienen ese texto."""
    if e.get("within"):
        sub = {k: v for k, v in e.items() if k != "within"}
        return sum(apply(c, sub) for c in cells_within(doc, e["within"]))
    op = e.get("op", "replace")
    n = 0
    if op == "replace":
        for t in text_nodes(doc):
            k = t["text"].count(e["old"])
            if k:
                t["text"] = t["text"].replace(e["old"], e["new"])
                n += k
        return n
    if op == "drop_paragraph":
        for p, parent in list(paragraphs(doc)):
            if parent is not None and ptext(p).strip() == e["text"].strip():
                parent["content"].remove(p)
                n += 1
        return n
    if op == "text_to_ref":
        target = f"[{e['id']}]"

        def walk(node):
            nonlocal n
            c = node.get("content")
            if not c:
                return
            for i, ch in enumerate(c):
                if ch.get("type") == "text" and ch["text"].strip() == target:
                    c[i] = {"type": "reference", "attrs": {"referenceId": e["id"]}}
                    n += 1
                else:
                    walk(ch)
        walk(doc)
        return n
    raise ValueError("op desconocida: " + op)


def cited(doc):
    s = json.dumps(doc)
    return s.count('"type": "reference"')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edits")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backup-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work",
                                                         "backups"))
    a = ap.parse_args()
    edits = json.load(open(a.edits, encoding="utf-8"))
    names = {s["id"]: s["name"] for s in S.gql("{reports_reports_section{id name}}")["reports_reports_section"]}
    groups = {}
    for i, e in enumerate(edits):
        groups.setdefault((e["synthesis"], e["section"]), []).append((i, e))
    ok_all = True
    for (sid, sec), es in groups.items():
        d = S.gql("""query($s:uuid!){sk_syntheses_by_pk(id:$s){name}
          reports_synthesis_reports(where:{synthesis_id:{_eq:$s}}){id section_id updated_at content}
          sk_synthesis_references(where:{synthesis_id:{_eq:$s}}){reference_id}}""", {"s": sid})
        syn = d["sk_syntheses_by_pk"]["name"]
        rep = [r for r in d["reports_synthesis_reports"] if names.get(r["section_id"]) == sec]
        if len(rep) != 1:
            print(f"ERROR {syn} / {sec}: {len(rep)} secciones con ese nombre")
            ok_all = False
            continue
        rep = rep[0]
        before = rep["content"] if isinstance(rep["content"], dict) else json.loads(rep["content"])
        doc = copy.deepcopy(before)
        bad, new_refs = [], []
        for i, e in es:
            n = apply(doc, e)
            want = e.get("count")
            label = e.get("old") or e.get("text") or e.get("id")
            if (want is None and n < 1) or (want is not None and n != want):
                bad.append(f"  edición {i}: «{label[:70]}» encontrada {n} veces (se esperaban {want or '>=1'})")
            if e.get("op") == "text_to_ref" and e["id"] not in {r["reference_id"] for r in d["sk_synthesis_references"]}:
                new_refs.append(e["id"])
        print(f"{'NO SE TOCA' if bad else 'OK  '} {syn} / {sec}: {len(es)} ediciones" + (", " + str(len(set(new_refs))) + " referencias a registrar" if new_refs else ""))
        for b in bad:
            print(b)
        if bad:
            ok_all = False
            continue
        n_text_to_ref = sum(apply(copy.deepcopy(before), e) for _, e in es if e.get("op") == "text_to_ref")
        if cited(doc) != cited(before) + n_text_to_ref:
            print("  ERROR: cambió el número de citas; no se escribe")
            ok_all = False
            continue
        if a.dry_run:
            continue
        os.makedirs(a.backup_dir, exist_ok=True)
        bk = os.path.join(a.backup_dir, f"fix_{sid}_{rep['section_id']}_{time.strftime('%Y%m%d-%H%M%S')}.json")
        json.dump(before, open(bk, "w"), ensure_ascii=False)
        if new_refs:
            S.gql("mutation($o:[sk_synthesis_references_insert_input!]!){insert_sk_synthesis_references(objects:$o)"
                  "{affected_rows}}",
                  {"o": [{"synthesis_id": sid, "reference_id": r, "type": "references_manager_epistemonikos",
                          "source": "epistemonikos", "type_identifier": r} for r in sorted(set(new_refs))]})
        r = S.gql("mutation($id:uuid!,$u:timestamptz!,$c:json!){update_reports_synthesis_reports("
                  "where:{id:{_eq:$id},updated_at:{_eq:$u}},_set:{content:$c}){affected_rows}}",
                  {"id": rep["id"], "u": rep["updated_at"], "c": doc})
        if r["update_reports_synthesis_reports"]["affected_rows"] != 1:
            print("  CONFLICTO: alguien editó la sección mientras tanto; no se escribió")
            ok_all = False
            continue
        d2 = S.gql("query($id:uuid!){reports_synthesis_reports_by_pk(id:$id){content}}", {"id": rep["id"]})
        got = d2["reports_synthesis_reports_by_pk"]["content"]
        got = got if isinstance(got, dict) else json.loads(got)
        if got != doc:
            print("  ERROR: lo releído no coincide con lo escrito (copia en " + bk + ")")
            ok_all = False
        else:
            print("  escrito y verificado (copia previa: " + os.path.basename(bk) + ")")
    if not ok_all:
        sys.exit(1)


if __name__ == "__main__":
    main()
