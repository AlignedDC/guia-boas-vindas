"""Confere as coordenadas de places.json contra as distancias do guia.

O rodape do guia diz que as distancias sao em linha reta a partir do
endereco-base, entao a distancia haversine calculada tem que bater com o
texto. O que nao bate esta geocodificado errado.

    python validate.py
"""
import json
import math
import re

FILE = "places.json"
TOLERANCIA = 350  # metros de folga antes de sinalizar


def metros(texto):
    """'1,26 km' -> 1260 ; '850 m' -> 850 ; '1,0-1,4 km' -> 1000 (menor)."""
    if not texto:
        return None
    t = texto.replace("–", "-").replace("—", "-")
    primeiro = t.split("-")[0].strip()
    m = re.search(r"([\d.,]+)\s*(km|m)", primeiro or t)
    if not m:
        return None
    valor = float(m.group(1).replace(".", "").replace(",", "."))
    return valor * 1000 if m.group(2) == "km" else valor


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def main():
    with open(FILE, encoding="utf-8") as f:
        doc = json.load(f)

    office = doc["office"]
    base = (office["lat"], office["lng"])
    print("base: %s  (%s, %s)\n" % (office["address"], base[0], base[1]))

    ruim, sem_pino, ok = [], [], 0
    for section in doc["sections"]:
        for p in section["places"]:
            if p.get("lat") is None:
                sem_pino.append((section["key"], p["name"], "sem coordenada"))
                continue
            calc = haversine(base, (p["lat"], p["lng"]))
            dito = metros(p.get("dist"))
            if dito is None:
                continue
            delta = abs(calc - dito)
            if delta > TOLERANCIA and calc > dito * 1.4:
                ruim.append((section["key"], p["name"], dito, calc))
            else:
                ok += 1

    print("%d conferem" % ok)
    if ruim:
        print("\n%d FORA (guia diz / calculado):" % len(ruim))
        for k, n, d, c in sorted(ruim, key=lambda r: -r[3]):
            print("  %-15s %-44s %6.0f m / %8.0f m" % (k, n[:44], d, c))
    if sem_pino:
        print("\n%d sem pino:" % len(sem_pino))
        for k, n, why in sem_pino:
            print("  %-15s %-44s %s" % (k, n[:44], why))


if __name__ == "__main__":
    main()
