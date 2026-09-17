#!/usr/bin/env python3
"""
Auditoría de un Perfil de Empresa en Google (Google Maps). Recibe lo relevado en un JSON
y devuelve puntaje, faltantes ordenados por impacto y el informe en Markdown.

Uso:
  python3 auditoria_gbp.py relevamiento.json [informe.md]

relevamiento.json (todo opcional; lo que no se releva cuenta como faltante):
{
  "nombre": "Bar Central", "rubro": "Cafetería",
  "verificado": true,
  "nombre_limpio": true,              # sin keywords, ciudad ni slogans agregados
  "categoria_principal": "Cafetería",
  "categorias_secundarias": ["Pastelería", "Bar de desayunos"],
  "direccion_ok": true,               # o "area_servicio": true para negocios sin local
  "telefono": true, "web": true,
  "horarios": true, "horarios_especiales": true,
  "descripcion_chars": 620,
  "logo": true, "portada": true,
  "fotos_exterior": 3, "fotos_interior": 6, "fotos_productos": 12, "fotos_equipo": 0,
  "fotos_total": 24, "fotos_ultimo_mes": 2,
  "servicios_o_productos": 14,        # ítems cargados en Servicios / Productos / Menú
  "atributos": 6,
  "resenas_total": 48, "resenas_promedio": 4.6, "resenas_respondidas_pct": 40,
  "resenas_ultimos_90d": 5,
  "publicaciones_ultimos_30d": 0,
  "preguntas_respondidas": 2,
  "enlaces_accion": ["reservas"],     # reservas, pedidos, menu, citas, whatsapp
  "redes": ["instagram"],
  "mensajes_activados": false
}
"""
import json
import sys
from pathlib import Path


