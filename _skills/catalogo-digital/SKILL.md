---
name: catalogo-digital
description: "Menú o catálogo digital a medida para un comercio (carta de bar o restaurante, catálogo de ropa, lista de artículos o servicios), publicado en GitHub Pages con QR y precios editables desde una planilla de Google. Usar cuando Gian pida una carta, menú, catálogo o lista de precios digital para un local."
---

# Menú / catálogo digital

Servicio que Gian vende a negocios de barrio: una página con las categorías y los ítems que el comercio quiera, que se abre desde un QR y se comparte por WhatsApp. Es **a medida**: sirve igual para la carta de un bar, el catálogo de un local de ropa con fotos y talles, la lista de artículos de una ferretería o los servicios y precios de una peluquería. Las categorías son las pestañas de navegación; el cliente define cuáles y cuántas.

Complementa a la skill `cartel-qr`: el hosting, el repo `Giannsalva/GS-Servicios-Digitales`, la carpeta local y el procedimiento de push son los de esa skill y no se repiten acá. Leerla si hace falta subir algo.

## Paso 0: la plantilla del cliente (siempre)

El servicio **arranca por la plantilla de `_plantillas/`**, no por preguntas sueltas.

1. Si el cliente todavía no la completó, mandarle el `.docx` de `_plantillas/docx/`.
2. Cuando la devuelve (archivo, foto o audios de WhatsApp), transcribirla y archivarla como
   `<slug>/alta-menu-digital.md` (o `alta-catalogo.md`) en el repo: ese archivo es la fuente de verdad del cliente.
3. **Leer el alta antes de generar nada.** De ahí salen todos los datos; nunca inventar nombres,
   links, precios ni teléfonos.
4. Lo que quedó vacío se pregunta una sola vez, todo junto, y se completa en el mismo archivo.
   Lo que sigue faltando se marca `PENDIENTE` y no se publica ni se imprime nada que dependa de eso.
5. Si el cliente ya tiene otro servicio contratado, los datos del comercio se copian de su alta
   anterior en vez de volver a pedirlos.

La plantilla depende del rubro: `_plantillas/menu-digital.md` para gastronomía y
`_plantillas/catalogo.md` para productos, servicios o lista de precios.

| Bloque de la plantilla | Dónde va |
|---|---|
| Datos del comercio | `config.json`: `nombre`, `accent`, `whatsapp`, `mensaje` |
| Cómo querés la carta / el catálogo | `tagline`, `detalle` (texto de precios), `cta`, `buscador`, `layout` |
| Etiquetas elegidas | `tags` de los ítems |
| La carta / los productos | `categorias[].items[]` (`nombre`, `desc`, `precio`, `tags`, `variantes`, `foto`) |
| Fotos adjuntas | `<slug>/<carpeta>/fotos/`, redimensionadas a 600 px |
| Planilla de Google + mail | activar la planilla y compartirla a ese mail |
| Carteles con QR | cuántos y de qué tamaño se imprimen |

Transcribir la carta **tal cual vino** y marcar lo ilegible para que el cliente lo confirme antes
de publicar. Si la plantilla dice que los precios cambian seguido, activar sí o sí la planilla.

## Qué pedir antes de generar

Solo lo que falte. Nunca inventar productos, precios ni teléfonos: si el cliente manda una foto de la carta o una lista por WhatsApp, transcribirla tal cual y marcar lo ilegible para que lo confirme.

- **Nombre del comercio** y qué es lo que muestra ("Carta", "Catálogo", "Servicios", "Lista de precios").
- **Categorías e ítems**: nombre, precio (número o texto como "Consultar"), descripción opcional, etiquetas opcionales (Nuevo, Oferta, Vegano, Sin TACC...), variantes opcionales (talles, medidas, tamaños).
- **Fotos**, solo si el rubro las necesita (ropa, deco, productos): una por ítem, de menos de 150 KB cada una (redimensionar a 600 px de lado si vienen grandes). Sin fotos, el layout `list` queda perfecto.
- **WhatsApp** para el botón de pedido/consulta (código de país sin `+`, Argentina `549...`) y qué dice el botón ("Pedir por WhatsApp", "Consultar por WhatsApp", "Reservar turno").
- **Color de acento** si tiene marca; si no, elegir uno acorde al rubro.
- **Slug** del cliente (el mismo de su carpeta en el repo) y si ya tiene página de links (para agregarle el botón "Ver la carta").


