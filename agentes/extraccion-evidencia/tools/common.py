"""Utilidades compartidas: carga de listas y formateo numérico."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = json.loads((ROOT / "schemas" / "lists.json").read_text(encoding="utf-8"))

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def fecha_es(d):
    """date -> '28 Octubre 2026' (formato de la columna K de Tablas_capa_1)."""
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def num(x):
    """Número o texto numérico -> texto limpio sin ceros sobrantes ('85.4', '90')."""
    if x is None or x == "":
        return ""
    if isinstance(x, (int, float)):
        return f"{x:g}"
    return str(x).strip()


def es_num(text):
    """Convierte un texto numérico en inglés a formato español: 85.4 -> 85,4; 85,050 -> 85.050.
    Solo toca tokens numéricos; el resto del texto queda igual."""
    def fix(m):
        s = m.group(0)
        if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", s):          # miles con coma
            ent, _, dec = s.partition(".")
            return ent.replace(",", ".") + ("," + dec if dec else "")
        return s.replace(".", ",")
    return re.sub(r"\d[\d,]*\.?\d*", fix, text)


AGE_PATTERNS = [
    (re.compile(r"^(\d+) (years?|months?) (and older|or older)$"), lambda m: f"{m[1]} {'años' if m[2].startswith('year') else 'meses'} o más"),
    (re.compile(r"^(\d+) (years?|months?) (and younger|or younger)$"), lambda m: f"{m[1]} {'años' if m[2].startswith('year') else 'meses'} o menos"),
    (re.compile(r"^(\d+) to (\d+) (years?|months?)$"), lambda m: f"{m[1]} a {m[2]} {'años' if m[3].startswith('year') else 'meses'}"),
    (re.compile(r"^all ages$"), lambda m: "todas las edades"),
    (re.compile(r"^NR$"), lambda m: "NR"),
]


def age_es(age):
    for pat, fn in AGE_PATTERNS:
        m = pat.match(age.strip())
        if m:
            return fn(m)
    return None
