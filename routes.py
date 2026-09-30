"""Troca a distancia em linha reta pela distancia real a pe.

Por que: medido em 2026-09-30 nos 49 lugares do guia, a caminhada e em
mediana 1,39x a linha reta, e ate 2,42x no Shopping Iguatemi — 235 m em
linha reta viram 567 m a pe, porque e preciso atravessar a Faria Lima.
Prometer "3 min" para uma caminhada de 7 min e o tipo de erro que a pessoa
percebe na primeira vez que tenta.

Roteador: instancia publica do Valhalla da FOSSGIS, sobre dados do
OpenStreetMap. Sem chave, sem cadastro. Roda uma vez e grava o resultado no
places.json — o site publicado nao chama roteador nenhum.

    python routes.py

Grava em cada lugar:
    dist     "567 m"   texto exibido, agora a pe
    walk     "7 min"   tempo estimado pelo proprio roteador
    m_pe     567       metros a pe, para o validate.py conferir
    m_reta   235       metros em linha reta, idem
"""
import json
import math
import time
import urllib.request

FILE = "places.json"
ENDPOINT = "https://valhalla1.openstreetmap.de/route"
UA = "guia-boas-vindas/1.0 (ODATA internal office guide)"
PAUSA = 1.0  # instancia publica e gentileza nossa


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def rotear(origem, destino):
    corpo = {
        "locations": [{"lat": origem[0], "lon": origem[1]},
                      {"lat": destino[0], "lon": destino[1]}],
        "costing": "pedestrian",
        "units": "kilometers",
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        resumo = json.load(r)["trip"]["summary"]
    return resumo["length"] * 1000, resumo["time"] / 60


def texto(metros):
    return ("%.2f km" % (metros / 1000)).replace(".", ",") if metros >= 1000 else "%d m" % round(metros)


def main():
    with open(FILE, encoding="utf-8") as f:
        doc = json.load(f)
    base = (doc["office"]["lat"], doc["office"]["lng"])

    falhas = []
    for secao in doc["sections"]:
        for p in secao["places"]:
            if p.get("lat") is None:
                continue
            reta = haversine(base, (p["lat"], p["lng"]))
            try:
                pe, minutos = rotear(base, (p["lat"], p["lng"]))
            except Exception as exc:
                falhas.append((p["name"], str(exc)))
                time.sleep(PAUSA)
                continue
            p["dist"] = texto(pe)
            p["walk"] = "%d min" % max(1, round(minutos))
            p["m_pe"] = round(pe)
            p["m_reta"] = round(reta)
            print("%-44s %7s a pe  (reta %5.0f m, %.2fx)" % (p["name"][:44], p["dist"], reta, pe/reta))
            time.sleep(PAUSA)

        secao["places"].sort(key=lambda p: p.get("m_pe", 9e9))

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if falhas:
        print("\nSEM ROTA — mantiveram o valor anterior:")
        for nome, erro in falhas:
            print("   %-44s %s" % (nome[:44], erro[:40]))


if __name__ == "__main__":
    main()