> **Número de WhatsApp:** en un cliente real va el del comercio, tal como lo escribió en la plantilla.
> En la demo `cliente-demo` va el de Gian, `5491137845392`. Nunca dejar publicado un número de ejemplo
> tipo `5492610000000`: el botón queda apuntando a la nada y no se nota hasta que un cliente lo toca.

## Decisiones de diseño según el rubro

| Rubro | layout | buscador | Qué mostrar por ítem |
|---|---|---|---|
| Bar, café, restaurante, heladería | `list` | no (sí con más de 60 ítems) | nombre, descripción corta, precio, etiquetas dietéticas |
| Ropa, calzado, deco, regalería | `grid` | sí | foto, nombre, precio, variantes (talles/colores) |
| Ferretería, librería, repuestos | `list` | sí | nombre, descripción técnica, precio o "Consultar" |
| Peluquería, estética, taller, profesionales | `list` | no | servicio, duración o detalle, precio; `cta` "Reservar turno" |

Las etiquetas son texto libre: usar las que el cliente use en su rubro. El título de la página y la carpeta se adaptan: `carta/` para gastronomía, `catalogo/` para productos, `servicios/` para servicios.

## Procedimiento

1. Escribir `pagina_menu.py` (abajo) en el directorio de trabajo si no existe en esta sesión. No necesita dependencias fuera de la librería estándar.
2. Armar `<slug>/<carta|catalogo|servicios>/config.json` con el formato del docstring. Si hay fotos, guardarlas en `<slug>/<carpeta>/fotos/` y referenciarlas con ruta relativa; el script las embebe en el HTML.
3. Generar:
   ```bash
   python3 pagina_menu.py <slug>/carta/config.json <slug>/carta/index.html
   ```
4. Mirar la página una vez a 400 px de ancho (captura con Playwright) para confirmar que no hay textos cortados ni precios desalineados; ajustar y regenerar.
5. Subir al repo según `cartel-qr` (la carpeta del cliente entera). URL final: `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/carta/` (o `catalogo/`, `servicios/`). Verificar con WebFetch desde el contenedor.
6. Cartel QR de la carta con `cartel_qr.py` (tipo `menu`, se detecta solo si la URL contiene `/carta`, `/menu` o `/catalogo`; forzar con `--tipo menu` si no):
   ```bash
   python3 cartel_qr.py --nombre "Nombre" --url "<URL>" --sub "Precios siempre actualizados" --out <slug>/carteles/cartel-menu-<slug>.pdf
   ```
   Verificar el QR decodificando el PNG.
7. Si el cliente tiene página de links, agregar o actualizar el botón `{"tipo": "menu", "label": "Ver la carta", "url": "<URL>"}` en su `config.json` y regenerar con `pagina_links.py --standalone`.
8. Entregar: URL, cartel PDF + PNG, y el instructivo de la planilla si la activaron.

## Precios editables por el dueño (planilla de Google)

Es el argumento de venta del servicio: el dueño cambia precios sin llamar a nadie.

1. Crear una hoja de Google con encabezados en la fila 1, exactamente: `categoria | nombre | descripcion | precio | tags | variantes | img | disponible`. Una fila por ítem; `tags` separados por `|`; `disponible` = `no` oculta el ítem; `img` admite URL pública.
2. Cargar los ítems (los mismos del config.json) y compartir la hoja con el dueño como editor.
3. Archivo → Compartir → **Publicar en la web** → esa hoja → formato **CSV** → Publicar. Copiar el link (`.../pub?output=csv`).
4. Pegarlo en `"sheet_csv"` del config.json, regenerar y subir. La página carga la planilla al abrirse; si falla, muestra lo que tiene el config.json, así que mantener el config razonablemente actualizado.
5. Entregarle al dueño el link de la hoja y una línea: "Editá el precio y en un minuto se ve en la carta. No cambies los títulos de la fila 1."

Limitación: el CSV se parte por comas; si una descripción lleva coma, Google la exporta entre comillas y la página la muestra mal. Pedir que usen punto o guion en vez de coma, o cargar ese ítem sin descripción.

