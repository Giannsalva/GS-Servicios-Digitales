---
name: turnos-online
description: "Sistema de turnos y reservas online para un comercio de cualquier rubro (gastronomía, peluquería, consultorio, taller, clases): página de reservas en GitHub Pages + backend en Google Apps Script con mails de confirmación y recordatorio. Usar cuando Gian pida turnos, reservas, agenda online o recordatorios automáticos para un local."
---

# Turnos y reservas online

Servicio "Recordatorios automáticos / Turnos" del catálogo de Gianluca. El cliente final elige
servicio → día → horario → deja nombre, celular y mail → recibe confirmación por mail (con `.ics`,
botón "Confirmar por WhatsApp" y link de cancelación) y un recordatorio automático el día anterior.
El dueño ve cada turno en su Google Calendar y en una planilla, recibe un mail por turno nuevo o
cancelado y la agenda del día a las 8. Costo cero, sin servidor.

## Paso 0: la plantilla del cliente (siempre)

El servicio **arranca por `_plantillas/turnos.md`**, no por preguntas sueltas. Ese archivo es el
contrato de lo que hace falta para poder trabajar.

1. Si el cliente todavía no la completó: mandarle `_plantillas/docx/plantilla-turnos.docx`.
2. Cuando la devuelve (archivo, foto o audios de WhatsApp), transcribirla y archivarla como
   `<slug>/alta-turnos.md` en el repo. Ese archivo es la fuente de verdad del cliente.
3. **Leer el alta antes de tocar nada** y armar el `config.json` y la planilla desde ahí.
   Nunca inventar horarios, servicios, duraciones ni mails.
4. Lo que quedó vacío se pregunta **una sola vez, todo junto**, y se completa en el mismo
   `alta-turnos.md`. Lo que sigue faltando se marca `PENDIENTE` y no se publica nada que dependa
   de un dato pendiente (sobre todo horarios y duraciones: un horario mal cargado le hace perder
   plata al cliente).
5. Si el cliente ya tiene otro servicio contratado, los datos del comercio se copian de su alta
   anterior en vez de volver a pedirlos.

Mapeo del alta al sistema:

| Bloque de la plantilla | Dónde va |
|---|---|
| Datos del comercio, color, dirección, WhatsApp | `config.json` de la página (`nombre`, `accent`, `direccion`, `whatsapp`) + hoja Config |
| Cuenta de Google, mail de avisos, resumen diario, calendario aparte | hoja Config (`email_dueno`, `agenda_diaria`, `calendario`); el `setup()` se corre en esa cuenta |
| Qué se reserva (servicios, duración, descripción) | hoja Servicios + `servicios` del `config.json` (tienen que coincidir) |
| Cuándo (horarios, feriados, intervalo, capacidad, anticipación) | hoja Config + hoja Bloqueos + `horarios`, `intervalo_min`, `dias_adelante` |
| Cancelaciones | `cancelacion_horas` en Config y el texto del mail |
| Datos extra a pedir | `campos_extra` del `config.json` (se guardan como columnas en Turnos) |
| Textos | `titulo`, `detalle`, `notas` |
| "Lo que necesito de tu lado" | agenda de la sesión de 10 minutos con el dueño |

## Piezas (todo en el repo público `Giannsalva/GS-Servicios-Digitales`)

| Pieza | Dónde | Qué es |
|---|---|---|
| Backend | `_tools/turnos/Code.gs` | Apps Script: planilla (Config, Servicios, Bloqueos, Turnos) + Calendar + Gmail. Web app con `doGet` (disponibilidad, cancelar, servicios) y `doPost` (reservar). Disparadores: `enviarRecordatorios` cada hora, `agendaDelDia` a las 8. |
| Guía de instalación | `_tools/turnos/README.md` | Pasos exactos para desplegar, adaptar al rubro, probar y errores conocidos. **Leerla siempre.** |
| Generador de página | `_tools/pagina_turnos.py` | `config.json` → `index.html` autocontenido (Manrope/Fraunces, claro/oscuro, 4 pasos, validaciones, modo demo si `api_url` vacío). |
| Demo | `cliente-demo/turnos/` | Bar Central, conectado al script de la cuenta de Gian. |
| Plantilla para el cliente | `_plantillas/turnos.md` (+ `docx/plantilla-turnos.docx`) | Lo que hay que pedirle al comercio. Se regenera el docx con `_tools/plantillas_docx.py`. |

