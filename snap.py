"""Interpola endereco AO LONGO do traçado da rua, nao em linha reta.

A interpolacao em corda entre dois numeros conhecidos erra onde a via faz
curva: medido na Faria Lima, 35 a 68 m de desvio, o suficiente para o pino
cair na rua de tras. Aqui a gente monta a polilinha da via a partir da
geometria do OpenStreetMap, projeta as ancoras nela e caminha pela via.
"""
import math, pickle

R = 6371000.0

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def _xy(p, lat0):
    return (math.radians(p[1])*math.cos(math.radians(lat0))*R, math.radians(p[0])*R)

def montar(segmentos):
    """Costura os segmentos do OSM numa polilinha unica, ponta com ponta."""
    segs = [list(s) for s in segmentos if len(s) > 1]
    linha = segs.pop(0)
    while segs:
        melhor, inverter, ponta, dist = None, False, None, float("inf")
        for i, s in enumerate(segs):
            for ponta_nome, alvo in (("fim", linha[-1]), ("ini", linha[0])):
                for inv, extremo in ((False, s[0]), (True, s[-1])):
                    d = hav(alvo, extremo)
                    if d < dist:
                        melhor, inverter, ponta, dist = i, inv, ponta_nome, d
        if dist > 120:
            break
        s = segs.pop(melhor)
        if inverter:
            s = s[::-1]
        linha = linha + s[1:] if ponta == "fim" else s[:-1] + linha
    return linha

def acumulado(linha):
    acc = [0.0]
    for i in range(1, len(linha)):
        acc.append(acc[-1] + hav(linha[i-1], linha[i]))
    return acc

def projetar(linha, acc, ponto):
    """Distancia ao longo da linha do ponto mais proximo de `ponto`."""
    lat0 = ponto[0]
    px, py = _xy(ponto, lat0)
    melhor = (float("inf"), 0.0)
    for i in range(len(linha)-1):
        ax, ay = _xy(linha[i], lat0)
        bx, by = _xy(linha[i+1], lat0)
        dx, dy = bx-ax, by-ay
        L2 = dx*dx + dy*dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy)/L2))
        qx, qy = ax + t*dx, ay + t*dy
        d = math.hypot(px-qx, py-qy)
        if d < melhor[0]:
            melhor = (d, acc[i] + t*math.sqrt(L2))
    return melhor[1], melhor[0]

def ponto_em(linha, acc, s):
    s = max(0.0, min(acc[-1], s))
    for i in range(1, len(acc)):
        if acc[i] >= s:
            t = 0.0 if acc[i] == acc[i-1] else (s-acc[i-1])/(acc[i]-acc[i-1])
            return (linha[i-1][0] + t*(linha[i][0]-linha[i-1][0]),
                    linha[i-1][1] + t*(linha[i][1]-linha[i-1][1]))
    return linha[-1]

class Via:
    def __init__(self, segmentos, ancoras):
        """ancoras: {numero_do_imovel: (lat, lng)} — pontos confirmados."""
        self.linha = montar(segmentos)
        self.acc = acumulado(self.linha)
        self.anc = sorted((n, projetar(self.linha, self.acc, p)[0]) for n, p in ancoras.items())

    def numero(self, n):
        """Coordenada do numero `n`, caminhando pelo traçado."""
        a = [x for x in self.anc if x[0] <= n] or [self.anc[0]]
        b = [x for x in self.anc if x[0] >= n] or [self.anc[-1]]
        n0, s0 = a[-1]
        n1, s1 = b[0]
        if n0 == n1:
            return ponto_em(self.linha, self.acc, s0)
        t = (n - n0) / (n1 - n0)
        return ponto_em(self.linha, self.acc, s0 + t*(s1 - s0))

def carregar():
    return pickle.load(open("ruas.pkl", "rb"))
