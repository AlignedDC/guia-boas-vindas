"""Confere as distancias e as coordenadas de places.json.

Desde 2026-09-30 o guia mostra distancia real a pe, nao linha reta, entao
a conferencia mudou. Sao quatro invariantes:

1. o texto em `dist` tem que ser o mesmo numero de `m_pe`;
2. `m_reta` tem que bater com a haversine calculada da coordenada — e o que
   pega coordenada trocada;
3. a caminhada nunca pode ser menor que a linha reta;
4. razao a pe / linha reta acima de 3x e suspeita: ou o pino esta do lado
   errado de uma barreira, ou o roteador nao achou travessia.

    python validate.py
"""
import json
import math
import re

FILE = "places.json"
RAZAO_SUSPEITA = 3.0
TOLERANCIA_RETA = 5  # metros


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def metros(texto):
    if not texto:
        return None
    m = re.search(r"([\d.,]+)\s*(km|m)", texto)
    if not m:
        return None
    v = float(m.group(1).replace(".", "").replace(",", "."))
    return v * 1000 if m.group(2) == "km" else v


def main():
    with open(FILE, encoding="utf-8") as f:
        doc = json.load(f)
    base = (doc["office"]["lat"], doc["office"]["lng"])
    print("base: %s\n" % doc["office"]["address"])

    ok, problemas, sem_pino, sem_rota = 0, [], [], []

    for secao in doc["sections"]:
        for p in secao["places"]:
            nome = p["name"]
            if p.get("lat") is None:
                sem_pino.append(nome)
                continue
            if p.get("m_pe") is None:
                sem_rota.append(nome)
                continue

            falhas = []
            if abs((metros(p["dist"]) or 0) - p["m_pe"]) > 10:
                falhas.append("texto %s nao bate com m_pe %d" % (p["dist"], p["m_pe"]))

            reta = haversine(base, (p["lat"], p["lng"]))
            if abs(reta - p["m_reta"]) > TOLERANCIA_RETA:
                falhas.append("m_reta %d, coordenada da %.0f m" % (p["m_reta"], reta))
            if p["m_pe"] < p["m_reta"] - TOLERANCIA_RETA:
                falhas.append("a pe %d < linha reta %d" % (p["m_pe"], p["m_reta"]))
            razao = p["m_pe"] / max(1, p["m_reta"])
            if razao > RAZAO_SUSPEITA:
                falhas.append("razao %.2fx" % razao)

            if falhas:
                problemas.append((nome, falhas))
            else:
                ok += 1

    print("%d conferem" % ok)
    if problemas:
        print("\n%d com problema:" % len(problemas))
        for nome, falhas in problemas:
            print("  %-44s %s" % (nome[:44], " | ".join(falhas)))
    if sem_rota:
        print("\n%d sem rota a pe (rode routes.py): %s" % (len(sem_rota), ", ".join(sem_rota)))
    if sem_pino:
        print("\n%d sem pino: %s" % (len(sem_pino), ", ".join(sem_pino)))


if __name__ == "__main__":
    main()
