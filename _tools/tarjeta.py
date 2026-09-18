#!/usr/bin/env python3
"""Tarjeta de presentación de Gianluca Salvatori (90x55 mm, frente y dorso).

    python3 _tools/tarjeta.py [salida.pdf]

Genera el PDF de 2 páginas (página 1 frente, página 2 dorso) listo para imprimir,
y un PNG de cada cara a 300 dpi para mandar por WhatsApp.
El QR del dorso abre un WhatsApp a Gian con el mensaje ya escrito.
"""

import io
import sys
from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

NOMBRE = "Gianluca Salvatori"
TAGLINE = "SERVICIOS DIGITALES"
TELEFONO = "+54 11 3784-5392"
WA = "5491137845392"
MENSAJE = "Hola, Gianluca! Me interesa saber mas sobre tus servicios digitales."

SERVICIOS = [
    "Cartel QR: reseñas, WhatsApp, Instagram",
    "Perfil de Google Maps más llamativo",
    "Menú / catálogo digital con QR",
    "Mini web de presentación sobre tu comercio",
    "Bot de WhatsApp para respuestas automáticas",
    "Turnos y reservas online",
]

NAVY = HexColor("#141A33")
NAVY2 = HexColor("#1D2547")
ORANGE = HexColor("#FF6B35")
LIGHT = HexColor("#F6F6F9")
WHITE = HexColor("#FFFFFF")
INK = HexColor("#1B1F2E")
MUTED = HexColor("#5C6273")
MUTED_L = HexColor("#B9BED0")

F = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Sans", F + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansB", F + "LiberationSans-Bold.ttf"))

W, H = 90 * mm, 55 * mm


def y(bottom, size):
    """Línea base en coordenadas de reportlab, a partir de la medición del PDF original."""
    return H - bottom + 0.212 * size


def qr_image():
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data("https://wa.me/" + WA + "?text=" + MENSAJE.replace(" ", "%20")
               .replace(",", "%2C").replace("!", "%21"))
    q.make(fit=True)
    img = q.make_image(fill_color="#141A33", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def frente(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY2)
    c.circle(266.5, H - 17.0, 73.7, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.circle(229.6, H - 136.05, 34.0, stroke=0, fill=1)

    c.setFillColor(ORANGE)
    c.setFont("SansB", 5.6)
    c.drawString(19.8, y(26.7, 5.6), TAGLINE)

    c.setFillColor(WHITE)
    c.setFont("SansB", 16)
    c.drawString(19.8, y(50.1, 16), NOMBRE)

    c.setFont("SansB", 7.8)
    c.drawString(19.8, y(69.7, 7.8), "Más clientes te encuentran.")
    c.drawString(19.8, y(81.0, 7.8), "Más clientes te eligen.")

    c.setFillColor(MUTED_L)
    c.setFont("Sans", 5.8)
    c.drawString(19.8, y(97.6, 5.8), "Servicios digitales simples para hacer crecer")
    c.drawString(19.8, y(106.7, 5.8), "a tu negocio desde hoy.")

    c.setFillColor(ORANGE)
    c.circle(25.5, H - 128.95, 6.2, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("SansB", 4.5)
    c.drawCentredString(25.5, y(132.5, 4.5), "WA")
    c.setFont("SansB", 9)
    c.drawString(38.3, y(134.3, 9), TELEFONO)


def dorso(c, qr):
    c.setFillColor(LIGHT)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(0, 0, 6.2, H, stroke=0, fill=1)

    c.setFillColor(INK)
    c.setFont("SansB", 7.8)
    c.drawString(22.7, y(25.7, 7.8), "Haz crecer a tu negocio")
    c.drawString(22.7, y(36.5, 7.8), "con estos servicios")

    bases = [53.8, 67.9, 82.1, 96.3, 110.5, 124.6]
    puntos = [49.9, 64.05, 78.25, 92.4, 106.6, 120.75]
    for texto, base, punto in zip(SERVICIOS, bases, puntos):
        c.setFillColor(ORANGE)
        c.circle(26.1, H - punto, 2.0, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Sans", 6.3)
        c.drawString(32.6, y(base, 6.3), texto)

    c.setFillColor(WHITE)
    c.roundRect(172.9, H - 85.0, 68.0, 68.0, 6, stroke=0, fill=1)
    c.drawImage(qr, 178.6, H - 79.4, 56.7, 56.7)

    c.setFillColor(MUTED)
    c.setFont("SansB", 5.6)
    c.drawCentredString(206.9, y(95.3, 5.6), "Escaneá y escribime")
    c.setFont("Sans", 5.2)
    c.drawCentredString(206.9, y(104.3, 5.2), "por WhatsApp")

    c.setFont("Sans", 5.6)
    c.drawString(22.7, y(141.5, 5.6),
                 "Elegí los que más se amolden a tus necesidades y comencemos hoy.")


def main(salida):
    qr = qr_image()
    c = canvas.Canvas(str(salida), pagesize=(W, H))
    frente(c)
    c.showPage()
    dorso(c, qr)
    c.showPage()
    c.save()
    print(salida)
    png(salida)


def png(pdf, dpi=300):
    """Exporta cada cara a PNG (para mandar por WhatsApp)."""
    import subprocess
    base = pdf.with_suffix("")
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(base)], check=True)
    for n, cara in ((1, "frente"), (2, "dorso")):
        viejo = Path(f"{base}-{n}.png")
        if viejo.exists():
            nuevo = base.parent / f"{base.name}-{cara}.png"
            viejo.replace(nuevo)
            print(nuevo)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "Gianluca_Salvatori_-_Servicios_digitales.pdf"))
