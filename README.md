# GS-Servicios-Digitales

Archivo de clientes del Kit QR. Una carpeta por comercio, servida con GitHub Pages.

| Cliente | Página | Contenido |
|---|---|---|
| Cliente demo (Bar Central, ficticio) | https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/ | `config.json`, `index.html`, `carteles/` |

Estructura por cliente:

```
<slug>/
  index.html      página de links publicada
  config.json     datos para regenerar la página
  carteles/       PDF (imprimir) y PNG (WhatsApp) de cada cartel QR
```

Herramientas en `_tools/`:

```
python3 _tools/pagina_links.py <slug>/config.json <slug>/index.html --standalone
python3 _tools/cartel_qr.py --nombre "Nombre" --tipo links --url "https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/" --out <slug>/carteles/cartel-links-<slug>.pdf
```
