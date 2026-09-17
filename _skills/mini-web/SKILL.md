---
name: mini-web
description: "Crea una mini web de presentación (una sola página) para un comercio de cualquier rubro, con secciones libres, la publica en GitHub Pages dentro del repo GS-Servicios-Digitales y genera su cartel QR."
---

# Mini web de presentación

Servicio "Mini web" del catálogo de servicios digitales de Gianluca. Es una página de
presentación del comercio (no una tienda ni una carta): portada con foto, quiénes somos,
destacados, **secciones libres** que cuentan sobre el lugar, galería, horarios, ubicación
y contacto. Se adapta a cualquier rubro: bar, peluquería, gimnasio, ferretería, estudio,
consultorio, taller, etc.

## Convenciones fijas (no cambiar)

- Repo público: `Giannsalva/GS-Servicios-Digitales`, hosteado en GitHub Pages.
- URL base: `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/web/`
- Cada cliente tiene su carpeta `<slug>/` (slug en minúsculas, sin espacios ni acentos).
  La mini web va en `<slug>/web/` con `config.json`, `fotos/` e `index.html`.
  El cartel QR va en `<slug>/carteles/`. La demo es `cliente-demo/` ("Bar Central").
- **Nunca renombrar** el repo, la carpeta del cliente ni `web/`: los QR impresos apuntan a esa URL.
- El generador vive en `_tools/pagina_web.py` del repo (misma copia que abajo). Los otros
  generadores (`cartel_qr.py`, `pagina_links.py`, `pagina_menu.py`) están en las skills
  `cartel-qr` y `catalogo-digital`.
- El token de GitHub lo pega Gian en el chat cuando hace falta; no se guarda en skills ni en el repo.

## Paso 0: la plantilla del cliente (siempre)

El servicio **arranca por la plantilla de `_plantillas/`**, no por preguntas sueltas.

1. Si el cliente todavía no la completó, mandarle el `.docx` de `_plantillas/docx/`.
2. Cuando la devuelve (archivo, foto o audios de WhatsApp), transcribirla y archivarla como
   `<slug>/alta-mini-web.md` en el repo: ese archivo es la fuente de verdad del cliente.
3. **Leer el alta antes de generar nada.** De ahí salen todos los datos; nunca inventar nombres,
   links, precios ni teléfonos.
4. Lo que quedó vacío se pregunta una sola vez, todo junto, y se completa en el mismo archivo.
   Lo que sigue faltando se marca `PENDIENTE` y no se publica ni se imprime nada que dependa de eso.
5. Si el cliente ya tiene otro servicio contratado, los datos del comercio se copian de su alta
   anterior en vez de volver a pedirlos.

Mapeo de `_plantillas/mini-web.md` al `config.json`:

| Bloque de la plantilla | Dónde va |
|---|---|
| Datos del comercio | `nombre`, `rubro`, `accent`, `direccion`, `maps_url`, `whatsapp`, `mensaje`, `telefono`, redes |
| Horarios | `horarios[]` |
| Frase corta / quiénes son | `frase`, `descripcion` |
| Cosas que los destacan | `destacados[]` |
| Historia, qué ofrecen, comodidades, preguntas | `secciones[]` (texto+imagen, tarjetas, lista, preguntas) |
| Botones principales | `botones[]` |
| Fotos | `portada`, `galeria[]`, imagen por sección |

Los textos se redactan a partir de lo que escribió o grabó el dueño, con sus palabras. Si un bloque
quedó vacío en la plantilla, esa sección simplemente no va: mejor una página corta y verdadera.


> **Botón del hero:** por defecto el primer botón es "Escribinos" (WhatsApp, verde). Si la página
> ya tiene la sección Contacto abajo, conviene `"cta_whatsapp": false` y dejar el botón útil del rubro
> ("Ver la carta", "Reservar"), que toma el color de acento. Así es la demo.

> **Número de WhatsApp:** en un cliente real va el del comercio, tal como lo escribió en la plantilla.
> En la demo `cliente-demo` va el de Gian, `5491137845392`. Nunca dejar publicado un número de ejemplo
> tipo `5492610000000`: el botón queda apuntando a la nada y no se nota hasta que un cliente lo toca.

## Pasos

