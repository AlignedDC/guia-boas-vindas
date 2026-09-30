# guia-boas-vindas — notas para a próxima sessão

Site estático do guia do novo escritório ODATA (Al. Gabriel Monteiro da Silva,
2407). Publicado em <https://aligneddc.github.io/guia-boas-vindas/> pelo
GitHub Pages, a partir da branch `main`, raiz do repositório.
Remoto: `AlignedDC/guia-boas-vindas`, **público** — foi o primeiro repositório
público da organização, decisão do Gabriel em 2026-09-28.

## Rode `python build.py` antes de todo commit

Não é opcional e não é só para regenerar `data.js`. O `build.py` também
carimba `?v=<hash do conteúdo>` em `styles.css`, `data.js` e `app.js` dentro do
`index.html`.

**O motivo, medido em 2026-09-28:** o GitHub Pages serve cada arquivo com
`Cache-Control: max-age=600`, contado por arquivo, independente. Um commit que
mexeu no `index.html` e no `app.js` ao mesmo tempo deixou visitantes recebendo
o HTML novo com o JS velho ainda em cache. O script antigo procurou um
elemento que o HTML novo não tinha mais, estourou
`Cannot set properties of null`, e morreu antes de montar qualquer coisa — a
página inteira ficou em branco, não só o pedaço alterado. Reproduzido em
laboratório: 0 cartões, 0 chips.

Com o `?v=`, mudar o conteúdo muda a URL, e o navegador não tem como combinar
versões diferentes. Verificado com perfil de navegador com cache quente: o
visitante que volta carrega tudo novo, sem erro.

Se esquecer, o sintoma não é um erro de build — é a página branca para quem já
visitou antes, e você não vê nada disso numa aba anônima.

## A ordem das categorias é calculada, não é a do arquivo

O `app.js` ordena as seções por quantidade de estabelecimentos, da maior para
a menor, antes de montar a página. Pedido do Gabriel em 2026-09-30. A ordem em
que as seções aparecem no `places.json` só resolve empate — o `sort` do
JavaScript é estável. Não tente reordenar mexendo no arquivo; mexa no
`G.sections.sort` no topo do `app.js`.

## Ciclo de alteração

```powershell
# editar places.json (a fonte da verdade de todo o conteúdo)
python geocode.py     # so se acrescentou lugar sem lat/lng
python routes.py      # se mexeu em coordenada: refaz a distancia a pe
python validate.py    # confere as quatro invariantes
python build.py       # SEMPRE
git add -A; git commit -m "..."; git push
```

## A distância exibida é a pé, não em linha reta

Trocado em 2026-09-30, depois de medir os 49 lugares: a caminhada é em mediana
**1,39x** a linha reta e chega a **2,42x** no Shopping Iguatemi — 235 m de
linha reta viram 567 m a pé, porque é preciso atravessar a Faria Lima. O guia
prometia 3 minutos para uma caminhada de 7.

`routes.py` usa a instância pública do Valhalla da FOSSGIS, com perfil de
pedestre, sem chave e sem cadastro. Roda uma vez e grava `dist`, `walk`,
`m_pe` e `m_reta` no `places.json`; **o site publicado não chama roteador
nenhum**. Se mexer em qualquer coordenada, rode de novo — senão a distância
fica descolada do pino.

`validate.py` confere quatro coisas: o texto de `dist` contra `m_pe`; o
`m_reta` contra a haversine da coordenada (é o que pega coordenada trocada);
que a caminhada nunca é menor que a linha reta; e razão a pé / linha reta
acima de 3x, que denuncia pino do lado errado de uma barreira.

## Armadilhas já pagas neste repositório

- **Nominatim erra e erra com confiança.** `Avenida Brigadeiro Faria Lima, 1912`
  voltou em Guarulhos, 21 km fora. E o próprio endereço-base voltou 1,5 km
  deslocado, o que jogou *todos* os pinos junto. Nunca aceite o primeiro
  resultado: `fix_geocode.py` pede vários candidatos e escolhe o que bate com a
  distância declarada.
- **Vários números da Faria Lima não existem no OpenStreetMap.** São
  interpolados entre dois números que existem e depois **projetados na
  geometria da avenida** (`snap.py`, com `via_fl.pkl`). Estão marcados com
  `"approx": true`. A projeção não é enfeite: interpolar só em linha reta
  errava de 35 a 68 m onde a avenida faz curva, e isso jogou o HIIT Club na
  Rua Jacarezinho e o Carrefour na Rua Agrário de Sousa. Medido em 2026-09-30.
- **Endereço que o Nominatim não acha, procure na web antes de desistir.** O
  Bodytech ficou sem pino por uma sessão inteira porque o guia só dizia "Av.
  Rebouças"; uma busca resolvia — é a unidade Pinheiros, dentro do Eldorado.
- **O site lê `data.js` por `<script>`, não `places.json` por `fetch()`**, para
  que o `index.html` também abra com duplo clique. `file://` bloqueia `fetch`.
- **CARTO não serve mais tile sem chave de API** — devolve tile com marca
  d'água "API KEY REQUIRED". O mapa usa OpenStreetMap com um filtro CSS em
  `.leaflet-tile` para ficar escuro.
- **`[hidden]` perde para `display` de classe.** `.btn { display: inline-flex }`
  anulava o atributo `hidden` e o botão aparecia. Existe um
  `[hidden] { display: none !important }` no topo do `styles.css`; não remova.

## Fonte e marca

- Galatea em `fonts/`, WOFF2 subsetado (latin + latin-ext) a partir de
  `MyFonts Order M10230840.zip`, em
  `SGI - Documents\MKT\Identidade Visual\Branding Itens`.
  **Aquele pedido é licença desktop.** Uso em `@font-face` num site público
  costuma exigir licença webfont separada — pendente com o Marketing.
- Tokens de cor tirados de `odatadc.com/wp-content/uploads/dsmp-assets/theme.css`,
  não estimados de screenshot: `#120720`, `#2e1547`, `#522582`, `#ee3968`,
  `#A267D8`.
- Logo: `assets/odata-logo-white.svg`, extraído de
  `Identidade Visual\NEW ODATA LOGO.zip`.

## Em aberto

- Transporte público é a única seção sem lista do Google Maps; as outras seis têm.
- O guia escreve "Jardim América"; o OpenStreetMap coloca o número 2407 em
  "Jardim Europa". Mantida a redação do Gabriel.
