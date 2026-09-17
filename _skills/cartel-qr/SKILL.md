---
name: cartel-qr
description: "Cartel QR imprimible (15x21 cm, PDF + PNG) para un comercio con estética según el destino (reseñas Google, Instagram, Facebook, WhatsApp) y página de links publicada en GitHub Pages (giannsalva.github.io/GS-Servicios-Digitales/slug/), con todo lo del cliente archivado en el repo Giannsalva/GS-Servicios-Digitales. Usar cuando Gian pida un cartel, QR, kit QR o página de links para un local."
---

# Kit QR para comercios

Producto que Gian vende a negocios de barrio. Dos piezas, que se combinan:

1. **Cartel QR** (15x21 cm, PDF para imprimir + PNG para WhatsApp) con el nombre del comercio y una estética que imita al destino, no la identidad de Gian.
2. **Página de links** (estilo link-in-bio): una sola página con N botones a WhatsApp, Instagram, Facebook, reseñas, cómo llegar, carta, web, teléfono, mail, TikTok. Se publica en GitHub Pages y queda en `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/`; esa URL es la que el local pone en su bio de Instagram y la que lleva el cartel tipo `links`.

No publicar la página como Artifact: los artefactos son privados y quien escanea sin estar logueado ve la pantalla de Claude. Ya pasó; el hosting es siempre GitHub Pages.

## Paso 0: la plantilla del cliente (siempre)

El servicio **arranca por la plantilla de `_plantillas/`**, no por preguntas sueltas.

1. Si el cliente todavía no la completó, mandarle el `.docx` de `_plantillas/docx/`.
2. Cuando la devuelve (archivo, foto o audios de WhatsApp), transcribirla y archivarla como
   `<slug>/alta-qr-links.md` en el repo: ese archivo es la fuente de verdad del cliente.
3. **Leer el alta antes de generar nada.** De ahí salen todos los datos; nunca inventar nombres,
   links, precios ni teléfonos.
4. Lo que quedó vacío se pregunta una sola vez, todo junto, y se completa en el mismo archivo.
   Lo que sigue faltando se marca `PENDIENTE` y no se publica ni se imprime nada que dependa de eso.
5. Si el cliente ya tiene otro servicio contratado, los datos del comercio se copian de su alta
   anterior en vez de volver a pedirlos.

Mapeo de `_plantillas/qr-links.md` al trabajo:

| Bloque de la plantilla | Dónde va |
|---|---|
| Datos del comercio | `<slug>/config.json`: `nombre`, `tagline` (rubro), `accent`, y el logo |
| Horarios y dirección | `detalle` de la página de links |
| Botones, en el orden indicado | `links[]` (`tipo`, `label`, `sub`, `url`) |
| Mensaje precargado de WhatsApp | el `?text=` del `wa.me` |
| Carteles marcados | una corrida de `cartel_qr.py` por cartel, salida en `<slug>/carteles/` |
| Dónde van, cuántas copias, tamaño, plastificado | qué se entrega y en qué formato se imprime |
| Link de reseña de Google | `--url` del cartel de reseñas (si el cliente mandó el de Maps, sacar el de "Escribir reseña") |

Si en la plantilla falta un link, **no inventarlo ni deducirlo**: un QR impreso que no lleva a
ningún lado es plata perdida en papel.

## Qué pedir antes de generar

Solo lo que falte. Nunca inventar URLs, nombres ni teléfonos.

- **Nombre del comercio** tal como quiere verlo impreso.
- **Para un cartel simple**, el destino:
  - Google: link de Maps (`maps.app.goo.gl/...`) o, mejor, el link directo de "Escribir reseña" (`search.google.com/local/writereview?placeid=...` o `g.page/r/.../review`), que el dueño obtiene desde su Perfil de Empresa → "Pedir reseñas". Ambos van tal cual en `--url`.
  - Instagram / Facebook: URL del perfil. Opcional `--handle @usuario`.
  - WhatsApp: número con código de país sin `+` ni espacios (Argentina: `549` + área + número) y mensaje precargado opcional; el script arma el `wa.me`.
