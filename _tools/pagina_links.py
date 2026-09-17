#!/usr/bin/env python3
"""
Página de links para un comercio (estilo link-in-bio). Toma un JSON y genera un
index.html autocontenido, listo para publicar (Artifact, GitHub Pages, Netlify).

Uso:
  python3 pagina_links.py config.json [salida.html] [--standalone]
  --standalone: documento HTML completo (GitHub Pages / Netlify). Sin el flag, fragmento para publicar como Artifact.

config.json:
{
  "nombre": "Bar Central",
  "tagline": "Café de especialidad · Godoy Cruz, Mendoza",
  "detalle": "Lun a Sáb 8 a 20 hs · San Martín 1234",
  "accent": "#C8552B",
  "logo": "logo.png",            (opcional, se embebe como data URI)
  "links": [
    {"tipo": "whatsapp",  "label": "Pedinos por WhatsApp", "sub": "Respondemos al toque", "url": "https://wa.me/549..."},
    {"tipo": "instagram", "label": "Instagram", "sub": "@barcentral", "url": "https://instagram.com/barcentral"},
    {"tipo": "google",    "label": "Dejanos tu reseña", "url": "https://maps.app.goo.gl/..."},
    {"tipo": "maps",      "label": "Cómo llegar", "url": "https://maps.app.goo.gl/..."},
    {"tipo": "facebook",  "label": "Facebook", "url": "https://facebook.com/..."},
    {"tipo": "web",       "label": "Nuestra web", "url": "https://..."},
    {"tipo": "menu",      "label": "Ver la carta", "url": "https://..."},
    {"tipo": "tel",       "label": "Llamanos", "url": "tel:+54261..."},
    {"tipo": "mail",      "label": "Escribinos", "url": "mailto:..."},
    {"tipo": "tiktok",    "label": "TikTok", "url": "https://tiktok.com/@..."}
  ]
}
"""
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path

ICONS = {
    "whatsapp": ("#25D366", '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 2.9 2.9 0 0 0-.9 2.2 5 5 0 0 0 1.1 2.7 11.5 11.5 0 0 0 4.4 3.9c1.6.7 2.3.8 3.1.6a2.6 2.6 0 0 0 1.7-1.2 2 2 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/>'),
    "instagram": ("#E1306C", '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2"/>'),
    "facebook": ("#1877F2", '<path d="M14 8.5V6.8c0-.8.5-1 .9-1H17V2.5h-2.9C11 2.5 10 4.8 10 6.4v2.1H7.5V12H10v9.5h4V12h2.8l.4-3.5H14Z"/>'),
    "google": ("#4285F4", '<path d="M12 2l2.9 6.2 6.8.8-5 4.6 1.3 6.7L12 17l-6 3.3 1.3-6.7-5-4.6 6.8-.8L12 2z"/>'),
    "maps": ("#EA4335", '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/>'),
    "web": ("#0F766E", '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18" fill="none" stroke="currentColor" stroke-width="2"/>'),
    "menu": ("#B45309", '<path d="M5 3h14a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm2 4h10v2H7V7Zm0 4h10v2H7v-2Zm0 4h6v2H7v-2Z"/>'),
    "tel": ("#2563EB", '<path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.2c1.1.4 2.3.6 3.6.6a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.2.2 2.4.6 3.6a1 1 0 0 1-.3 1L6.6 10.8Z"/>'),
    "mail": ("#7C3AED", '<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm1 2.3V18h16V7.3l-8 5.2-8-5.2ZM5.4 7l6.6 4.3L18.6 7H5.4Z"/>'),
    "tiktok": ("#111111", '<path d="M16.5 3c.3 2.2 1.6 3.6 3.7 3.8v3.1c-1.4 0-2.6-.4-3.7-1.2v6.4A5.6 5.6 0 1 1 10.9 9.5v3.2a2.5 2.5 0 1 0 2.5 2.5V3h3.1Z"/>'),
}