def evaluar(d):
    g = d.get
    checks = []

    def c(bloque, nombre, puntos, ok, accion, parcial=None):
        checks.append({"bloque": bloque, "nombre": nombre, "max": puntos,
                       "obt": puntos if ok else (parcial or 0), "accion": accion})

    # Base (28)
    c("Base", "Perfil verificado", 5, g("verificado"), "Verificar el perfil (video es lo habitual: cartel, interior y gestión en vivo).")
    c("Base", "Nombre real, sin keywords", 3, g("nombre_limpio"), "Dejar solo el nombre del comercio: sin ciudad, rubro ni frases agregadas (Google puede suspender).")
    c("Base", "Categoría principal correcta", 5, bool(g("categoria_principal")), "Elegir la categoría más específica que describa el negocio (es el factor que más pesa).")
    sec = len(g("categorias_secundarias") or [])
    c("Base", "Categorías secundarias (2 a 5)", 3, sec >= 2, "Agregar 2 a 5 categorías secundarias que también apliquen (máximo 9).", parcial=1 if sec == 1 else 0)
    c("Base", "Dirección o área de servicio", 4, g("direccion_ok") or g("area_servicio"), "Cargar la dirección exacta con el pin bien ubicado, o el área de servicio si atiende a domicilio.")
    c("Base", "Teléfono", 2, g("telefono"), "Cargar un teléfono que atienda (puede ser el celular con WhatsApp).")
    c("Base", "Sitio web o página de links", 3, g("web"), "Cargar la mini web o la página de links como sitio web.")
    c("Base", "Horarios completos", 3, g("horarios"), "Cargar horario de cada día, incluidos los días cerrado.")
    # Descripción (8)
    dc = g("descripcion_chars") or 0
    c("Descripción", "Descripción de 500 a 750 caracteres", 8, dc >= 500, "Redactar descripción (máx. 750): qué ofrece, para quién, zona, qué lo diferencia. Sin links ni promos.", parcial=4 if 150 <= dc < 500 else 0)
    # Fotos (20)
    c("Fotos", "Logo", 3, g("logo"), "Subir logo cuadrado (mín. 250x250, legible chico).")
    c("Fotos", "Foto de portada", 3, g("portada"), "Subir portada horizontal 16:9 (mín. 1080x608) que muestre el local o el producto estrella.")
    ext, inte, prod = g("fotos_exterior") or 0, g("fotos_interior") or 0, g("fotos_productos") or 0
    c("Fotos", "Exterior (mín. 3)", 3, ext >= 3, "Sacar 3 a 5 fotos de la fachada de día, con el cartel visible, desde la vereda.", parcial=1 if ext else 0)
    c("Fotos", "Interior (mín. 5)", 3, inte >= 5, "Sacar 5 fotos del interior con luz natural, ordenado y con gente si se puede.", parcial=1 if inte else 0)
    c("Fotos", "Productos / servicios (mín. 8)", 4, prod >= 8, "Subir 8 o más fotos de productos, platos o trabajos realizados.", parcial=2 if prod >= 3 else 0)
    c("Fotos", "Equipo", 2, (g("fotos_equipo") or 0) >= 1, "Subir 1 o 2 fotos del equipo atendiendo (genera confianza).")
    c("Fotos", "Total 20 o más", 1, (g("fotos_total") or 0) >= 20, "Llegar a 20-30 fotos en total.")
    c("Fotos", "Fotos nuevas en el último mes", 1, (g("fotos_ultimo_mes") or 0) >= 2, "Rutina: 2 a 4 fotos nuevas por mes.")
    # Contenido (14)
    sp = g("servicios_o_productos") or 0
    c("Contenido", "Servicios / productos / menú cargados", 8, sp >= 8, "Cargar cada servicio o producto con nombre, precio y descripción corta (o el menú completo).", parcial=4 if sp >= 3 else 0)
    c("Contenido", "Atributos", 3, (g("atributos") or 0) >= 4, "Marcar atributos reales: accesibilidad, medios de pago, wifi, pet friendly, delivery, etc.", parcial=1 if g("atributos") else 0)
    c("Contenido", "Horarios especiales (feriados)", 3, g("horarios_especiales"), "Cargar feriados y vacaciones (evita el cartel 'puede estar cerrado').")
    # Reseñas (14)
    rt, rp = g("resenas_total") or 0, g("resenas_promedio") or 0
    c("Reseñas", "10 o más reseñas", 4, rt >= 10, "Pedir reseñas con el cartel QR a los clientes que se van contentos.", parcial=2 if rt >= 3 else 0)
    c("Reseñas", "Promedio 4,3 o más", 2, rp >= 4.3, "Atender lo que se repite en las reseñas malas; el promedio sube con volumen nuevo.")
    c("Reseñas", "80 % o más respondidas", 5, (g("resenas_respondidas_pct") or 0) >= 80, "Responder todas las reseñas (buenas y malas), en menos de 48 h, con nombre y sin plantillas idénticas.", parcial=2 if (g("resenas_respondidas_pct") or 0) >= 40 else 0)
    c("Reseñas", "Reseñas recientes (últimos 90 días)", 3, (g("resenas_ultimos_90d") or 0) >= 3, "Sostener 1 o más reseñas nuevas por semana.", parcial=1 if g("resenas_ultimos_90d") else 0)
    # Actividad (12)
    c("Actividad", "Publicación en los últimos 30 días", 5, (g("publicaciones_ultimos_30d") or 0) >= 1, "Publicar novedades, ofertas o eventos cada 1 o 2 semanas (150-300 caracteres, con foto).")
    c("Actividad", "Preguntas y respuestas cargadas", 4, (g("preguntas_respondidas") or 0) >= 5, "Cargar 5 a 10 preguntas frecuentes con su respuesta desde la cuenta del dueño.", parcial=2 if g("preguntas_respondidas") else 0)
    c("Actividad", "Enlaces de acción (reservas, pedidos, menú, citas)", 3, len(g("enlaces_accion") or []) >= 1, "Agregar los enlaces de acción que apliquen: menú, pedidos, reservas o turnos (puede ser WhatsApp).")
    # Contacto (4)
    c("Contacto", "Redes sociales vinculadas", 2, len(g("redes") or []) >= 1, "Vincular Instagram, Facebook, TikTok o YouTube desde el perfil.")
    c("Contacto", "Mensajes / WhatsApp activo", 2, g("mensajes_activados"), "Activar mensajes o vincular WhatsApp (solo si van a responder en el día).")

    total = sum(x["obt"] for x in checks)
    maximo = sum(x["max"] for x in checks)
    return checks, total, maximo


def nivel(p):
    if p >= 85: return "Completo"
    if p >= 65: return "Bueno, con mejoras"
    if p >= 40: return "Incompleto"
    return "Básico o abandonado"


def informe(d, checks, total, maximo):
    faltan = sorted([x for x in checks if x["obt"] < x["max"]], key=lambda x: -(x["max"] - x["obt"]))
    bloques = {}
    for x in checks:
        b = bloques.setdefault(x["bloque"], [0, 0])
        b[0] += x["obt"]; b[1] += x["max"]
    out = [f"# Auditoría del perfil de Google: {d.get('nombre', '')}", "",
           f"**Puntaje: {total}/{maximo} · {nivel(total)}**", "", "| Bloque | Puntos |", "|---|---|"]
    out += [f"| {k} | {v[0]}/{v[1]} |" for k, v in bloques.items()]
    out += ["", "## Qué ajustar, por impacto", ""]
    out += [f"{i}. **{x['nombre']}** (+{x['max'] - x['obt']}): {x['accion']}" for i, x in enumerate(faltan, 1)]
    out += ["", "## Lo que ya está bien", ""]
    out += [f"- {x['nombre']}" for x in checks if x["obt"] == x["max"]]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: auditoria_gbp.py relevamiento.json [informe.md]")
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    checks, total, maximo = evaluar(d)
    md = informe(d, checks, total, maximo)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("auditoria.md")
    out.write_text(md, encoding="utf-8")
    print(f"{total}/{maximo} · {nivel(total)} → {out}")