- **Para la página de links**: lista de botones (tipo, texto, URL, subtexto opcional), tagline, horario/dirección, color de acento (si tiene marca) y logo (opcional, archivo de imagen).
- **Token de GitHub** para hacer el push: Gian lo dejó en la conversación del 17/09/2026 ("Kit QR") y pidió reutilizarlo; si no está en el chat actual, pedírselo. Es un fine-grained token con acceso solo al repo `Giannsalva/GS-Servicios-Digitales`.

## Procedimiento

1. Dependencias en el contenedor (una vez por sesión):
   ```bash
   python3 -c "import qrcode, reportlab, PIL" 2>/dev/null || pip install qrcode reportlab pillow --break-system-packages -q
   pip install pyzbar --break-system-packages -q 2>/dev/null
   ```
2. Escribir los dos scripts de abajo en el directorio de trabajo (`cartel_qr.py`, `pagina_links.py`) si no existen ya en esta sesión.
3. **Página de links** (solo si la piden):
   - Slug del cliente: minúsculas, sin acentos, guiones (`bar-central`). Armar `<slug>/config.json` con el formato del docstring y generar el documento completo:
     ```bash
     python3 pagina_links.py <slug>/config.json <slug>/index.html --standalone
     ```
   - Publicar en GitHub Pages (ver sección siguiente). URL final: `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/`. El cartel tipo `links` se genera recién cuando la URL está definida, con `--out <slug>/carteles/cartel-links-<slug>.pdf`.
4. **Cartel**, un comando por cartel:
   ```bash
   python3 cartel_qr.py --nombre "Parque de la Costa" --url "https://maps.app.goo.gl/xxxx"
   python3 cartel_qr.py --nombre "Bar Central" --url "https://instagram.com/barcentral" --handle "@barcentral"
   python3 cartel_qr.py --nombre "Kiosco 24" --url "https://facebook.com/kiosco24"
   python3 cartel_qr.py --nombre "Peluquería Lu" --telefono 5492611234567 --mensaje "Hola! Quiero pedir un turno"
   python3 cartel_qr.py --nombre "Bar Central" --tipo links --url "https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/" --sub "WhatsApp · Carta · Instagram · Reseñas" --accent "#C8552B"
   ```
   El tipo se deduce de la URL; `--tipo` lo fuerza (obligatorio para `links`). `--sub` reemplaza el subtítulo, `--accent` el color del tipo `links`, `--out ruta.pdf` el nombre de salida (por defecto `cartel-<tipo>-<slug>.pdf` + `.png` a 300 dpi). Todo cartel de un cliente se guarda en `<slug>/carteles/` del repo, aunque no tenga página de links.
5. **Verificar siempre** antes de entregar: mirar el PNG (nombre entero, nada superpuesto) y decodificar el QR:
   ```bash
   python3 -c "from PIL import Image; from pyzbar.pyzbar import decode; print(decode(Image.open('ARCHIVO.png'))[0].data.decode())"
   ```
6. Guardar todo en el repo (sección siguiente), actualizar la tabla del `README.md`, y entregar PDF + PNG (y la URL de la página si aplica) diciendo a qué URL apunta cada QR.

## Repo `Giannsalva/GS-Servicios-Digitales`: archivo de clientes + hosting

Público, rama `main`, GitHub Pages desde `/ (root)`, con `.nojekyll`. Todo lo que se genera para un cliente se guarda ahí:

```
GS-Servicios-Digitales/
├── _tools/                cartel_qr.py, pagina_links.py (copia de los scripts de esta skill)
├── <slug>/
│   ├── index.html         página publicada  → https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/
│   ├── config.json        datos de la página (para editar links y regenerar)
│   └── carteles/          PDF y PNG de cada cartel del cliente (links, google, instagram, ...)
├── index.html             vacío, evita listar clientes en la raíz
└── README.md              tabla de clientes con su URL
```

`cliente-demo/` es el ejemplo ficticio (Bar Central). Los carteles también quedan descargables por URL (`.../GS-Servicios-Digitales/<slug>/carteles/<archivo>.pdf`).

Copia local de trabajo: `Desktop\Gianluca\GS-Servicios-Digitales` (ruta real `C:\Users\gsalvatori\OneDrive - AXXON GROUP\Escritorio\Gianluca\GS-Servicios-Digitales`), que en `device_bash` aparece como `$HOME/mnt/GS-Servicios-Digitales` cuando está conectada. Local y GitHub deben quedar iguales.

### Cómo subir (desde la computadora de Gian)

