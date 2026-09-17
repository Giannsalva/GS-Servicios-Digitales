#!/usr/bin/env python3
"""
Cartel QR para comercios. Genera un PDF (15x21 cm) y un PNG a 300 dpi con
identidad visual acorde al destino del QR.

Uso:
  python3 cartel_qr.py --nombre "Parque de la Costa" --url "https://maps.app.goo.gl/xxxx"
  python3 cartel_qr.py --nombre "Bar Central" --tipo instagram --url "https://instagram.com/barcentral"
  python3 cartel_qr.py --nombre "Peluquería Lu" --tipo whatsapp --telefono 5492611234567 --mensaje "Hola! Quiero un turno"
  python3 cartel_qr.py --nombre "Kiosco 24" --tipo facebook --url "https://facebook.com/kiosco24"

Tipos: google (reseñas), instagram, facebook, whatsapp, links (página con todos los links), menu (carta/catálogo). Si no se pasa --tipo, se
deduce de la URL. Requiere: qrcode, reportlab, pillow (pip install qrcode reportlab pillow).
"""
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
    "menu": {
        "bg": "#FBF7F1", "ink": "#1E1B18", "muted": "#6B645D", "accent": "#C8552B",
        "qr": "#1E1B18", "card": "#FFFFFF", "kicker": "NUESTRA CARTA DIGITAL",
        "headline": "¡Mirá la carta!", "sub": "Precios siempre actualizados",
        "cta": "Escaneá con la cámara", "cta2": "y elegí lo que más te guste",
        "footer": "¡Buen provecho!",
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
    if "/carta" in u or "/menu" in u or "/catalogo" in u:
        return "menu"
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


def badge_menu(c, cx, cy, r):
    c.setFillColor(HexColor(THEMES["menu"]["accent"]))
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(r * 0.16)
    for k in (-0.3, 0.0, 0.3):
        c.line(cx - r * 0.45, cy + r * k, cx + r * 0.45, cy + r * k)


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


BADGES = {"menu": badge_menu, "links": badge_links, "google": badge_google, "instagram": badge_instagram, "facebook": badge_facebook, "whatsapp": badge_whatsapp}


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
    elif tipo == "menu":
        c.setFillColor(HexColor("#F1E6D8"))
        c.circle(W + 10 * mm, H + 8 * mm, 50 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor(t["accent"]))
        c.circle(-14 * mm, -14 * mm, 40 * mm, stroke=0, fill=1)
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
    if tipo in ("links", "menu"):
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
    ap.add_argument("--nombre", required=True, help="Nombre del comercio")
    ap.add_argument("--url", help="Destino del QR (Maps, reseña, Instagram, Facebook, wa.me)")
    ap.add_argument("--tipo", choices=THEMES.keys(), help="Se deduce de la URL si no se indica")
    ap.add_argument("--telefono", help="WhatsApp con código de país, sin + ni espacios (ej. 5492611234567)")
    ap.add_argument("--mensaje", default="", help="Mensaje precargado para WhatsApp")
    ap.add_argument("--handle", help="Usuario a mostrar bajo el título (ej. @barcentral)")
    ap.add_argument("--out", help="Ruta del PDF de salida")
    ap.add_argument("--sub", help="Subtítulo a mostrar (ej. redes disponibles en tipo links)")
    ap.add_argument("--accent", help="Color de acento hex para tipo links (ej. #C8552B)")
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
    if a.accent and tipo in ("links", "menu"):
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
