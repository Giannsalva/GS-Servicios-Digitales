# GS-Servicios-Digitales

Archivo de clientes del Kit QR. Una carpeta por comercio, servida con GitHub Pages.

| Cliente | Página | Contenido |
|---|---|---|
| Cliente demo (Bar Central, ficticio) | https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/ · [carta](https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/carta/) · [web](https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/web/) | `config.json`, `index.html`, `carta/`, `web/`, `carteles/` |

Estructura por cliente:

```
<slug>/
  index.html      página de links publicada
  config.json     datos para regenerar la página
  carta/          menú o catálogo digital (config.json + index.html)
  web/            mini web de presentación (config.json + fotos/ + index.html)
  carteles/       PDF (imprimir) y PNG (WhatsApp) de cada cartel QR
```

Herramientas en `_tools/`:

```
python3 _tools/pagina_links.py <slug>/config.json <slug>/index.html --standalone
python3 _tools/pagina_menu.py <slug>/carta/config.json <slug>/carta/index.html
python3 _tools/pagina_web.py <slug>/web/config.json <slug>/web/index.html
python3 _tools/cartel_qr.py --nombre "Nombre" --tipo links --url "https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/" --out <slug>/carteles/cartel-links-<slug>.pdf
```