El contenedor no puede hacer push a ese repo (el proxy bloquea repos no autorizados en la sesión, aun con token). Se hace con `device_bash`; requiere que la carpeta `GS-Servicios-Digitales` esté conectada a la conversación (si no aparece en `ls $HOME/mnt/`, pedirle a Gian que la agregue con "Add folder"; el Escritorio no se puede solicitar con `device_request_folder_access`).

1. En el contenedor, armar los archivos del cliente con la estructura de arriba y empaquetarlos: `zip -qr /mnt/user-data/outputs/links-repo.zip . -x '.git/*'`.
2. `device_commit_files` del zip a `<ruta real>\_upload.zip` (con `force: true` si ya existe).
3. En `device_bash`: descomprimir sobre `$HOME/mnt/GS-Servicios-Digitales` (script Python, saltando `.git/`), vaciar el zip con `: > _upload.zip` (no se puede borrar), clonar el repo en `/tmp` con el token, copiar las carpetas, commit y push:
   ```bash
   T=<token>; rm -rf /tmp/gs && git clone -q "https://x-access-token:$T@github.com/Giannsalva/GS-Servicios-Digitales.git" /tmp/gs \
   && cp -r "$HOME/mnt/GS-Servicios-Digitales/.nojekyll" "$HOME/mnt/GS-Servicios-Digitales/README.md" "$HOME/mnt/GS-Servicios-Digitales/index.html" "$HOME/mnt/GS-Servicios-Digitales/_tools" "$HOME/mnt/GS-Servicios-Digitales/<slug>" /tmp/gs/ \
   && cd /tmp/gs && git config user.email "gsalvatori@axxonconsulting.com" && git config user.name "Gianluca Salvatori" \
   && git add -A && git commit -qm "<Nombre>: página y carteles" && git push -q origin main && git remote set-url origin https://github.com/Giannsalva/GS-Servicios-Digitales.git && echo OK
   ```
   Git se ejecuta en `/tmp` porque no puede borrar sus locks dentro de carpetas conectadas. Nunca dejar el token en el remote ni en archivos del repo. No renombrar el repo ni las carpetas de clientes: cambia la URL y los QR impresos dejan de funcionar. Para renombrar o borrar una carpeta de cliente, usar `git rm -r` en el clon; en la carpeta local no se puede borrar, se renombra a `_old-...` y Gian la elimina.
4. Verificar con WebFetch desde el contenedor que `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/` responda (1–2 min). Desde `device_bash` no se llega a github.io.
5. Si el push falla con 403 desde la máquina de Gian, entregarle el zip y los comandos `git` para que lo suba él.

## Ajustes frecuentes

- Textos por tipo en `THEMES` de `cartel_qr.py`; colores, tipografía y layout de la página en el bloque `<style>` de `pagina_links.py`.
- Tamaño del cartel: `W, H = 150 * mm, 210 * mm`. Para 10x15 usar `100 * mm, 150 * mm` y `qs` ≈ `54 * mm`.
- Nombres largos se achican solos hasta 14 pt; si no entra, sugerir nombre corto.
- Íconos disponibles en la página: whatsapp, instagram, facebook, google (reseña), maps, web, menu, tel, mail, tiktok. Un tipo desconocido usa el ícono web.
- La página tiene tema claro y oscuro; el acento se aplica al avatar y al foco. Si el local no tiene logo, se muestra la inicial sobre el color de acento.
- Para cambiar links de un cliente ya publicado: editar su `config.json`, regenerar con `--standalone`, y repetir el push. El QR impreso no cambia. Si se renombra la carpeta cambia la URL y hay que regenerar el cartel `links`.

## Script `cartel_qr.py`

