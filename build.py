"""Gera data.js a partir de places.json.

O site le data.js por <script>, nao por fetch(), para abrir tambem com
duplo clique no index.html (file:// bloqueia fetch, nao bloqueia script).

    python build.py
"""
import json

with open("places.json", encoding="utf-8") as f:
    doc = json.load(f)

with open("data.js", "w", encoding="utf-8") as f:
    f.write("// gerado por build.py a partir de places.json — nao editar a mao\n")
    f.write("window.GUIA = ")
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write(";\n")

total = sum(len(s["places"]) for s in doc["sections"])
pinos = sum(1 for s in doc["sections"] for p in s["places"] if p.get("lat"))
print("data.js: %d secoes, %d locais, %d com pino" % (len(doc["sections"]), total, pinos))