1. **Relevar** con Gian: nombre, rubro, frase corta, descripción (2-3 oraciones), color de
   acento, fotos (portada, logo, galería, foto por sección), qué secciones quiere contar
   (historia, servicios, equipo, comodidades, preguntas frecuentes, promociones...), horarios,
   dirección, link de Maps, WhatsApp (con 549...), teléfono, redes, mail y botones extra
   (p. ej. link a la carta `<slug>/carta/` o a la página de links `<slug>/`).
   Si falta algo, dejar la sección fuera: todo salvo `nombre` es opcional y se omite si está vacío.
2. **Fotos**: redimensionar con PIL a 1200 px de ancho la portada y 800 px la galería, JPEG
   calidad 80, < 200 KB cada una. Se embeben en base64 en el HTML (página autocontenida).
3. **Armar `config.json`** en `<slug>/web/` (esquema en el docstring del script). Las
   `secciones` son libres: cada una tiene `titulo` y cualquier combinación de `texto`
   (párrafos separados por línea en blanco), `imagen`, `tarjetas`, `lista` y `preguntas`.
   Se muestran en el orden del JSON, después de "Quiénes somos" y los destacados.
   Elegir el tipo de bloque según el rubro: tarjetas para servicios/planes, lista para
   comodidades/marcas/obras sociales, preguntas para FAQ, texto+imagen para historia/equipo.
4. **Generar**: `python3 _tools/pagina_web.py <slug>/web/config.json <slug>/web/index.html`.
   Revisar con captura Playwright a 390 px y 1200 px de ancho (claro y oscuro).
5. **Cartel QR** con la skill `cartel-qr`: `--tipo web --url <URL de la web>`, salida en
   `<slug>/carteles/`. Verificar el QR con pyzbar.
6. **Publicar**: actualizar la tabla de clientes en `README.md`, zip de los archivos nuevos,
   `device_commit_files` a `_upload.zip` en la carpeta local
   `$HOME/mnt/GS-Servicios-Digitales`, y desde `device_bash` clonar en `/tmp/gs` con el
   token en la URL, copiar, commit y push (git no funciona dentro de la carpeta conectada).
   Después `git remote set-url` sin token, sincronizar la carpeta local y vaciar el zip
   (`: > _upload.zip`; no se pueden borrar archivos).
7. **Verificar** la URL publicada con WebFetch (Pages tarda ~1 min) y recién ahí entregar
   a Gian: URL, cartel PDF/PNG y resumen de secciones.

## Diseño

Manrope + Fraunces (Google Fonts), tema claro/oscuro automático, ancho máx. 640 px,
hero con foto de portada oscurecida y botones (WhatsApp verde + botones extra), tarjetas
redondeadas, galería 3 columnas con primera foto grande, mapa embebido opcional con
`mapa_embed: true`. Mobile first: se va a abrir escaneando un QR.

## `_tools/pagina_web.py`

