# Plantillas por servicio

Una plantilla por servicio. Cuando un cliente pide algo, se le manda **solo la que corresponde**
(por WhatsApp, como archivo o foto); cada una es autocontenida y arranca con los datos básicos del comercio.

| Servicio | Plantilla | Se guarda en | Skill |
|---|---|---|---|
| Kit QR y página de links | `qr-links.md` | `<slug>/config.json` + `carteles/` | `cartel-qr` |
| Menú digital (gastronomía) | `menu-digital.md` | `<slug>/carta/` | `catalogo-digital` |
| Catálogo (productos / servicios) | `catalogo.md` | `<slug>/carta/` | `catalogo-digital` |
| Mini web | `mini-web.md` | `<slug>/web/` | `mini-web` |
| Perfil de Google Maps | `perfil-google.md` | `<slug>/google/` | `perfil-google` |
| Turnos y reservas | `turnos.md` | `<slug>/turnos/` | `turnos-online` |

Cada plantilla tiene la misma estructura: **datos del comercio** (iguales en todas, se copian entre
servicios sin volver a preguntar), **preguntas propias del servicio**, y al final **"Lo que necesito
de tu lado"**, que es lo que hace falta para poder trabajar: accesos, materiales, tiempo del dueño
y plazos. Ese último bloque es el que evita la mitad de las idas y vueltas.

## Cómo se usa

1. El cliente pide un servicio → se le manda la plantilla de ese servicio (el `.docx` de `docx/`
   es el que se manda; el `.md` es la fuente).
2. El cliente la devuelve completa (archivo, foto o respondida por WhatsApp).
3. La versión completada se archiva en el repo como `<slug>/alta-<servicio>.md`
   (por ejemplo `bar-central/alta-turnos.md`), transcribiendo lo que haya venido por foto o audio.
4. La skill del servicio **arranca leyendo ese archivo** y de ahí saca todo: nunca se inventan
   datos ni se vuelve a preguntar algo que ya está respondido. Lo que quedó vacío se pregunta
   una sola vez, junto, y se completa en el mismo archivo.
5. Si el cliente contrata un segundo servicio, se le manda solo la plantilla nueva: los datos del
   comercio se copian del alta anterior.

Si no hay plantilla completada (venta en el momento, cliente que dicta todo por WhatsApp), se
igual se arma el `alta-<servicio>.md` con lo que haya, marcando lo que falta como `PENDIENTE`,
y no se publica nada que dependa de un dato pendiente.

## Mantenimiento

Los `.docx` se regeneran desde los `.md` con `python3 _tools/plantillas_docx.py`. Editar siempre
el `.md`, nunca el `.docx` a mano.