## Ajustes frecuentes

- Colores y tipografía en el bloque `<style>`: `--accent` viene del config; el resto de la paleta (claro y oscuro) está en `:root`.
- Para un catálogo con muchas fotos, preferir URLs (fotos subidas a la carpeta del cliente en el repo y referenciadas por URL de GitHub Pages) en vez de embeberlas, para que el HTML no pase de 2 MB.
- Si el cliente quiere secciones sin precio (por ejemplo "Nosotros"), agregar una categoría con ítems sin `precio`.
- Moneda: `"moneda": "USD"` o `""` para no mostrar símbolo.

## Script `pagina_menu.py`

```python
#!/usr/bin/env python3
"""
Uso:
  python3 pagina_menu.py config.json [salida.html]

config.json:
{
  "nombre": "Bar Central",
  "tagline": "Carta",
  "detalle": "Precios en pesos",
  "accent": "#C8552B",
  "moneda": "$",
  "whatsapp": "5492610000000",
  "mensaje": "Hola! Quiero hacer un pedido",
  "cta": "Pedir por WhatsApp",
  "layout": "list",
  "buscador": false,
  "sheet_csv": "",
  "categorias": [
    {"nombre": "Cafetería", "items": [
      {"nombre": "Espresso", "desc": "Blend de la casa", "precio": 2800, "tags": ["Nuevo"]},
      {"nombre": "Remera lisa", "precio": 18900, "variantes": "S · M · L", "img": "fotos/remera.jpg"}
    ]}
  ]
}
layout: "list" (filas) o "grid" (tarjetas con foto). precio: número o texto ("Consultar").
img: ruta local (se embebe, menos de 150 KB) o URL. disponible: false oculta el ítem.
Planilla CSV (fila 1): categoria | nombre | descripcion | precio | tags | variantes | img | disponible
"""
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path


def img_src(ref, base):
    if not ref:
        return ""
    if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("data:"):
        return ref
    p = (base / ref) if not Path(ref).is_absolute() else Path(ref)
    if not p.exists():
        return ""
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def fmt_price(p, moneda):
    if p is None or p == "":
        return ""
    try:
        n = float(p)
    except ValueError:
        return html.escape(str(p))
    s = f"{n:,.0f}".replace(",", ".")
    return f"{moneda} {s}"


def render(cfg, base=Path(".")):
    name = html.escape(cfg["nombre"])
    tagline = html.escape(cfg.get("tagline", "Carta"))
    detalle = html.escape(cfg.get("detalle", ""))
    accent = cfg.get("accent", "#C8552B")
    moneda = cfg.get("moneda", "$")
    wa = cfg.get("whatsapp")
    msg = cfg.get("mensaje", "Hola! Quiero hacer un pedido")
    sheet = cfg.get("sheet_csv", "")
    cta = html.escape(cfg.get("cta", "Pedir por WhatsApp"))
    layout = cfg.get("layout", "list")
    buscador = bool(cfg.get("buscador", False))

    nav, secs = [], []
    for i, cat in enumerate(cfg["categorias"]):
        cid = f"c{i}"
        nav.append(f'<a href="#{cid}">{html.escape(cat["nombre"])}</a>')
        rows = []
        for it in cat["items"]:
            if it.get("disponible", True) is False:
                continue
            tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in it.get("tags", []))
            desc = f'<p class="desc">{html.escape(it["desc"])}</p>' if it.get("desc") else ""
            var = f'<p class="var">{html.escape(it["variantes"])}</p>' if it.get("variantes") else ""
            src = img_src(it.get("img", ""), base)
            img = f'<img class="ph" src="{src}" alt="" loading="lazy">' if src else ""
            rows.append(
                f'<li class="item">{img}<div class="it"><h3>{html.escape(it["nombre"])}{tags}</h3>{desc}{var}</div>'
                f'<span class="price">{fmt_price(it.get("precio"), moneda)}</span></li>'
            )
        secs.append(f'<section id="{cid}"><h2>{html.escape(cat["nombre"])}</h2><ul>{"".join(rows)}</ul></section>')

    wa_btn = ""
    if wa:
        from urllib.parse import quote
        wa_btn = (f'<a class="wa" href="https://wa.me/{wa}?text={quote(msg)}" target="_blank" rel="noopener">'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 2.9 2.9 0 0 0-.9 2.2 5 5 0 0 0 1.1 2.7 11.5 11.5 0 0 0 4.4 3.9c1.6.7 2.3.8 3.1.6a2.6 2.6 0 0 0 1.7-1.2 2 2 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/></svg>'
                  f'{cta}</a>')

    sheet_js = ""
    if sheet:
        sheet_js = f"""
<script>
(async () => {{
  try {{
    const r = await fetch({json.dumps(sheet)}, {{cache: "no-store"}});
    if (!r.ok) return;
    const rows = (await r.text()).split(/\\r?\\n/).map(l => l.split(","));
    if (rows.length < 2) return;
    const h = rows[0].map(s => s.trim().toLowerCase());
    const ix = k => h.indexOf(k);
    const cats = new Map();
    for (const row of rows.slice(1)) {{
      if (!row[ix("nombre")]) continue;
      if ((row[ix("disponible")] || "").trim().toLowerCase() === "no") continue;
      const c = (row[ix("categoria")] || "Otros").trim();
      if (!cats.has(c)) cats.set(c, []);
      cats.get(c).push({{n: row[ix("nombre")].trim(), d: (row[ix("descripcion")] || "").trim(),
        p: (row[ix("precio")] || "").trim(), t: (row[ix("tags")] || "").split("|").map(s => s.trim()).filter(Boolean),
        v: (row[ix("variantes")] || "").trim(), i: (row[ix("img")] || "").trim()}});
    }}
    if (!cats.size) return;
    const esc = s => s.replace(/[&<>"]/g, ch => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[ch]);
    const fmt = p => {{ const n = Number(p); return isNaN(p) || p === "" ? esc(p) : {json.dumps(moneda)} + " " + n.toLocaleString("es-AR", {{maximumFractionDigits: 0}}); }};
    let i = 0, nav = "", secs = "";
    for (const [c, items] of cats) {{
      const id = "c" + (i++);
      nav += `<a href="#${{id}}">${{esc(c)}}</a>`;
      secs += `<section id="${{id}}"><h2>${{esc(c)}}</h2><ul>` + items.map(it =>
        `<li class="item">${{it.i ? `<img class="ph" src="${{esc(it.i)}}" alt="" loading="lazy">` : ""}}<div class="it"><h3>${{esc(it.n)}}${{it.t.map(t => `<span class="tag">${{esc(t)}}</span>`).join("")}}</h3>${{it.d ? `<p class="desc">${{esc(it.d)}}</p>` : ""}}${{it.v ? `<p class="var">${{esc(it.v)}}</p>` : ""}}</div><span class="price">${{fmt(it.p)}}</span></li>`
      ).join("") + `</ul></section>`;
    }}
    document.querySelector(".nav").innerHTML = nav;
    document.querySelector("main").innerHTML = secs;
  }} catch (e) {{}}
}})();
</script>"""

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{tagline} de {name}">
<title>{name} · {tagline}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@500;600;700&display=swap">
<style>
:root {{
  --accent: {accent};
  --bg: #F7F5F2; --card: #FFFFFF; --ink: #1E1B18; --muted: #6B645D; --line: #E8E3DD; --tagbg: #F1ECE6;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; --tagbg: #2A251F; }}
}}
:root[data-theme="dark"] {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; --tagbg: #2A251F; }}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 64px; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Manrope, "Segoe UI", system-ui, sans-serif; padding-inline: 16px; padding-block: 28px 96px; }}
.wrap {{ max-width: 560px; margin: 0 auto; }}
header {{ text-align: center; margin-bottom: 18px; }}
.brand {{ display: inline-grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; background: var(--accent); color: #fff; font-family: Fraunces, Georgia, serif; font-size: 28px; font-weight: 700; margin-bottom: 10px; }}
h1 {{ margin: 0; font-family: Fraunces, Georgia, serif; font-size: 30px; font-weight: 700; letter-spacing: -0.01em; }}
.tag-line {{ margin: 4px 0 0; color: var(--muted); font-size: 14px; }}
.nav {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 2; display: flex; gap: 8px; overflow-x: auto; padding: 10px 0; margin: 0 -16px; padding-inline: 16px; background: var(--bg); scrollbar-width: none; }}
.nav::-webkit-scrollbar {{ display: none; }}
.nav a {{ flex: none; text-decoration: none; color: var(--ink); background: var(--card); border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-size: 14px; font-weight: 600; }}
.nav a:hover {{ border-color: var(--accent); }}
section {{ margin-top: 26px; }}
h2 {{ font-family: Fraunces, Georgia, serif; font-size: 22px; font-weight: 600; margin: 0 0 10px; color: var(--accent); }}
ul {{ list-style: none; margin: 0; padding: 0; background: var(--card); border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }}
.item {{ display: flex; justify-content: space-between; gap: 14px; padding: 14px 16px; border-top: 1px solid var(--line); }}
.item:first-child {{ border-top: 0; }}
.it {{ min-width: 0; }}
h3 {{ margin: 0; font-size: 16px; font-weight: 700; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }}
.desc {{ margin: 3px 0 0; color: var(--muted); font-size: 13px; line-height: 1.4; }}
.tag {{ font-size: 10.5px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--accent); background: var(--tagbg); border-radius: 999px; padding: 2px 7px; }}
.price {{ flex: none; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.var {{ margin: 4px 0 0; color: var(--muted); font-size: 12px; letter-spacing: .02em; }}
.ph {{ flex: none; width: 64px; height: 64px; object-fit: cover; border-radius: 10px; background: var(--tagbg); }}
.search {{ width: 100%; margin: 10px 0 0; padding: 11px 14px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); color: var(--ink); font: inherit; font-size: 15px; }}
.search:focus {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
body.grid ul {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; background: none; border: 0; overflow: visible; }}
body.grid .item {{ flex-direction: column; justify-content: flex-start; gap: 8px; padding: 0 0 12px; border: 1px solid var(--line); border-radius: 14px; background: var(--card); overflow: hidden; }}
body.grid .ph {{ width: 100%; height: auto; aspect-ratio: 1; border-radius: 0; }}
body.grid .it {{ padding: 0 12px; }}
body.grid h3 {{ font-size: 15px; }}
body.grid .price {{ padding: 0 12px; color: var(--accent); }}
@media (min-width: 480px) {{ body.grid ul {{ grid-template-columns: repeat(3, 1fr); }} }}
.item.hide, section.hide {{ display: none; }}
.wa {{ position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(16px + env(safe-area-inset-bottom, 0px)); display: inline-flex; align-items: center; gap: 8px; background: #25D366; color: #fff; text-decoration: none; font-weight: 700; padding: 12px 20px; border-radius: 999px; white-space: nowrap; box-shadow: 0 6px 18px rgba(0,0,0,.18); }}
.wa svg {{ width: 20px; height: 20px; fill: currentColor; }}
.foot {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 28px; }}
</style></head><body class="{layout}">
<div class="wrap">
  <header>
    <div class="brand">{html.escape(cfg["nombre"][:1].upper())}</div>
    <h1>{name}</h1>
    <p class="tag-line">{tagline}{(" · " + detalle) if detalle else ""}</p>
  </header>
  <nav class="nav" aria-label="Categorías">{"".join(nav)}</nav>
  {'<input class="search" id="q" type="search" placeholder="Buscar..." aria-label="Buscar">' if buscador else ''}
  <main>{"".join(secs)}</main>
  <p class="foot">Los precios pueden cambiar sin previo aviso.</p>
</div>
{wa_btn}{sheet_js}
<script>
const q = document.getElementById("q");
if (q) q.addEventListener("input", () => {{
  const t = q.value.trim().toLowerCase();
  document.querySelectorAll("section").forEach(s => {{
    let any = false;
    s.querySelectorAll(".item").forEach(li => {{ const m = !t || li.textContent.toLowerCase().includes(t); li.classList.toggle("hide", !m); any = any || m; }});
    s.classList.toggle("hide", !any);
  }});
}});
</script>
</body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: pagina_menu.py config.json [salida.html]")
    src = Path(sys.argv[1])
    cfg = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("index.html")
    out.write_text(render(cfg, src.parent), encoding="utf-8")
    print(out)
```