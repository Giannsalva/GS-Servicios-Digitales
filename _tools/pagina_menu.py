#!/usr/bin/env python3
"""
Menú / catálogo digital para un comercio. Toma un JSON y genera un index.html
autocontenido. Si el JSON trae "sheet_csv" (planilla de Google publicada como CSV),
la página carga los productos desde ahí al abrirse y el dueño edita precios sin
tocar nada más; los datos del JSON quedan como respaldo.

Uso:
  python3 pagina_menu.py config.json [salida.html]

config.json:
{
  "nombre": "Bar Central",
  "tagline": "Carta",
  "detalle": "Precios en pesos · Actualizado septiembre 2026",
  "accent": "#C8552B",
  "moneda": "$",
  "whatsapp": "5492610000000",
  "mensaje": "Hola! Quiero hacer un pedido",
  "sheet_csv": "https://docs.google.com/spreadsheets/d/e/XXX/pub?output=csv",
  "categorias": [
    {"nombre": "Cafetería", "items": [
      {"nombre": "Espresso", "desc": "Blend de la casa", "precio": 2800, "tags": ["Nuevo"]},
      {"nombre": "Flat white", "precio": 3900}
    ]}
  ]
}
Formato de la planilla (una fila por producto, encabezados en la fila 1):
  categoria | nombre | descripcion | precio | tags | disponible
"""
import html
import json
import sys
from pathlib import Path


def fmt_price(p, moneda):
    if p is None or p == "":
        return ""
    try:
        n = float(p)
    except ValueError:
        return html.escape(str(p))
    s = f"{n:,.0f}".replace(",", ".")
    return f"{moneda} {s}"


def render(cfg):
    name = html.escape(cfg["nombre"])
    tagline = html.escape(cfg.get("tagline", "Carta"))
    detalle = html.escape(cfg.get("detalle", ""))
    accent = cfg.get("accent", "#C8552B")
    moneda = cfg.get("moneda", "$")
    wa = cfg.get("whatsapp")
    msg = cfg.get("mensaje", "Hola! Quiero hacer un pedido")
    sheet = cfg.get("sheet_csv", "")

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
            rows.append(
                f'<li class="item"><div class="it"><h3>{html.escape(it["nombre"])}{tags}</h3>{desc}</div>'
                f'<span class="price">{fmt_price(it.get("precio"), moneda)}</span></li>'
            )
        secs.append(f'<section id="{cid}"><h2>{html.escape(cat["nombre"])}</h2><ul>{"".join(rows)}</ul></section>')

    wa_btn = ""
    if wa:
        from urllib.parse import quote
        wa_btn = (f'<a class="wa" href="https://wa.me/{wa}?text={quote(msg)}" target="_blank" rel="noopener">'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 2.9 2.9 0 0 0-.9 2.2 5 5 0 0 0 1.1 2.7 11.5 11.5 0 0 0 4.4 3.9c1.6.7 2.3.8 3.1.6a2.6 2.6 0 0 0 1.7-1.2 2 2 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/></svg>'
                  f'Pedir por WhatsApp</a>')

    sheet_js = ""
    if sheet:
        sheet_js = f"""
<script>
(async () => {{
  try {{
    const r = await fetch({json.dumps(sheet)}, {{cache: "no-store"}});
    if (!r.ok) return;
    const rows = r.text().then ? (await r.text()).split(/\\r?\\n/).map(l => l.split(",")) : [];
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
        p: (row[ix("precio")] || "").trim(), t: (row[ix("tags")] || "").split("|").map(s => s.trim()).filter(Boolean)}});
    }}
    if (!cats.size) return;
    const esc = s => s.replace(/[&<>"]/g, ch => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[ch]);
    const fmt = p => {{ const n = Number(p); return isNaN(n) ? esc(p) : {json.dumps(moneda)} + " " + n.toLocaleString("es-AR", {{maximumFractionDigits: 0}}); }};
    let i = 0, nav = "", secs = "";
    for (const [c, items] of cats) {{
      const id = "c" + (i++);
      nav += `<a href="#${{id}}">${{esc(c)}}</a>`;
      secs += `<section id="${{id}}"><h2>${{esc(c)}}</h2><ul>` + items.map(it =>
        `<li class="item"><div class="it"><h3>${{esc(it.n)}}${{it.t.map(t => `<span class="tag">${{esc(t)}}</span>`).join("")}}</h3>${{it.d ? `<p class="desc">${{esc(it.d)}}</p>` : ""}}</div><span class="price">${{fmt(it.p)}}</span></li>`
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
.wa {{ position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(16px + env(safe-area-inset-bottom, 0px)); display: inline-flex; align-items: center; gap: 8px; background: #25D366; color: #fff; text-decoration: none; font-weight: 700; padding: 12px 20px; border-radius: 999px; white-space: nowrap; box-shadow: 0 6px 18px rgba(0,0,0,.18); }}
.wa svg {{ width: 20px; height: 20px; fill: currentColor; }}
.foot {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 28px; }}
</style></head><body>
<div class="wrap">
  <header>
    <div class="brand">{html.escape(cfg["nombre"][:1].upper())}</div>
    <h1>{name}</h1>
    <p class="tag-line">{tagline}{(" · " + detalle) if detalle else ""}</p>
  </header>
  <nav class="nav" aria-label="Categorías">{"".join(nav)}</nav>
  <main>{"".join(secs)}</main>
  <p class="foot">Los precios pueden cambiar sin previo aviso.</p>
</div>
{wa_btn}{sheet_js}
</body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: pagina_menu.py config.json [salida.html]")
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("index.html")
    out.write_text(render(cfg), encoding="utf-8")
    print(out)