```python
#!/usr/bin/env python3
import argparse
import unicodedata
import io
import math
import re
import subprocess
import urllib.parse
from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = 150 * mm, 210 * mm

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Sans", FONT_DIR + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansB", FONT_DIR + "LiberationSans-Bold.ttf"))

THEMES = {
    "google": {
        "bg": "#FFFFFF", "ink": "#202124", "muted": "#5F6368", "accent": "#4285F4",
        "qr": "#202124", "card": "#F1F3F4", "kicker": "TU OPINIÓN NOS AYUDA A CRECER",
        "headline": "¿Te gustó tu visita?", "sub": "Dejanos tu reseña en Google",
        "cta": "Escaneá con la cámara", "cta2": "y contanos tu experiencia en 30 segundos",
        "footer": "¡Gracias por elegirnos!",
    },
    "instagram": {
        "bg": None, "ink": "#FFFFFF", "muted": "#FFE9F3", "accent": "#FFFFFF",
        "qr": "#8A1C6B", "card": "#FFFFFF", "kicker": "ESTAMOS EN INSTAGRAM",
        "headline": "¡Seguinos!", "sub": "Novedades, promos y todo lo nuevo",
        "cta": "Escaneá con la cámara", "cta2": "y seguinos en un toque",
        "footer": "¡Gracias por elegirnos!",
    },
    "facebook": {
        "bg": "#1877F2", "ink": "#FFFFFF", "muted": "#DCE9FF", "accent": "#FFFFFF",
        "qr": "#0B3F8F", "card": "#FFFFFF", "kicker": "ESTAMOS EN FACEBOOK",
        "headline": "¡Seguinos!", "sub": "Enterate de todo lo que pasa en el local",
        "cta": "Escaneá con la cámara", "cta2": "y dale me gusta a nuestra página",
        "footer": "¡Gracias por elegirnos!",
    },
    "links": {
        "bg": "#1E1B18", "ink": "#FFFFFF", "muted": "#D9D2C9", "accent": "#C8552B",
        "qr": "#1E1B18", "card": "#FFFFFF", "kicker": "TODOS NUESTROS LINKS EN UN SOLO LUGAR",
        "headline": "¡Encontranos en todos lados!", "sub": "WhatsApp · Instagram · Reseñas · Web",
        "cta": "Escaneá con la cámara", "cta2": "y elegí por dónde contactarnos",
        "footer": "¡Gracias por elegirnos!",
    },
    "whatsapp": {
        "bg": "#075E54", "ink": "#FFFFFF", "muted": "#CFEFE6", "accent": "#25D366",
        "qr": "#075E54", "card": "#FFFFFF", "kicker": "ATENCIÓN POR WHATSAPP",
        "headline": "¡Escribinos!", "sub": "Pedidos, consultas y turnos",
        "cta": "Escaneá con la cámara", "cta2": "y se abre el chat con nosotros",
        "footer": "Respondemos a la brevedad",
    },
}


def detect_type(url):
    u = url.lower()
    if "instagram.com" in u:
        return "instagram"
    if "facebook.com" in u or "fb.com" in u or "fb.me" in u:
        return "facebook"
    if "wa.me" in u or "whatsapp.com" in u:
        return "whatsapp"
    return "google"


def qr_image(url, color):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_H)
    q.add_data(url)
    q.make(fit=True)
    img = q.make_image(fill_color=color, back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def star(c, cx, cy, r, color):
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def fit_font(c, text, font, max_size, max_w, min_size=14):
    s = max_size
    while s > min_size and c.stringWidth(text, font, s) > max_w:
        s -= 0.5
    return s


def badge_google(c, cx, cy, r):
    c.setFillColor(HexColor("#FFFFFF"))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setFillColor(HexColor("#4285F4"))
    c.setFont("SansB", r * 1.9)
    c.drawCentredString(cx, cy - r * 0.62, "G")


def badge_instagram(c, cx, cy, r):
    c.setFillColor(HexColor("#FFFFFF"))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#C13584"))
    c.setLineWidth(r * 0.16)
    c.roundRect(cx - r * 0.55, cy - r * 0.55, r * 1.1, r * 1.1, r * 0.3, stroke=1, fill=0)
    c.circle(cx, cy, r * 0.26, stroke=1, fill=0)
    c.setFillColor(HexColor("#C13584"))
    c.circle(cx + r * 0.36, cy + r * 0.36, r * 0.07, stroke=0, fill=1)


def badge_facebook(c, cx, cy, r):
    c.setFillColor(HexColor("#FFFFFF"))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setFillColor(HexColor("#1877F2"))
    c.setFont("SansB", r * 1.9)
    c.drawCentredString(cx + r * 0.05, cy - r * 0.62, "f")


def badge_links(c, cx, cy, r):
    c.setFillColor(HexColor(THEMES["links"]["accent"]))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(r * 0.18)
    c.roundRect(cx - r * 0.62, cy - r * 0.14, r * 0.7, r * 0.42, r * 0.21, stroke=1, fill=0)
    c.roundRect(cx - r * 0.08, cy - r * 0.28, r * 0.7, r * 0.42, r * 0.21, stroke=1, fill=0)


def badge_whatsapp(c, cx, cy, r):
    c.setFillColor(HexColor("#25D366"))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(r * 0.16)
    c.circle(cx, cy, r * 0.55, stroke=1, fill=0)
    c.setFillColor(HexColor("#FFFFFF"))
    p = c.beginPath()
    p.moveTo(cx - r * 0.55, cy - r * 0.2)
    p.lineTo(cx - r * 0.62, cy - r * 0.62)
    p.lineTo(cx - r * 0.2, cy - r * 0.5)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


BADGES = {"links": badge_links, "google": badge_google, "instagram": badge_instagram, "facebook": badge_facebook, "whatsapp": badge_whatsapp}


def draw_background(c, tipo, t):
    if tipo == "instagram":
        from PIL import Image
        stops = [(249, 206, 52), (238, 42, 123), (98, 40, 215)]
        img = Image.new("RGB", (300, 420))
        px = img.load()
        for y in range(420):
            for x in range(300):
                f = (x / 300 + y / 420) / 2
                i = 0 if f < 0.5 else 1
                k = (f - 0.5 * i) / 0.5
                px[x, y] = tuple(int(stops[i][j] + (stops[i + 1][j] - stops[i][j]) * k) for j in range(3))
        buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        c.drawImage(ImageReader(buf), 0, 0, W, H)
        return
    c.setFillColor(HexColor(t["bg"]))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if tipo == "google":
        for col, x in [("#4285F4", 0), ("#EA4335", 1), ("#FBBC05", 2), ("#34A853", 3)]:
            c.setFillColor(HexColor(col))
            c.rect(x * W / 4, H - 5 * mm, W / 4, 5 * mm, stroke=0, fill=1)
    elif tipo == "facebook":
        c.setFillColor(HexColor("#0F63C9"))
        c.circle(W + 12 * mm, H + 8 * mm, 60 * mm, stroke=0, fill=1)
    elif tipo == "links":
        c.setFillColor(HexColor(t["accent"]))
        c.circle(W + 8 * mm, H + 6 * mm, 46 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor("#2B2722"))
        c.circle(-12 * mm, -10 * mm, 52 * mm, stroke=0, fill=1)
    elif tipo == "whatsapp":
        c.setFillColor(HexColor("#128C7E"))
        c.circle(-10 * mm, -12 * mm, 55 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor("#25D366"))
        c.circle(W + 10 * mm, H + 8 * mm, 42 * mm, stroke=0, fill=1)


def build(nombre, url, tipo, handle, out_pdf):
    t = THEMES[tipo]
    c = canvas.Canvas(str(out_pdf), pagesize=(W, H))
    p = c.beginPath(); p.rect(0, 0, W, H); c.clipPath(p, stroke=0)
    draw_background(c, tipo, t)

    ink, muted, accent = HexColor(t["ink"]), HexColor(t["muted"]), HexColor(t["accent"])
    top = H - (16 * mm if tipo == "google" else 12 * mm)

    c.setFillColor(accent if tipo != "google" else HexColor("#EA4335"))
    c.setFont("SansB", 10)
    c.drawCentredString(W / 2, top - 8 * mm, t["kicker"])

    name = nombre.upper()
    fs = fit_font(c, name, "SansB", 30, W - 20 * mm)
    c.setFillColor(ink)
    c.setFont("SansB", fs)
    c.drawCentredString(W / 2, top - 22 * mm, name)

    c.setFont("SansB", 22)
    c.drawCentredString(W / 2, top - 40 * mm, t["headline"])
    c.setFillColor(muted)
    c.setFont("Sans", 13)
    sub = t["sub"] if not (handle and tipo in ("instagram", "facebook")) else handle
    if tipo == "links":
        c.setFont("Sans", fit_font(c, sub, "Sans", 13, W - 24 * mm, 9))
    c.drawCentredString(W / 2, top - 49 * mm, sub)

    y_after_sub = top - 49 * mm
    if tipo == "google":
        for i in range(5):
            star(c, W / 2 + (i - 2) * 11 * mm, y_after_sub - 11 * mm, 4.2 * mm, HexColor("#FBBC05"))
        y_after_sub -= 12 * mm

    qs = 74 * mm if tipo == "google" else 78 * mm
    qx = (W - qs) / 2
    qy = y_after_sub - (14 if tipo == "google" else 18) * mm - qs
    c.setFillColor(HexColor(t["card"]))
    c.roundRect(qx - 7 * mm, qy - 7 * mm, qs + 14 * mm, qs + 14 * mm, 6 * mm, stroke=0, fill=1)
    c.drawImage(qr_image(url, t["qr"]), qx, qy, qs, qs)
    BADGES[tipo](c, qx + qs + 3 * mm, qy + qs + 3 * mm, 8 * mm)

    c.setFillColor(ink)
    c.setFont("SansB", 15)
    c.drawCentredString(W / 2, qy - 17 * mm, t["cta"])
    c.setFillColor(muted)
    c.setFont("Sans", 11)
    c.drawCentredString(W / 2, qy - 24 * mm, t["cta2"])

    c.setFillColor(accent if tipo != "google" else HexColor("#34A853"))
    c.setFont("SansB", 9.5)
    c.drawCentredString(W / 2, 9 * mm, t["footer"].upper())

    c.showPage()
    c.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--url")
    ap.add_argument("--tipo", choices=THEMES.keys())
    ap.add_argument("--telefono")
    ap.add_argument("--mensaje", default="")
    ap.add_argument("--handle")
    ap.add_argument("--out")
    ap.add_argument("--sub")
    ap.add_argument("--accent")
    a = ap.parse_args()

    url = a.url
    if a.telefono and not url:
        url = f"https://wa.me/{a.telefono}"
        if a.mensaje:
            url += "?text=" + urllib.parse.quote(a.mensaje)
    if not url:
        ap.error("Indicá --url o --telefono")
    tipo = a.tipo or detect_type(url)
    if a.sub:
        THEMES[tipo]["sub"] = a.sub
    if a.accent and tipo == "links":
        THEMES[tipo]["accent"] = a.accent

    plain = unicodedata.normalize("NFKD", a.nombre).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    out_pdf = Path(a.out) if a.out else Path(f"cartel-{tipo}-{slug}.pdf")
    build(a.nombre, url, tipo, a.handle, out_pdf)

    png_prefix = out_pdf.with_suffix("")
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile", str(out_pdf), str(png_prefix)], check=False)
    print(f"PDF: {out_pdf}")
    print(f"PNG: {png_prefix}.png")
    print(f"QR -> {url}")


if __name__ == "__main__":
    main()
```

