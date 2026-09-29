/* Guia de boas-vindas — ODATA
   Le window.GUIA (data.js) e monta cartoes + mapa. Sem build, sem framework. */

(function () {
  "use strict";

  var G = window.GUIA;

  var COR = {
    comer: "#ee3968",
    cafeterias: "#f8991d",
    mercados: "#33d592",
    shopping: "#3e92ea",
    academia: "#FDD835",
    farmacias: "#7751A9",
    correios: "#e6e7e8",
    estacionamento: "#A267D8",
    transporte: "#4CAF50"
  };

  var estado = { categoria: "todos", busca: "", ativo: null };
  var itens = [];          // {p, secao, marker, card}
  var map, camadaPinos;

  /* ---------- utilidades ---------- */

  function semAcento(s) {
    return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function linkMaps(p) {
    var alvo = p.query || (p.name + ", Sao Paulo");
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(alvo);
  }

  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }

  function icone(svg) {
    var s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("viewBox", "0 0 24 24");
    s.setAttribute("fill", "none");
    s.setAttribute("stroke", "currentColor");
    s.setAttribute("stroke-width", "2");
    s.innerHTML = svg;
    return s;
  }

  var SVG_PIN = '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 1118 0z"/><circle cx="12" cy="10" r="3"/>';
  var SVG_LISTA = '<path d="M9 20l-6-3V4l6 3m0 13l6-3m-6 3V7m6 10l6 3V7l-6-3m0 13V4m0 0L9 7"/>';

  /* ---------- cabecalho ---------- */

  function montarTopo() {
    document.getElementById("hero-address").textContent = G.office.address;
    document.getElementById("footnote").textContent = G.footnote;

    var cta = document.getElementById("hero-cta");

    var rota = el("a", "btn btn-primary");
    rota.href = "https://www.google.com/maps/dir/?api=1&destination=" + encodeURIComponent(G.office.query);
    rota.target = "_blank";
    rota.rel = "noopener";
    rota.appendChild(icone(SVG_PIN));
    rota.appendChild(document.createTextNode("Como chegar"));
    cta.appendChild(rota);

    // Listas com secao aparecem dentro dela, em montarLista(). Uma lista sem
    // secao valeria para o guia inteiro e cairia aqui — hoje nao existe.
    (G.mapsLists || []).filter(function (l) { return !l.section; }).forEach(function (lista) {
      var a = el("a", "btn btn-ghost");
      a.href = lista.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.appendChild(icone(SVG_LISTA));
      a.appendChild(document.createTextNode(lista.label));
      cta.appendChild(a);
    });
  }

  /* ---------- filtros ---------- */

  function montarChips() {
    var box = document.getElementById("chips");
    var defs = [{ key: "todos", title: "Todos", cor: "#ffffff", n: 0 }];
    G.sections.forEach(function (s) {
      defs.push({ key: s.key, title: s.title, cor: COR[s.key], n: s.places.length });
      defs[0].n += s.places.length;
    });

    defs.forEach(function (d) {
      var b = el("button", "chip");
      b.type = "button";
      b.dataset.key = d.key;
      b.setAttribute("aria-pressed", d.key === "todos" ? "true" : "false");
      if (d.key !== "todos") {
        var dot = el("span", "dot");
        dot.style.background = d.cor;
        b.appendChild(dot);
      }
      b.appendChild(document.createTextNode(d.title));
      b.appendChild(el("span", "count", String(d.n)));
      b.addEventListener("click", function () {
        estado.categoria = d.key;
        Array.prototype.forEach.call(box.children, function (c) {
          c.setAttribute("aria-pressed", c.dataset.key === d.key ? "true" : "false");
        });
        aplicar();
      });
      box.appendChild(b);
    });

    document.getElementById("busca").addEventListener("input", function (e) {
      estado.busca = semAcento(e.target.value.trim());
      aplicar();
    });
  }

  /* ---------- cartoes ---------- */

  function montarCartao(p, secao) {
    var card = el("article", "card");
    card.style.setProperty("--cat", COR[secao.key]);
    if (p.highlight) card.classList.add("highlight");
    if (p.warn) card.classList.add("warn");

    if (p.tag) {
      var t = el("span", "tag", p.tag);
      card.appendChild(t);
    }

    var top = el("div", "card-top");
    top.appendChild(el("h3", null, p.name));
    var dist = [p.dist, p.walk].filter(Boolean).join(" · ");
    if (dist) top.appendChild(el("span", "dist", "≈ " + dist));
    card.appendChild(top);

    card.appendChild(el("p", "desc", p.desc));
    if (p.addr) card.appendChild(el("p", "addr", p.addr));

    var go = el("a", "go");
    go.href = linkMaps(p);
    go.target = "_blank";
    go.rel = "noopener";
    go.appendChild(icone(SVG_PIN));
    go.appendChild(document.createTextNode("Ver no Maps"));
    go.addEventListener("click", function (e) { e.stopPropagation(); });
    card.appendChild(go);

    return card;
  }

  function montarLista() {
    var raiz = document.getElementById("lista");

    G.sections.forEach(function (s) {
      var sec = el("section", "section");
      sec.id = "sec-" + s.key;

      var head = el("div", "section-head");
      head.appendChild(el("span", "section-num", s.num));
      head.appendChild(el("h2", null, s.title));
      sec.appendChild(head);
      if (s.intro) sec.appendChild(el("p", "intro", s.intro));

      (G.mapsLists || []).forEach(function (lista) {
        if (lista.section !== s.key) return;
        var a = el("a", "section-maps");
        a.href = lista.url;
        a.target = "_blank";
        a.rel = "noopener";
        a.appendChild(icone(SVG_LISTA));
        a.appendChild(document.createTextNode(lista.label));
        sec.appendChild(a);
      });

      var grid = el("div", "cards");
      s.places.forEach(function (p) {
        var card = montarCartao(p, s);
        grid.appendChild(card);
        itens.push({ p: p, secao: s, card: card, marker: null });
      });
      sec.appendChild(grid);
      raiz.appendChild(sec);
    });

    var vazio = el("div", "empty", "Nenhum lugar encontrado");
    vazio.id = "vazio";
    vazio.hidden = true;
    raiz.appendChild(vazio);
  }

  /* ---------- mapa ---------- */

  function montarMapa() {
    map = L.map("map", { scrollWheelZoom: false, zoomControl: true })
           .setView([G.office.lat, G.office.lng], 15);

    // OpenStreetMap: sem chave de API e sem prazo de validade. O tema escuro
    // vem de um filtro CSS em .leaflet-tile (styles.css) — a CARTO passou a
    // exigir chave e devolve tile com marca d'agua.
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(map);

    L.marker([G.office.lat, G.office.lng], {
      icon: L.divIcon({ className: "", html: '<div class="pin-office"></div>', iconSize: [22, 22], iconAnchor: [11, 11] }),
      zIndexOffset: 1000,
      title: G.office.name
    }).addTo(map).bindPopup("<strong>" + G.office.name + "</strong>" + G.office.address);

    camadaPinos = L.layerGroup().addTo(map);

    itens.forEach(function (it) {
      if (it.p.lat == null) return;
      var cor = COR[it.secao.key];
      it.marker = L.marker([it.p.lat, it.p.lng], {
        icon: L.divIcon({
          className: "",
          html: '<div class="pin" style="background:' + cor + '"></div>',
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        }),
        title: it.p.name
      });

      var html = "<strong>" + it.p.name + "</strong>" +
        '<div class="p-dist">≈ ' + [it.p.dist, it.p.walk].filter(Boolean).join(" · ") + "</div>" +
        (it.p.addr ? "<div>" + it.p.addr + "</div>" : "") +
        '<div style="margin-top:8px"><a href="' + linkMaps(it.p) + '" target="_blank" rel="noopener">Ver no Maps</a></div>';
      it.marker.bindPopup(html);

      it.marker.on("click", function () {
        destacar(it, true);
      });

      it.card.addEventListener("click", function () {
        destacar(it, false);
        map.flyTo([it.p.lat, it.p.lng], 17, { duration: 0.6 });
        it.marker.openPopup();
      });
    });
  }

  function destacar(it, rolar) {
    itens.forEach(function (o) {
      o.card.classList.remove("is-active");
      if (o.marker) {
        var d = o.marker.getElement() && o.marker.getElement().querySelector(".pin");
        if (d) d.classList.remove("is-active");
      }
    });
    it.card.classList.add("is-active");
    if (it.marker && it.marker.getElement()) {
      var dot = it.marker.getElement().querySelector(".pin");
      if (dot) dot.classList.add("is-active");
    }
    if (rolar) it.card.scrollIntoView({ behavior: "smooth", block: "center" });
    estado.ativo = it;
  }

  /* ---------- aplicar filtro ---------- */

  function visivel(it) {
    if (estado.categoria !== "todos" && it.secao.key !== estado.categoria) return false;
    if (!estado.busca) return true;
    var alvo = semAcento([it.p.name, it.p.desc, it.p.addr, it.secao.title].join(" "));
    return alvo.indexOf(estado.busca) !== -1;
  }

  function aplicar() {
    var n = 0;
    var bounds = L.latLngBounds([[G.office.lat, G.office.lng]]);

    camadaPinos.clearLayers();
    itens.forEach(function (it) {
      var v = visivel(it);
      it.card.hidden = !v;
      if (v) {
        n++;
        if (it.marker) {
          camadaPinos.addLayer(it.marker);
          bounds.extend(it.marker.getLatLng());
        }
      }
    });

    G.sections.forEach(function (s) {
      var sec = document.getElementById("sec-" + s.key);
      var algum = itens.some(function (it) { return it.secao.key === s.key && !it.card.hidden; });
      sec.hidden = !algum;
    });

    document.getElementById("vazio").hidden = n > 0;
    document.getElementById("map-note").textContent = n + " de " + itens.length + " locais";

    if (n > 0) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
  }

  /* ---------- inicio ---------- */

  montarTopo();
  montarChips();
  montarLista();
  montarMapa();
  aplicar();
})();
