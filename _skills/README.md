# Skills

Copia de referencia de las skills de Claude que producen cada servicio. La versión que se
ejecuta es la instalada en Claude; esta carpeta es el archivo y el punto de partida para
actualizarlas (editar acá, empaquetar el `.skill` y reinstalarlo).

| Skill | Servicio | Plantilla que consume |
|---|---|---|
| `cartel-qr` | Kit QR y página de links | `_plantillas/qr-links.md` |
| `catalogo-digital` | Menú o catálogo digital | `_plantillas/menu-digital.md` / `_plantillas/catalogo.md` |
| `mini-web` | Mini web de presentación | `_plantillas/mini-web.md` |
| `perfil-google` | Perfil de Google Maps | `_plantillas/perfil-google.md` |
| `turnos-online` | Turnos y reservas | `_plantillas/turnos.md` |

Todas arrancan por el mismo paso 0: leer el alta del cliente (`<slug>/alta-<servicio>.md`),
que es la plantilla completada. Nada se inventa ni se vuelve a preguntar.
