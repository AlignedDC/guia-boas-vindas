"""Gera data.js a partir de places.json e carimba a versao no index.html.

Duas coisas:

1. O site le data.js por <script>, nao por fetch(), para abrir tambem com
   duplo clique no index.html (file:// bloqueia fetch, nao bloqueia script).

2. O GitHub Pages serve tudo com max-age=600, e cada arquivo expira por
   conta propria. Sem versao na URL, da para receber o index.html novo com o
   app.js velho ainda em cache — o script antigo procura um elemento que nao
   existe mais, quebra, e a pagina aparece vazia. O ?v=<hash> muda a URL
   sempre que o conteudo muda, entao os tres nunca ficam desencontrados.

    python build.py
"""
import hashlib
import json
import re

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

VERSIONADOS = ["styles.css", "data.js", "app.js"]

h = hashlib.md5()
for nome in VERSIONADOS:
    with open(nome, "rb") as f:
        h.update(f.read())
versao = h.hexdigest()[:8]

with open("index.html", encoding="utf-8") as f:
    html = f.read()

for nome in VERSIONADOS:
    padrao = re.compile(r'(?P<attr>href|src)="' + re.escape(nome) + r'(\?v=[^"]*)?"')
    html, n = padrao.subn(lambda m: '%s="%s?v=%s"' % (m.group("attr"), nome, versao), html)
    if n == 0:
        raise SystemExit("index.html nao referencia %s — versao nao aplicada" % nome)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html: versao ?v=%s" % versao)