def data_uri(path):
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def render(cfg, standalone=False):
    name = html.escape(cfg["nombre"])
    tagline = html.escape(cfg.get("tagline", ""))
    detalle = html.escape(cfg.get("detalle", ""))
    accent = cfg.get("accent", "#C8552B")
    logo = cfg.get("logo")
    avatar = (
        f'<img class="logo" src="{data_uri(logo)}" alt="">'
        if logo and Path(logo).exists()
        else f'<div class="logo mono">{html.escape(cfg["nombre"][:1].upper())}</div>'
    )

    items = []
    for l in cfg["links"]:
        tipo = l.get("tipo", "web")
        color, svg = ICONS.get(tipo, ICONS["web"])
        sub = f'<span class="sub">{html.escape(l["sub"])}</span>' if l.get("sub") else ""
        items.append(
            f'<a class="btn" href="{html.escape(l["url"])}" target="_blank" rel="noopener">'
            f'<span class="ic" style="--c:{color}"><svg viewBox="0 0 24 24" aria-hidden="true">{svg}</svg></span>'
            f'<span class="tx"><span class="lb">{html.escape(l["label"])}</span>{sub}</span>'
            f'<span class="ar" aria-hidden="true">›</span></a>'
        )
    links = "\n".join(items)

    doc = f"""<title>{name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&display=swap">
<style>
:root {{
  --accent: {accent};
  --bg: #F7F5F2; --card: #FFFFFF; --ink: #1E1B18; --muted: #6B645D;
  --line: #E8E3DD; --hover: #FBF9F7;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; --hover: #27231D;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; --hover: #27231D;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: Manrope, "Segoe UI", system-ui, -apple-system, sans-serif;
  padding-block: 32px 40px; padding-inline: 16px;
}}
.wrap {{ max-width: 460px; margin: 0 auto; display: flex; flex-direction: column; gap: 22px; }}
.head {{ text-align: center; display: flex; flex-direction: column; align-items: center; gap: 6px; }}
.logo {{
  width: 92px; height: 92px; border-radius: 50%; object-fit: cover; margin-bottom: 8px;
  border: 3px solid var(--card); box-shadow: 0 0 0 3px var(--accent);
}}
.logo.mono {{
  display: grid; place-items: center; background: var(--accent); color: #fff;
  font-weight: 800; font-size: 40px;
}}
h1 {{ margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.01em; text-wrap: balance; }}
.tag {{ margin: 0; color: var(--muted); font-weight: 500; font-size: 15px; }}
.det {{ margin: 0; color: var(--muted); font-size: 13px; }}
.list {{ display: flex; flex-direction: column; gap: 12px; }}
.btn {{
  display: flex; align-items: center; gap: 14px; text-decoration: none; color: var(--ink);
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  padding: 14px 16px; transition: transform .12s ease, background .12s ease;
}}
.btn:hover {{ background: var(--hover); transform: translateY(-1px); }}
.btn:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 2px; }}
.ic {{
  flex: none; width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center;
  background: color-mix(in srgb, var(--c) 14%, transparent); color: var(--c);
}}
.ic svg {{ width: 24px; height: 24px; fill: currentColor; }}
.tx {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }}
.lb {{ font-weight: 700; font-size: 16px; }}
.sub {{ color: var(--muted); font-size: 13px; }}
.ar {{ color: var(--muted); font-size: 24px; line-height: 1; }}
.foot {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 8px; }}
@media (prefers-reduced-motion: reduce) {{ .btn {{ transition: none; }} }}
</style>
<div class="wrap">
  <header class="head">
    {avatar}
    <h1>{name}</h1>
    {f'<p class="tag">{tagline}</p>' if tagline else ''}
    {f'<p class="det">{detalle}</p>' if detalle else ''}
  </header>
  <nav class="list" aria-label="Enlaces de {name}">
{links}
  </nav>
  <p class="foot">Guardá esta página o compartila: todos nuestros contactos en un solo lugar.</p>
</div>
"""
    if standalone:
        doc = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
               f'<meta name="description" content="{tagline or name}">'
               + doc.replace("<title>", "<title>", 1).split("<style>", 1)[0]
               + "<style>" + doc.split("<style>", 1)[1].split("</style>", 1)[0] + "</style></head><body>"
               + doc.split("</style>", 1)[1] + "</body></html>")
    return doc


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--standalone"]
    standalone = "--standalone" in sys.argv
    if not args:
        sys.exit("Uso: pagina_links.py config.json [salida.html] [--standalone]")
    cfg = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    out = Path(args[1]) if len(args) > 1 else Path("index.html")
    out.write_text(render(cfg, standalone), encoding="utf-8")
    print(out)
