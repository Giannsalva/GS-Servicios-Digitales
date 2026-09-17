#!/usr/bin/env python3
"""
Página de reservas de turnos para un comercio. Una sola página: elegís servicio, día,
horario, dejás tus datos y recibís la confirmación por mail (backend: _tools/turnos/Code.gs
en Google Apps Script). Si "api_url" está vacío, la página corre en modo demo (simula
disponibilidad y no envía nada).

Uso:
  python3 pagina_turnos.py config.json [salida.html]

config.json:
{
  "nombre": "Bar Central",
  "titulo": "Reservá tu lugar",
  "detalle": "Elegí el día y el horario. Te llega la confirmación por mail.",
  "accent": "#C8552B",
  "api_url": "https://script.google.com/macros/s/.../exec",
  "whatsapp": "5491137845392",
  "direccion": "San Martín 1234, Godoy Cruz, Mendoza",
  "volver": "https://.../cliente-demo/",
  "dias_adelante": 30,
  "intervalo_min": 30,
  "horarios": {"lun_vie": "09:00-13:00, 16:00-20:00", "sab": "09:00-14:00", "dom": ""},
  "servicios": [
    {"id": "mesa2", "nombre": "Mesa para 2", "duracion": 90, "descripcion": "Reserva de mesa para dos"},
    {"id": "mesa4", "nombre": "Mesa para 4", "duracion": 90, "descripcion": "Hasta cuatro personas"}
  ],
  "campos_extra": [{"id": "personas", "label": "¿Cuántos son?", "tipo": "number"}],
  "notas": true
}
"servicios", "horarios" e "intervalo_min" tienen que coincidir con la planilla del Apps Script
(la página los usa para dibujar el calendario; la disponibilidad real siempre viene del API).
"""
import html
import json
import sys
from pathlib import Path


