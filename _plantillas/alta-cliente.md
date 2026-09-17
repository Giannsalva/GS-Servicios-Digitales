# Alta de cliente

Copiar este archivo a `<slug>/alta.md` y completarlo en la primera visita (o por WhatsApp).
Todo lo que se carga acá alimenta los cuatro servicios: página de links, catálogo, mini web
y perfil de Google. Lo que no aplique se deja vacío.

Slug (carpeta en el repo, minúsculas, sin espacios ni acentos, **no se cambia nunca**): `__________`

Servicios contratados: [ ] Kit QR / links  [ ] Catálogo  [ ] Mini web  [ ] Perfil de Google  [ ] Turnos  [ ] Bot

---

## 1. Datos base (todos los servicios)

| Campo | Valor |
|---|---|
| Nombre exacto del comercio (como está en el cartel) | |
| Rubro en una frase (ej. "Café de especialidad y pastelería") | |
| Frase corta / slogan (opcional) | |
| Dirección completa (calle, número, localidad) | |
| Link de Google Maps del local | |
| WhatsApp (formato 549 + área + número, sin 15) | |
| Teléfono fijo (opcional) | |
| Email de contacto | |
| Instagram (URL) | |
| Facebook (URL) | |
| TikTok / otra (URL) | |
| Sitio web actual (si tiene) | |
| Nombre y celular del dueño / responsable | |

## 2. Horarios

| Días | Horario |
|---|---|
| Lunes a viernes | |
| Sábados | |
| Domingos | |
| Feriados | |
| Vacaciones / cierres previstos | |

## 3. Identidad visual

| Campo | Valor |
|---|---|
| Color principal (hex, o "el del cartel") | |
| Logo (archivo en `<slug>/fotos/logo.*`) | [ ] tengo  [ ] hay que hacerlo |
| Tono de comunicación | [ ] cercano/tuteo  [ ] formal  [ ] otro: |

Fotos a pedir o sacar (guardar en `<slug>/fotos/`, nombres descriptivos):
- [ ] Fachada de día con el cartel (3)
- [ ] Interior (5)
- [ ] Productos / platos / trabajos (8 o más)
- [ ] Equipo atendiendo (1 o 2)
- [ ] Portada horizontal para la web (1)

## 4. Página de links (Kit QR)

Botones en orden. Tipos: whatsapp, instagram, facebook, google (reseña), maps, web, menu, tel, mail, tiktok.

| # | Tipo | Texto del botón | Subtítulo | URL |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |

Mensaje inicial del WhatsApp (lo que llega escrito al tocar el botón): `__________`

Carteles a imprimir: [ ] links  [ ] reseñas Google  [ ] Instagram  [ ] WhatsApp  [ ] menú

## 5. Catálogo / menú

| Campo | Valor |
|---|---|
| Nombre de la pestaña (Carta, Catálogo, Lista de precios...) | |
| Moneda / texto de precios ("$", "Precios en pesos", "Consultar") | |
| Layout | [ ] lista (bar/restó)  [ ] grilla con fotos (ropa, productos) |
| Buscador | [ ] sí  [ ] no |
| Pedido por WhatsApp | [ ] sí, mensaje: __________  [ ] no |
| Precios editables por el dueño (Google Sheet) | [ ] sí, mail de su cuenta Google: __________  [ ] no |

Categorías e ítems (o adjuntar la carta actual en foto/PDF y se transcribe):

| Categoría | Ítem | Descripción corta | Precio | Etiquetas (Nuevo, Vegano, Sin TACC...) | Variantes |
|---|---|---|---|---|---|
| | | | | | |

## 6. Mini web

| Campo | Valor |
|---|---|
| Descripción "Quiénes somos" (2 o 3 oraciones, el dueño lo cuenta y se redacta) | |
| 2 a 4 destacados (título + una línea) | |
| Botones del hero además de WhatsApp (ej. Ver la carta, Reservar) | |
| Mapa embebido | [ ] sí  [ ] no |

Secciones libres (elegir las que apliquen, en orden). Cada una: título + texto y/o foto, tarjetas, lista o preguntas.

| Orden | Título | Tipo (texto / texto+foto / tarjetas / lista / preguntas) | Contenido o notas |
|---|---|---|---|
| 1 | Nuestra historia | | |
| 2 | Qué ofrecemos / servicios | | |
| 3 | Comodidades (wifi, pet friendly, estacionamiento, acceso...) | | |
| 4 | Preguntas frecuentes | | |
| 5 | | | |

## 7. Perfil de Google Maps

| Campo | Valor |
|---|---|
| ¿Existe perfil? | [ ] sí, verificado  [ ] sí, sin reclamar  [ ] no |
| Cuenta de Google del dueño (para crear / gestionar) | |
| ¿Gian agregado como Administrador? | [ ] sí  [ ] pendiente |
| Categoría principal | |
| Categorías secundarias (2 a 5) | |
| Atributos reales (wifi, tarjeta, QR, delivery, para llevar, accesible, pet friendly, estacionamiento...) | |
| Link de reseñas del perfil | |
| Preguntas frecuentes de los clientes (5 a 10, con la respuesta del dueño) | |

Relevamiento del perfil actual → `<slug>/google/relevamiento.json` (esquema en `_tools/auditoria_gbp.py`).

## 8. Turnos / recordatorios (si aplica)

| Campo | Valor |
|---|---|
| Servicios que se agendan y duración de cada uno | |
| Días y franjas de atención | |
| Cuántos turnos simultáneos | |
| Anticipación mínima / máxima para reservar | |
| Datos a pedir además de nombre, teléfono y mail | |
| Cuenta de Google del dueño (agenda y mails salen de ahí) | |

---

## Qué se genera con esto

| Sección | Archivo | Skill |
|---|---|---|
| 1, 2, 3, 4 | `<slug>/config.json` + `<slug>/carteles/` | `cartel-qr` |
| 1, 3, 5 | `<slug>/carta/config.json` | `catalogo-digital` |
| 1, 2, 3, 6 | `<slug>/web/config.json` | `mini-web` |
| 1, 2, 3, 7 | `<slug>/google/relevamiento.json` + `kit.md` | `perfil-google` |