## Script `pagina_links.py`

```python
#!/usr/bin/env python3
"""
Uso:
  python3 pagina_links.py config.json [salida.html] [--standalone]
  --standalone: documento HTML completo (GitHub Pages). Sin el flag, fragmento para Artifact.

config.json:
{
  "nombre": "Bar Central",
  "tagline": "Café de especialidad",
  "detalle": "Lun a Sáb 8 a 20 hs · San Martín 1234",
  "accent": "#C8552B",
  "logo": "logo.png",
  "links": [
    {"tipo": "whatsapp", "label": "Pedinos por WhatsApp", "sub": "Respondemos al toque", "url": "https://wa.me/549..."},
    {"tipo": "instagram", "label": "Instagram", "sub": "@barcentral", "url": "https://instagram.com/barcentral"},
    {"tipo": "google", "label": "Dejanos tu reseña", "url": "https://maps.app.goo.gl/..."},
    {"tipo": "maps", "label": "Cómo llegar", "url": "https://maps.app.goo.gl/..."},
    {"tipo": "facebook", "label": "Facebook", "url": "https://facebook.com/..."},
    {"tipo": "web", "label": "Nuestra web", "url": "https://..."},
    {"tipo": "menu", "label": "Ver la carta", "url": "https://..."},
    {"tipo": "tel", "label": "Llamanos", "url": "tel:+54261..."},
    {"tipo": "mail", "label": "Escribinos", "url": "mailto:..."},
    {"tipo": "tiktok", "label": "TikTok", "url": "https://tiktok.com/@..."}
  ]
}
Tipos de botón: whatsapp, instagram, facebook, google, maps, web, menu, tel, mail, tiktok.
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
               + doc.split("<style>", 1)[0]
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
```