En una sesión nueva, traer el código con `curl -sL https://raw.githubusercontent.com/Giannsalva/GS-Servicios-Digitales/main/<ruta>`
(o desde la carpeta local `$HOME/mnt/GS-Servicios-Digitales` vía `device_bash`). No reescribirlo de memoria.

## Convenciones fijas

- URL de la página: `https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/turnos/` (nunca renombrar).
- El backend corre en la **cuenta de Google del dueño** (planilla, calendario y mails son suyos). La cuenta de Gian solo para la demo.
- La página necesita `servicios`, `horarios` e `intervalo_min` **iguales** a la planilla (dibuja el calendario con eso; la disponibilidad real siempre la da el API).
- Botón en la página de links del cliente: `{"tipo": "reservas", "label": "Reservas", "sub": "Guardá tu lugar", "url": ".../<slug>/turnos/"}`, **último de la lista**.
- Validaciones en página y servidor: nombre y apellido (2+ palabras), celular 8-15 dígitos (se guarda solo dígitos; un `+` inicial rompe Sheets), email válido, obligatorios salvo notas. Honeypot `hp` antispam. `LockService` evita dobles reservas.
- Carga de horarios: la página muestra esqueleto mientras responde el API y **precarga los días siguientes**, para que al tocar un día no parpadee ni se pisen dos respuestas (se descarta la respuesta vieja si el usuario ya cambió de día).

## Mails (los tres salen del mismo `Code.gs`)

| Mail | A quién | Cuándo |
|---|---|---|
| Confirmación | al cliente | al reservar; lleva `.ics`, "Confirmar por WhatsApp" y link de cancelación |
| Recordatorio | al cliente | el día anterior, a la hora que pidió el dueño |
| Aviso de turno | al dueño | por cada turno nuevo o cancelado, con los datos y "Escribirle por WhatsApp" |

**Regla de oro del HTML de los mails:** los botones se arman con `boton_(url, texto, color)`, que
devuelve una tabla con `bgcolor` y el texto en blanco forzado (`color:#ffffff !important` + `<span>`).
Gmail —sobre todo en modo oscuro en el celular— reescribe los fondos de un `<a style="background:...">`
y el botón queda gris ilegible. **No volver a usar `btn_()` para un botón visible.** Además:

- Fondo de la tarjeta en `#FFFFFF` y color de texto explícito en cada bloque (Gmail invierte los grises).
- Debajo de cada botón, el link en texto plano (`wa.me/…`) como respaldo.
- "Ver planilla" es un link chico de texto, no un botón.
- Para probar el diseño sin re-desplegar: renderizar el HTML con `node` + Playwright, y mandarse el
  mismo HTML por Gmail a la cuenta de Gian para verlo en el celular.

## Flujo por cliente

