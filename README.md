# Guia de boas-vindas — novo escritório ODATA

Site estático com os lugares perto da Alameda Gabriel Monteiro da Silva, 2407
(Jardim Europa, São Paulo): onde comer, padarias, mercados, Shopping Iguatemi,
academias, estacionamento e transporte público.

Sem framework, sem build obrigatório, sem back-end. Publicado no GitHub Pages.

## Arquivos

| Arquivo | O que é |
|---|---|
| `index.html` | a página |
| `styles.css` | tema ODATA escuro, tokens tirados de `odatadc.com` |
| `app.js` | cartões, filtros, busca e mapa Leaflet |
| `places.json` | **a fonte da verdade** — todo o conteúdo do guia |
| `data.js` | gerado a partir de `places.json` pelo `build.py` |
| `fonts/` | Galatea em WOFF2, convertida dos OTF licenciados |
| `assets/` | logo ODATA (SVG branco) |

## Como alterar um lugar

1. Edite `places.json`.
2. `python build.py` — regenera `data.js`.
3. Commit e push. O GitHub Pages republica sozinho em cerca de um minuto.

Se você **adicionar** um lugar novo, deixe `"lat"` e `"lng"` de fora e rode:

```powershell
python geocode.py    # busca as coordenadas no OpenStreetMap
python validate.py   # confere as coordenadas contra as distâncias do texto
python build.py
```

## Os scripts

- **`geocode.py`** — preenche `lat`/`lng` de quem ainda não tem, via Nominatim.
- **`validate.py`** — calcula a distância em linha reta do escritório até cada
  lugar e compara com o campo `dist`. Divergência grande = geocodificação errada.
- **`fix_geocode.py`** — quando o Nominatim erra, pede vários candidatos e
  escolhe o que bate com a distância declarada.
- **`build.py`** — escreve `data.js`.

O site lê `data.js` por `<script>`, e não `places.json` por `fetch()`, para que
`index.html` também abra com duplo clique (o `file://` bloqueia `fetch`).

## Ver localmente

```powershell
python -m http.server 8787
# http://127.0.0.1:8787
```

## Coordenadas

28 dos 30 lugares têm pino, todos conferidos contra as distâncias do guia.

- Três endereços da Av. Brig. Faria Lima (1912 e 2092) não existem no
  OpenStreetMap. Foram interpolados entre os números 1853 e 2232, que existem,
  e estão marcados com `"approx": true`.
- **Padoca of Maní · Um Coffee Co. · KOF** e **Bodytech (Av. Rebouças)** não têm
  pino: o guia original não traz o número do endereço. Os cartões aparecem
  normalmente, só não entram no mapa. Para colocá-los, acrescente `lat`/`lng`
  à mão em `places.json`.

## Fonte Galatea

Os WOFF2 em `fonts/` foram convertidos e subsetados (latin + latin-ext) a partir
de `MyFonts Order M10230840.zip`, em
`SGI - Documents\MKT\Identidade Visual\Branding Itens`.

**Aquele pedido é de licença desktop.** Uso em `@font-face` num site público
normalmente exige licença webfont separada. Confirmar com o Marketing antes de
tratar como definitivo.

## Mapa

Tiles do OpenStreetMap, sem chave de API. O visual escuro é um filtro CSS em
`.leaflet-tile`. A CARTO, que seria a opção escura pronta, passou a exigir chave
e devolve tile com marca d'água.
