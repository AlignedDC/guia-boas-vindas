"""Corrige as coordenadas que o geocode.py errou.

O Nominatim devolve o primeiro palpite, que para 'Avenida Brigadeiro Faria
Lima, 1912' caiu em Guarulhos. Aqui pedimos varios candidatos e escolhemos
o que bate com a distancia que o proprio guia afirma — a distancia e o
criterio de desempate, nao a ordem do resultado.

    python fix_geocode.py
"""
import json
import math
import re
import time
import urllib.parse
import urllib.request

FILE = "places.json"
UA = "guia-boas-vindas/1.0 (ODATA internal office guide)"
BASE = "https://nominatim.openstreetmap.org/search?format=json&countrycodes=br&limit=8&"

# Iguatemi veio certo do geocode inicial e o guia diz que fica a 190 m do
# escritorio — serve de ancora para validar o endereco-base.
ANCORA_IGUATEMI = (-23.5771992, -46.6880485)
RAIO_MAX = 5000  # nada no guia passa de 1,5 km; 5 km ja e folga generosa


def get(params):
    url = BASE + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    time.sleep(1.2)
    return [(float(c["lat"]), float(c["lon"]), c.get("display_name", "")) for c in out]


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def metros(texto):
    if not texto:
        return None
    t = texto.replace("–", "-").replace("—", "-")
    m = re.search(r"([\d.,]+)\s*(km|m)", t.split("-")[0].strip() or t)
    if not m:
        return None
    v = float(m.group(1).replace(".", "").replace(",", "."))
    return v * 1000 if m.group(2) == "km" else v


def achar_escritorio():
    tentativas = [
        {"street": "2407 Alameda Gabriel Monteiro da Silva", "city": "Sao Paulo", "state": "SP"},
        {"q": "Alameda Gabriel Monteiro da Silva 2407, Jardim Paulistano, Sao Paulo"},
        {"q": "Alameda Gabriel Monteiro da Silva 2407, Sao Paulo"},
    ]
    melhor = None
    for p in tentativas:
        for lat, lng, nome in get(p):
            d = haversine((lat, lng), ANCORA_IGUATEMI)
            print("   cand %8.0f m do Iguatemi  %s" % (d, nome[:70]))
            if melhor is None or abs(d - 190) < abs(melhor[3] - 190):
                melhor = (lat, lng, nome, d)
    return melhor


def main():
    with open(FILE, encoding="utf-8") as f:
        doc = json.load(f)

    print("escritorio:")
    esc = achar_escritorio()
    if esc and esc[3] < 900:
        doc["office"]["lat"], doc["office"]["lng"] = esc[0], esc[1]
        print("   -> %s, %s (%.0f m do Iguatemi)\n" % (esc[0], esc[1], esc[3]))
    else:
        print("   -> NAO RESOLVIDO, mantido\n")

    base = (doc["office"]["lat"], doc["office"]["lng"])

    for section in doc["sections"]:
        for p in section["places"]:
            dito = metros(p.get("dist"))
            if not p.get("query") or dito is None:
                continue
            atual = haversine(base, (p["lat"], p["lng"])) if p.get("lat") is not None else None
            if atual is not None and (abs(atual - dito) <= 350 or atual <= dito * 1.4):
                continue  # ja esta coerente

            cands = get({"q": p["query"]})
            viaveis = [(c, haversine(base, (c[0], c[1]))) for c in cands]
            viaveis = [(c, d) for c, d in viaveis if d <= RAIO_MAX]
            if not viaveis:
                print("SEM CANDIDATO  %-42s (antes %s m)" % (p["name"][:42], int(atual) if atual else "-"))
                p["lat"] = p["lng"] = None
                continue
            (lat, lng, nome), dist = min(viaveis, key=lambda t: abs(t[1] - dito))
            p["lat"], p["lng"] = lat, lng
            print("corrigido      %-42s %5.0f m dito / %5.0f m novo" % (p["name"][:42], dito, dist))

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
