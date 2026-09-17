# GS-Servicios-Digitales

Archivo de clientes del Kit QR. Una carpeta por comercio, servida con GitHub Pages.

| Cliente | Página | Contenido |
|---|---|---|
| Cliente demo (Bar Central, ficticio) | https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/ · [carta](https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/carta/) · [web](https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/web/) · [turnos](https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/turnos/) | `config.json`, `index.html`, `carta/`, `web/`, `turnos/`, `carteles/` |

Estructura por cliente:

```
<slug>/
  index.html          página de links publicada
  config.json         datos para regenerar la página
  carta/              menú o catálogo digital (config.json + index.html)
  web/                mini web de presentación (config.json + fotos/ + index.html)
  turnos/             reservas online (config.json + index.html; backend en _tools/turnos/)
  google/             relevamiento y kit del perfil de Google Maps
  alta-<servicio>.md  plantilla completada por el cliente (alta-qr-links, alta-menu-digital,
                      alta-catalogo, alta-mini-web, alta-perfil-google, alta-turnos)
  carteles/           PDF (imprimir) y PNG (WhatsApp) de cada cartel QR
```

Cada servicio arranca por su alta: se le manda al cliente la plantilla de `_plantillas/docx/`,
se transcribe lo que devuelve en `<slug>/alta-<servicio>.md` y la skill trabaja desde ahí.
Ver `_plantillas/alta-cliente.md` (índice y método) y `_skills/README.md`.

Herramientas en `_tools/`:

```
python3 _tools/pagina_links.py <slug>/config.json <slug>/index.html --standalone
python3 _tools/pagina_menu.py <slug>/carta/config.json <slug>/carta/index.html
python3 _tools/pagina_web.py <slug>/web/config.json <slug>/web/index.html
python3 _tools/pagina_turnos.py <slug>/turnos/config.json <slug>/turnos/index.html   # backend: _tools/turnos/README.md
python3 _tools/auditoria_gbp.py <slug>/google/relevamiento.json <slug>/google/auditoria.md
python3 _tools/cartel_qr.py --nombre "Nombre" --tipo links --url "https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/" --out <slug>/carteles/cartel-links-<slug>.pdf
python3 _tools/plantillas_docx.py                                                   # regenera _plantillas/docx/*.docx desde los .md
```
