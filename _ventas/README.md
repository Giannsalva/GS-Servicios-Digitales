# Material de venta

Lo que Gian usa para vender: la presentación, la tarjeta y el mensaje de WhatsApp.
Los tres dicen lo mismo — si cambia un servicio, se cambian los tres.

| Pieza | Archivo | Cuándo se usa |
|---|---|---|
| Presentación (10 slides) | `Gianluca_Salvatori_-_Servicios_digitales.pptx` / `.pdf` | Se manda por WhatsApp al que mostró interés. El PDF es el que se manda; el pptx es para editar. |
| Tarjeta 90x55 mm | `tarjeta/Gianluca_Salvatori_-_tarjeta.pdf` (+ PNG de cada cara) | Se imprime y se deja en la visita. El QR del dorso abre un WhatsApp a Gian con el mensaje escrito. |
| Mensaje de respuesta | `mensaje-whatsapp.md` | Se pega cuando alguien escribe por primera vez. |

La tarjeta se regenera con `python3 _tools/tarjeta.py _ventas/tarjeta/Gianluca_Salvatori_-_tarjeta.pdf`
(edita la lista `SERVICIOS` del script, no el PDF). La presentación se edita a mano en PowerPoint.

Todo apunta al cliente demo `https://giannsalva.github.io/GS-Servicios-Digitales/cliente-demo/`,
que es la prueba de que los servicios existen y funcionan: la slide de cierre y el mensaje lo linkean.

Pendiente: la lista de precios definitiva, y decidir el dominio propio antes de imprimir QR de
clientes reales.
