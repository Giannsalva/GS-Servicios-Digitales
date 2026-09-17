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

La plantilla completada por el cliente se archiva como `<slug>/alta-<servicio>.md`.