1. **Alta**: leer `<slug>/alta-turnos.md` (paso 0).
2. **Backend** (con el dueño, 10 min, según `_tools/turnos/README.md` sección A): pegar `Code.gs` en script.google.com, cambiar `NEGOCIO_DEFAULT`, ejecutar `setup()`, implementar como web app (Ejecutar como *Yo*, acceso *Cualquier usuario*), copiar la URL `/exec`. Completar Config, Servicios y Bloqueos en la planilla.
3. **Página**: copiar `cliente-demo/turnos/config.json` a `<slug>/turnos/config.json`, cargar `api_url`, `whatsapp` (vacío si el rubro prefiere discreción), `direccion`, `volver`, `horarios`, `intervalo_min`, `servicios`, `campos_extra` (`{"id","label","tipo","req"}`), `titulo`, `detalle`, `accent`. Generar: `python3 _tools/pagina_turnos.py <slug>/turnos/config.json <slug>/turnos/index.html`. Revisar con Playwright a 390 px.
4. **Links + cartel**: agregar el botón Reservas (último) y regenerar la página de links (`--standalone`); cartel QR opcional con la skill `cartel-qr`.
5. **Publicar**: flujo habitual (zip → `_upload.zip` → `device_bash` clona en `/tmp/gs` con el token que pega Gian → commit → push; `git remote set-url` sin token; copiar a la carpeta local; `: > _upload.zip`). Actualizar tabla del `README.md`.
6. **Probar** desde el navegador (no con curl: la redirección de Apps Script engaña): reservar con un mail propio, verificar fila en Turnos, evento en el calendario, los tres mails (mirando uno en Gmail, no solo en Outlook), y cancelar por el link. Borrar las pruebas poniendo `estado = cancelado`.
7. **Entregar** al dueño: link de la página, link de la planilla, y la guía "Qué le queda al dueño" del README (bloquear días, cambiar horarios, cancelar). Si cambia servicios o intervalos, hay que regenerar la página.

## Adaptar al rubro (todo en la planilla, sin código)

- Gastronomía: servicios = tipos de mesa/eventos, `capacidad` = mesas, 90-120 min, extra "¿Cuántos son?".
- Peluquería / estética: corte, color, barba con duración real; `capacidad` = sillas; intervalo 15-30.
- Psicología / consultorio: "Consulta" 50-60 min, `capacidad` 1, `anticipacion_min_horas` 24, extra "Obra social", sin WhatsApp.
- Taller / gomería: por tipo de trabajo, extra "Patente" o "Modelo".
- Clases / gimnasio: servicio = clase, `capacidad` = cupo, `intervalo_min` = duración.
- Días distintos: filas `horario_lun`, `horario_mar`... en Config pisan a `horario_lun_vie`. Feriados en Bloqueos.
- Otro calendario (compartido con el equipo): clave `calendario` en Config con el ID del calendario.

## Errores conocidos

- Cambios en `Code.gs` requieren *Implementar → Administrar implementaciones → Nueva versión* (la URL no cambia).
- Botones de mail grises: es Gmail reescribiendo el fondo. Solución arriba; no es un problema del color elegido.
- Primera llamada del día tarda 2-4 s (arranque en frío): la página muestra esqueleto y precarga los días siguientes.
- "No lo veo en el calendario": está en la cuenta que ejecutó `setup()`; revisar qué cuenta tiene el celular.
- Límite de ~100 mails/día por cuenta Gmail común: sobra para un local; avisar si el volumen es mayor.

## Esquema de `config.json` de la página

```json
{
  "nombre": "Bar Central",
  "titulo": "Reservá tu lugar",
  "detalle": "Elegí qué querés reservar, el día y el horario. Te llega la confirmación por mail.",
  "accent": "#C8552B",
  "api_url": "https://script.google.com/macros/s/.../exec",
  "whatsapp": "5491137845392",
  "direccion": "San Martín 1234, Godoy Cruz, Mendoza",
  "volver": "https://giannsalva.github.io/GS-Servicios-Digitales/<slug>/",
  "dias_adelante": 30,
  "intervalo_min": 30,
  "horarios": {"lun_vie": "09:00-13:00, 16:00-20:00", "sab": "09:00-14:00", "dom": ""},
  "servicios": [{"id": "mesa2", "nombre": "Mesa para 2", "duracion": 90, "descripcion": "Reserva de mesa para dos"}],
  "campos_extra": [{"id": "personas", "label": "¿Cuántos son?", "tipo": "number", "req": false}],
  "notas": true
}
```

## API del backend

- `GET ?action=servicios` → `{servicios, config}`
- `GET ?action=disponibilidad&fecha=YYYY-MM-DD&servicio=<id>` → `{fecha, slots:["09:00",...], cerrado?}`
- `GET ?action=cancelar&id=..&token=..` → página HTML de confirmación
- `POST` (Content-Type `text/plain`) `{servicio, fecha, hora, nombre, telefono, email, notas, hp}` → `{ok,id,fecha,hora,servicio}` o `{error}`
