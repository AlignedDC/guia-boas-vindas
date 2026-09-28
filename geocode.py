"""Preenche lat/lng em places.json via Nominatim (OpenStreetMap).

Roda uma vez, grava as coordenadas no proprio places.json e nao precisa
rodar de novo — o site publicado nunca chama geocodificacao.

    python geocode.py
"""
import json
import time
import urllib.parse
import urllib.request

FILE = "places.json"
UA = "guia-boas-vindas/1.0 (ODATA internal office guide)"
ENDPOINT = "https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=br&q="


def lookup(query):
    req = urllib.request.Request(ENDPOINT + urllib.parse.quote(query), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if not data:
        return None, None
    return float(data[0]["lat"]), float(data[0]["lon"])


def main():
    with open(FILE, encoding="utf-8") as f:
        doc = json.load(f)

    targets = [doc["office"]]
    for section in doc["sections"]:
        targets.extend(section["places"])

    for item in targets:
        if item.get("lat") is not None or not item.get("query"):
            continue
        try:
            lat, lng = lookup(item["query"])
        except Exception as exc:  # rede, rate limit, etc
            print("ERRO   %-45s %s" % (item["name"][:45], exc))
            time.sleep(1.2)
            continue
        item["lat"], item["lng"] = lat, lng
        print("%-6s %-45s %s, %s" % ("ok" if lat else "SEM", item["name"][:45], lat, lng))
        time.sleep(1.2)  # politica de uso do Nominatim: 1 req/s

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