```python
#!/usr/bin/env python3
"""
Mini web de presentación para un comercio: una sola página con portada, quiénes
somos, destacados, galería, horarios, ubicación y contacto. Genera un index.html
autocontenido (las fotos locales se embeben).

Uso:
  python3 pagina_web.py config.json [salida.html]

config.json:
{
  "nombre": "Bar Central",
  "rubro": "Café de especialidad y pastelería",
  "frase": "El café de tu barrio, hecho con calma.",
  "descripcion": "Párrafo corto sobre el local. Puede tener dos o tres oraciones.",
  "accent": "#C8552B",
  "portada": "fotos/portada.jpg",
  "logo": "fotos/logo.png",
  "destacados": [
    {"titulo": "Café de especialidad", "texto": "Granos tostados en Mendoza, molidos al momento."},
    {"titulo": "Pastelería propia", "texto": "Horneamos todos los días desde las 6."}
  ],
  "secciones": [
    {"titulo": "Nuestra historia", "texto": "Uno o varios párrafos.\n\nSeparados por línea en blanco.", "imagen": "fotos/historia.jpg"},
    {"titulo": "Qué ofrecemos", "tarjetas": [{"titulo": "Desayunos", "texto": "..."}, {"titulo": "Eventos", "texto": "..."}]},
    {"titulo": "Servicios", "lista": ["Wi-Fi libre", "Pet friendly", "Acceso sin escaleras"]},
    {"titulo": "Preguntas frecuentes", "preguntas": [{"p": "¿Hacen delivery?", "r": "Sí, en Godoy Cruz y Ciudad."}]}
  ],
  "galeria": ["fotos/1.jpg", "fotos/2.jpg", "fotos/3.jpg"],
  "horarios": [
    {"dias": "Lunes a viernes", "horas": "8:00 a 20:00"},
    {"dias": "Sábados", "horas": "9:00 a 21:00"},
    {"dias": "Domingos", "horas": "Cerrado"}
  ],
  "direccion": "San Martín 1234, Godoy Cruz, Mendoza",
  "maps_url": "https://maps.app.goo.gl/...",
  "mapa_embed": true,
  "whatsapp": "5492610000000",
  "mensaje": "Hola! Quiero hacer una consulta",
  "telefono": "+54 261 000-0000",
  "instagram": "https://instagram.com/barcentral.mza",
  "facebook": "https://facebook.com/barcentral",
  "email": "hola@barcentral.com",
  "cta_whatsapp": false,        # opcional: saca el boton "Escribinos" del hero (el WhatsApp sigue en Contacto)
  "botones": [
    {"label": "Ver la carta", "url": "https://.../carta/"},
    {"label": "Reservar mesa", "url": "https://wa.me/549..."}
  ]
}
Todos los campos salvo "nombre" son opcionales: cada sección aparece solo si tiene datos.
"secciones" es libre y se adapta al rubro: cada una lleva "titulo" y cualquier combinación de
"texto" (párrafos separados por línea en blanco), "imagen", "tarjetas", "lista" y "preguntas".
Se muestran en el orden del JSON, después de "Quiénes somos" y los destacados.
Fotos locales de menos de 200 KB (redimensionar a 1200 px de ancho la portada, 800 px la galería).
"""
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path
from urllib.parse import quote


def img_src(ref, base):
    if not ref:
        return ""
    if ref.startswith(("http://", "https://", "data:")):
        return ref
    p = Path(ref) if Path(ref).is_absolute() else base / ref
    if not p.exists():
        return ""
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


ICO = {
    "wa": '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 2.9 2.9 0 0 0-.9 2.2 5 5 0 0 0 1.1 2.7 11.5 11.5 0 0 0 4.4 3.9c1.6.7 2.3.8 3.1.6a2.6 2.6 0 0 0 1.7-1.2 2 2 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/>',
    "ig": '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2"/>',
    "fb": '<path d="M14 8.5V6.8c0-.8.5-1 .9-1H17V2.5h-2.9C11 2.5 10 4.8 10 6.4v2.1H7.5V12H10v9.5h4V12h2.8l.4-3.5H14Z"/>',
    "tel": '<path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.2c1.1.4 2.3.6 3.6.6a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.2.2 2.4.6 3.6a1 1 0 0 1-.3 1L6.6 10.8Z"/>',
    "mail": '<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm1 2.3V18h16V7.3l-8 5.2-8-5.2ZM5.4 7l6.6 4.3L18.6 7H5.4Z"/>',
    "pin": '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/>',
}


def svg(k):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICO[k]}</svg>'


def render(cfg, base=Path(".")):
    e = html.escape
    name = e(cfg["nombre"])
    accent = cfg.get("accent", "#C8552B")
    portada = img_src(cfg.get("portada", ""), base)
    logo = img_src(cfg.get("logo", ""), base)
    wa = cfg.get("whatsapp")
    wa_url = f"https://wa.me/{wa}?text={quote(cfg.get('mensaje', 'Hola!'))}" if wa else ""

    hero_style = f' style="background-image:url({portada})"' if portada else ""
    brand = f'<img class="logo" src="{logo}" alt="">' if logo else f'<div class="logo mono">{e(cfg["nombre"][:1].upper())}</div>'
    hero_btns = ""
    if wa_url and cfg.get("cta_whatsapp", True):
        hero_btns += f'<a class="btn wa" href="{wa_url}" target="_blank" rel="noopener">{svg("wa")}Escribinos</a>'
    for b in cfg.get("botones", []):
        clase = "btn primary" if not hero_btns else "btn"
        hero_btns += f'<a class="{clase}" href="{e(b["url"])}" target="_blank" rel="noopener">{e(b["label"])}</a>'

    about = ""
    if cfg.get("descripcion"):
        about = f'<section class="about"><h2>Quiénes somos</h2><p>{e(cfg["descripcion"])}</p></section>'

    feats = ""
    if cfg.get("destacados"):
        cards = "".join(f'<div class="card"><h3>{e(d["titulo"])}</h3><p>{e(d.get("texto", ""))}</p></div>' for d in cfg["destacados"])
        feats = f'<section><div class="feats">{cards}</div></section>'

    extra = ""
    for sec in cfg.get("secciones", []):
        parts = []
        if sec.get("texto"):
            parts.append("".join(f"<p>{e(par.strip())}</p>" for par in sec["texto"].split("\n\n") if par.strip()))
        if sec.get("tarjetas"):
            parts.append('<div class="feats">' + "".join(f'<div class="card"><h3>{e(t["titulo"])}</h3><p>{e(t.get("texto", ""))}</p></div>' for t in sec["tarjetas"]) + "</div>")
        if sec.get("lista"):
            parts.append('<ul class="bul">' + "".join(f"<li>{e(x)}</li>" for x in sec["lista"]) + "</ul>")
        if sec.get("preguntas"):
            parts.append("".join(f'<details><summary>{e(q["p"])}</summary><p>{e(q["r"])}</p></details>' for q in sec["preguntas"]))
        im = img_src(sec.get("imagen", ""), base)
        body = "".join(parts)
        if im:
            body = f'<div class="split"><img src="{im}" alt="" loading="lazy"><div>{body}</div></div>'
        extra += f'<section class="free"><h2>{e(sec["titulo"])}</h2>{body}</section>'

    gal = ""
    pics = [img_src(p, base) for p in cfg.get("galeria", [])]
    pics = [p for p in pics if p]
    if pics:
        gal = '<section><h2>Galería</h2><div class="gal">' + "".join(f'<img src="{p}" alt="" loading="lazy">' for p in pics) + "</div></section>"

    hours = ""
    if cfg.get("horarios"):
        rows = "".join(f'<div class="row"><span>{e(h["dias"])}</span><b>{e(h["horas"])}</b></div>' for h in cfg["horarios"])
        hours = f'<div class="box"><h2>Horarios</h2>{rows}</div>'

    loc = ""
    if cfg.get("direccion") or cfg.get("maps_url"):
        addr = e(cfg.get("direccion", ""))
        link = f'<a class="btn small" href="{e(cfg["maps_url"])}" target="_blank" rel="noopener">{svg("pin")}Cómo llegar</a>' if cfg.get("maps_url") else ""
        embed = ""
        if cfg.get("mapa_embed") and cfg.get("direccion"):
            embed = f'<iframe title="Mapa" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q={quote(cfg["direccion"])}&output=embed"></iframe>'
        loc = f'<div class="box"><h2>Dónde estamos</h2><p>{addr}</p>{link}{embed}</div>'

    info = f'<section class="info">{hours}{loc}</section>' if (hours or loc) else ""

    contact_items = []
    if wa_url:
        contact_items.append(f'<a href="{wa_url}" target="_blank" rel="noopener">{svg("wa")}WhatsApp</a>')
    if cfg.get("telefono"):
        tel = cfg["telefono"]
        contact_items.append(f'<a href="tel:{e(tel.replace(" ", "").replace("-", ""))}">{svg("tel")}{e(tel)}</a>')
    if cfg.get("instagram"):
        contact_items.append(f'<a href="{e(cfg["instagram"])}" target="_blank" rel="noopener">{svg("ig")}Instagram</a>')
    if cfg.get("facebook"):
        contact_items.append(f'<a href="{e(cfg["facebook"])}" target="_blank" rel="noopener">{svg("fb")}Facebook</a>')
    if cfg.get("email"):
        contact_items.append(f'<a href="mailto:{e(cfg["email"])}">{svg("mail")}{e(cfg["email"])}</a>')
    contact = f'<section class="contact"><h2>Contacto</h2><div class="clist">{"".join(contact_items)}</div></section>' if contact_items else ""

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{e(cfg.get('rubro', ''))} · {e(cfg.get('direccion', ''))}">
<title>{name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@500;600;700&display=swap">
<style>
:root {{ --accent: {accent}; --bg: #F7F5F2; --card: #FFFFFF; --ink: #1E1B18; --muted: #6B645D; --line: #E8E3DD; --hero: #2A2420; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; }} }}
:root[data-theme="dark"] {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Manrope, "Segoe UI", system-ui, sans-serif; line-height: 1.5; }}
.hero {{ position: relative; min-height: 78vh; display: grid; place-items: end start; padding: 24px 16px calc(28px + env(safe-area-inset-bottom, 0px)); color: #fff; background: var(--hero) center/cover no-repeat; }}
.hero::before {{ content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.72)); }}
.hero > div {{ position: relative; max-width: 640px; width: 100%; margin: 0 auto; }}
.logo {{ width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 3px solid #fff; margin-bottom: 14px; }}
.logo.mono {{ display: grid; place-items: center; background: var(--accent); font-family: Fraunces, Georgia, serif; font-size: 34px; font-weight: 700; }}
.hero h1 {{ margin: 0; font-family: Fraunces, Georgia, serif; font-size: clamp(34px, 8vw, 52px); font-weight: 700; line-height: 1.05; letter-spacing: -0.01em; text-wrap: balance; }}
.rubro {{ margin: 6px 0 0; font-size: 15px; opacity: .9; }}
.frase {{ margin: 14px 0 0; font-size: 18px; max-width: 34ch; text-wrap: balance; }}
.btns {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }}
.btn {{ display: inline-flex; align-items: center; gap: 8px; padding: 12px 18px; border-radius: 999px; text-decoration: none; font-weight: 700; font-size: 15px; background: rgba(255,255,255,.14); color: #fff; border: 1px solid rgba(255,255,255,.4); backdrop-filter: blur(4px); }}
.btn.wa {{ background: #25D366; border-color: #25D366; }}
.btn.primary {{ background: var(--accent); border-color: var(--accent); }}
.btn svg {{ width: 18px; height: 18px; fill: currentColor; }}
main {{ max-width: 640px; margin: 0 auto; padding: 8px 16px 48px; }}
section {{ margin-top: 36px; }}
h2 {{ font-family: Fraunces, Georgia, serif; font-size: 24px; font-weight: 600; margin: 0 0 12px; color: var(--accent); }}
.about p {{ margin: 0; font-size: 17px; max-width: 60ch; }}
.feats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 18px; }}
.card h3 {{ margin: 0 0 6px; font-size: 16px; }}
.card p {{ margin: 0; color: var(--muted); font-size: 14px; }}
.gal {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }}
.gal img {{ width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 12px; display: block; }}
.gal img:first-child {{ grid-column: span 2; grid-row: span 2; }}
.info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }}
.box {{ background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 18px; }}
.box h2 {{ font-size: 20px; }}
.box p {{ margin: 0 0 10px; }}
.row {{ display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-top: 1px solid var(--line); font-size: 15px; }}
.row:first-of-type {{ border-top: 0; }}
.btn.small {{ background: var(--accent); border-color: var(--accent); padding: 10px 14px; font-size: 14px; }}
iframe {{ width: 100%; height: 220px; border: 0; border-radius: 12px; margin-top: 12px; }}
.clist {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
.clist a {{ display: flex; align-items: center; gap: 10px; background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; color: var(--ink); text-decoration: none; font-weight: 600; font-size: 15px; }}
.clist svg {{ width: 20px; height: 20px; fill: var(--accent); flex: none; }}
.free p {{ margin: 0 0 10px; font-size: 16px; max-width: 60ch; }}
.free p:last-child {{ margin-bottom: 0; }}
.split {{ display: grid; gap: 16px; align-items: start; }}
.split img {{ width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: 14px; }}
@media (min-width: 560px) {{ .split {{ grid-template-columns: 1fr 1.3fr; }} }}
.bul {{ margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; }}
.bul li {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; font-size: 15px; }}
.bul li::before {{ content: "\\2713"; color: var(--accent); font-weight: 700; margin-right: 8px; }}
details {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 10px 14px; margin-bottom: 8px; }}
summary {{ cursor: pointer; font-weight: 700; font-size: 15px; }}
details p {{ margin: 8px 0 0; color: var(--muted); font-size: 14px; }}
footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 0 16px 32px; }}
</style></head><body>
<header class="hero"{hero_style}><div>
  {brand}
  <h1>{name}</h1>
  {f'<p class="rubro">{e(cfg["rubro"])}</p>' if cfg.get("rubro") else ""}
  {f'<p class="frase">{e(cfg["frase"])}</p>' if cfg.get("frase") else ""}
  {f'<div class="btns">{hero_btns}</div>' if hero_btns else ""}
</div></header>
<main>
{about}{feats}{extra}{gal}{info}{contact}
</main>
<footer>{name}{(" · " + e(cfg["direccion"])) if cfg.get("direccion") else ""}</footer>
</body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: pagina_web.py config.json [salida.html]")
    src = Path(sys.argv[1])
    cfg = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("index.html")
    out.write_text(render(cfg, src.parent), encoding="utf-8")
    print(out)
```