def render(cfg):
    e = html.escape
    name = e(cfg["nombre"])
    accent = cfg.get("accent", "#C8552B")
    js_cfg = json.dumps({
        "api": cfg.get("api_url", ""),
        "dias": cfg.get("dias_adelante", 30),
        "intervalo": cfg.get("intervalo_min", 30),
        "horarios": cfg.get("horarios", {}),
        "servicios": cfg.get("servicios", []),
        "whatsapp": cfg.get("whatsapp", ""),
        "nombre": cfg["nombre"],
    }, ensure_ascii=False)
    extra = "".join(
        f'<label>{e(c["label"])}<input name="{e(c["id"])}" type="{e(c.get("tipo", "text"))}" {"required" if c.get("req") else ""}></label>'
        for c in cfg.get("campos_extra", []))
    notas = '<label>Algo que tengamos que saber (opcional)<textarea name="notas" rows="2"></textarea></label>' if cfg.get("notas", True) else ""
    volver = f'<a class="back" href="{e(cfg["volver"])}">← Volver</a>' if cfg.get("volver") else ""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(cfg.get("titulo", "Reservas"))} · {name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@500;600;700&display=swap">
<style>
:root {{ --accent: {accent}; --bg: #F7F5F2; --card: #FFFFFF; --ink: #1E1B18; --muted: #6B645D; --line: #E8E3DD; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; }} }}
:root[data-theme="dark"] {{ --bg: #15130F; --card: #201D18; --ink: #F4EFE8; --muted: #A79F95; --line: #322D26; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Manrope, "Segoe UI", system-ui, sans-serif; line-height: 1.45; }}
main {{ max-width: 560px; margin: 0 auto; padding: 20px 16px 56px; }}
.back {{ color: var(--muted); text-decoration: none; font-size: 14px; }}
h1 {{ font-family: Fraunces, Georgia, serif; font-size: 32px; margin: 8px 0 4px; letter-spacing: -0.01em; }}
.sub {{ color: var(--muted); margin: 0 0 20px; }}
.brand {{ font-size: 13px; color: var(--accent); font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }}
h2 {{ font-size: 15px; margin: 22px 0 10px; color: var(--muted); font-weight: 700; }}
.srv {{ display: grid; gap: 8px; }}
.srv button, .days button, .slots button {{ font: inherit; cursor: pointer; border: 1px solid var(--line); background: var(--card); color: var(--ink); border-radius: 12px; }}
.srv button {{ text-align: left; padding: 12px 14px; display: flex; justify-content: space-between; gap: 10px; align-items: center; }}
.srv button small {{ display: block; color: var(--muted); font-weight: 500; }}
.srv .dur {{ color: var(--muted); font-size: 13px; white-space: nowrap; }}
.days {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; scrollbar-width: none; }}
.days button {{ flex: none; width: 64px; padding: 10px 0; text-align: center; font-weight: 700; }}
.days button small {{ display: block; color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }}
.days button:disabled {{ opacity: .35; cursor: default; }}
.slots {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(84px, 1fr)); gap: 8px; }}
.slots button {{ padding: 10px 0; font-weight: 700; }}
.sel {{ border-color: var(--accent) !important; background: var(--accent) !important; color: #fff !important; }}
.sel small, .sel .dur {{ color: rgba(255,255,255,.85) !important; }}
.msg {{ color: var(--muted); font-size: 14px; padding: 10px 0; }}
form {{ display: grid; gap: 12px; margin-top: 8px; }}
label {{ display: grid; gap: 4px; font-size: 14px; font-weight: 600; }}
input, textarea {{ font: inherit; padding: 11px 12px; border: 1px solid var(--line); border-radius: 10px; background: var(--card); color: var(--ink); }}
.hp {{ position: absolute; left: -9999px; }}
.cta {{ font: inherit; font-weight: 700; font-size: 16px; padding: 14px; border: 0; border-radius: 999px; background: var(--accent); color: #fff; cursor: pointer; }}
.cta:disabled {{ opacity: .6; cursor: wait; }}
.err {{ color: #B42318; font-size: 14px; }}
.ok {{ background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px; margin-top: 20px; }}
.ok h2 {{ font-family: Fraunces, Georgia, serif; font-size: 24px; color: var(--accent); margin: 0 0 8px; }}
.ok .big {{ font-size: 18px; margin: 6px 0; }}
.wa {{ display: inline-flex; align-items: center; gap: 8px; margin-top: 14px; padding: 12px 18px; border-radius: 999px; background: #25D366; color: #fff; text-decoration: none; font-weight: 700; }}
.demo {{ background: #FEF3C7; color: #78350F; border-radius: 10px; padding: 10px 12px; font-size: 13px; margin-bottom: 14px; }}
.hidden {{ display: none; }}
footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 32px; }}
</style></head><body><main>
{volver}
<div class="brand">{name}</div>
<h1>{e(cfg.get("titulo", "Reservá tu lugar"))}</h1>
<p class="sub">{e(cfg.get("detalle", "Elegí el día y el horario. Te llega la confirmación por mail."))}</p>
<div id="demo" class="demo hidden">Modo demo: la disponibilidad es simulada y no se envían mails.</div>

<section id="paso1"><h2>1 · ¿Qué reservás?</h2><div class="srv" id="srv"></div></section>
<section id="paso2" class="hidden"><h2>2 · ¿Qué día?</h2><div class="days" id="days"></div></section>
<section id="paso3" class="hidden"><h2>3 · ¿A qué hora?</h2><div class="slots" id="slots"></div><div class="msg" id="slotmsg"></div></section>
<section id="paso4" class="hidden"><h2>4 · Tus datos</h2>
<form id="f">
  <label>Nombre y apellido<input name="nombre" required autocomplete="name"></label>
  <label>Teléfono<input name="telefono" type="tel" required autocomplete="tel" placeholder="261 555 1234"></label>
  <label>Email<input name="email" type="email" required autocomplete="email"></label>
  {extra}
  {notas}
  <input class="hp" name="hp" tabindex="-1" autocomplete="off">
  <div class="err" id="err"></div>
  <button class="cta" id="btn" type="submit">Confirmar reserva</button>
</form></section>
<div id="ok" class="ok hidden"></div>
<footer>{name}{(" · " + e(cfg["direccion"])) if cfg.get("direccion") else ""}</footer>
</main>
<script>
const CFG = {js_cfg};
const DEMO = !CFG.api;
const $ = s => document.querySelector(s);
const st = {{ srv: null, fecha: null, hora: null }};
const DIAS = ["dom","lun","mar","mié","jue","vie","sáb"];
const MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
if (DEMO) $("#demo").classList.remove("hidden");

function ymd(d) {{ return d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,"0") + "-" + String(d.getDate()).padStart(2,"0"); }}
function rangos(d) {{
  const dow = d.getDay();
  const h = CFG.horarios || {{}};
  const key = dow === 0 ? "dom" : dow === 6 ? "sab" : "lun_vie";
  const txt = (h[DIAS[dow].replace("é","e").replace("á","a")] ?? h[key]) || "";
  return String(txt).split(",").map(s => s.trim()).filter(Boolean).map(p => p.split("-").map(m));
}}
function m(hhmm) {{ const [a,b] = hhmm.split(":"); return +a*60 + +(b||0); }}
function hh(x) {{ return String(Math.floor(x/60)).padStart(2,"0") + ":" + String(x%60).padStart(2,"0"); }}

// paso 1
CFG.servicios.forEach(s => {{
  const b = document.createElement("button"); b.type = "button";
  b.innerHTML = `<span>${{s.nombre}}<small>${{s.descripcion||""}}</small></span><span class="dur">${{s.duracion}} min</span>`;
  b.onclick = () => {{ st.srv = s; st.fecha = st.hora = null; [...$("#srv").children].forEach(x => x.classList.remove("sel")); b.classList.add("sel"); dias(); }};
  $("#srv").appendChild(b);
}});

// paso 2
function dias() {{
  $("#paso2").classList.remove("hidden"); $("#paso3").classList.add("hidden"); $("#paso4").classList.add("hidden");
  const c = $("#days"); c.innerHTML = "";
  const hoy = new Date(); hoy.setHours(0,0,0,0);
  for (let i = 0; i < CFG.dias; i++) {{
    const d = new Date(hoy); d.setDate(hoy.getDate() + i);
    const b = document.createElement("button"); b.type = "button";
    b.innerHTML = `<small>${{i===0?"hoy":DIAS[d.getDay()]}}</small>${{d.getDate()}}<small>${{MESES[d.getMonth()]}}</small>`;
    b.disabled = rangos(d).length === 0;
    b.onclick = () => {{ st.fecha = ymd(d); st.hora = null; [...c.children].forEach(x => x.classList.remove("sel")); b.classList.add("sel"); slots(); }};
    c.appendChild(b);
  }}
  $("#paso2").scrollIntoView({{ behavior: "smooth", block: "start" }});
}}

// paso 3
async function slots() {{
  $("#paso3").classList.remove("hidden"); $("#paso4").classList.add("hidden");
  const c = $("#slots"); c.innerHTML = ""; $("#slotmsg").textContent = "Buscando horarios…";
  let lista = [];
  try {{
    if (DEMO) lista = demoSlots();
    else {{
      const r = await fetch(CFG.api + "?action=disponibilidad&fecha=" + st.fecha + "&servicio=" + encodeURIComponent(st.srv.id));
      const j = await r.json(); if (j.error) throw new Error(j.error); lista = j.slots || [];
    }}
  }} catch (e) {{ $("#slotmsg").textContent = "No pudimos cargar los horarios. Probá de nuevo."; return; }}
  $("#slotmsg").textContent = lista.length ? "" : "No quedan horarios ese día. Probá con otro.";
  lista.forEach(h => {{
    const b = document.createElement("button"); b.type = "button"; b.textContent = h;
    b.onclick = () => {{ st.hora = h; [...c.children].forEach(x => x.classList.remove("sel")); b.classList.add("sel"); $("#paso4").classList.remove("hidden"); $("#paso4").scrollIntoView({{ behavior: "smooth", block: "start" }}); }};
    c.appendChild(b);
  }});
}}
function demoSlots() {{
  const d = new Date(st.fecha + "T12:00:00"); const out = [];
  const ahora = new Date(); const minIni = ahora.getTime() + 2*3600000;
  rangos(d).forEach(([a,b]) => {{ for (let t = a; t + st.srv.duracion <= b; t += CFG.intervalo) {{
    const ini = new Date(st.fecha + "T" + hh(t) + ":00");
    if (ini.getTime() < minIni) continue;
    if ((t/CFG.intervalo + d.getDate()) % 4 === 1) continue; // simula ocupados
    out.push(hh(t));
  }} }});
  return out;
}}

// paso 4
$("#f").onsubmit = async ev => {{
  ev.preventDefault(); $("#err").textContent = "";
  const fd = new FormData(ev.target); const p = Object.fromEntries(fd.entries());
  const extras = Object.keys(p).filter(k => !["nombre","telefono","email","notas","hp"].includes(k)).map(k => k + ": " + p[k]).filter(x => !x.endsWith(": "));
  const body = {{ servicio: st.srv.id, fecha: st.fecha, hora: st.hora, nombre: p.nombre.trim(), telefono: p.telefono.trim(), email: p.email.trim(), notas: [p.notas||"", ...extras].filter(Boolean).join(" · "), hp: p.hp }};
  $("#btn").disabled = true; $("#btn").textContent = "Reservando…";
  try {{
    let j;
    if (DEMO) {{ await new Promise(r => setTimeout(r, 700)); j = {{ ok: true, id: "DEMO", fecha: st.fecha, hora: st.hora, servicio: st.srv.nombre }}; }}
    else {{
      const r = await fetch(CFG.api, {{ method: "POST", headers: {{ "Content-Type": "text/plain;charset=utf-8" }}, body: JSON.stringify(body) }});
      j = await r.json();
    }}
    if (j.error) throw new Error(j.error);
    listo(j, body);
  }} catch (e) {{ $("#err").textContent = e.message || "No se pudo reservar. Probá de nuevo."; if (String(e.message).includes("disponible")) slots(); }}
  $("#btn").disabled = false; $("#btn").textContent = "Confirmar reserva";
}};
function listo(j, b) {{
  ["#paso1","#paso2","#paso3","#paso4"].forEach(s => $(s).classList.add("hidden"));
  const d = new Date(j.fecha + "T12:00:00");
  const fecha = `${{DIAS[d.getDay()]}} ${{d.getDate()}} de ${{MESES[d.getMonth()]}}`;
  const wa = CFG.whatsapp ? `https://wa.me/${{CFG.whatsapp}}?text=${{encodeURIComponent("Hola! Confirmo mi reserva " + j.id + ": " + j.servicio + ", " + fecha + " a las " + j.hora + ". " + b.nombre)}}` : "";
  $("#ok").innerHTML = `<h2>¡Listo, ${{b.nombre.split(" ")[0]}}!</h2><div class="big"><b>${{j.servicio}}</b></div><div class="big">${{fecha}} · <b>${{j.hora}}</b> hs</div>
    <p>${{DEMO ? "En la versión real te llega un mail de confirmación con el turno para agendar y un recordatorio el día anterior." : "Te enviamos la confirmación a <b>" + b.email + "</b> (revisá spam) y un recordatorio el día anterior."}}</p>
    ${{wa ? `<a class="wa" href="${{wa}}" target="_blank" rel="noopener">Confirmar por WhatsApp</a>` : ""}}
    <p style="color:var(--muted);font-size:13px;margin-top:14px">Reserva ${{j.id}}</p>`;
  $("#ok").classList.remove("hidden"); window.scrollTo({{ top: 0, behavior: "smooth" }});
}}
</script></body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: pagina_turnos.py config.json [salida.html]")
    src = Path(sys.argv[1])
    cfg = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("index.html")
    out.write_text(render(cfg), encoding="utf-8")
    print(out)
