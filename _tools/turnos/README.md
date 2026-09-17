# Turnos online: instalación por cliente

Dos piezas: la **página de reservas** (estática, en este repo, `<slug>/turnos/`) y el
**backend** en Google Apps Script, que vive en la cuenta de Google del dueño (o de Gian
para la demo). El backend usa una planilla como base de datos, el calendario del dueño como
agenda y Gmail para los mails. Costo: cero. Límite: ~100 mails por día por cuenta.

## A. Backend (5 minutos, con la cuenta de Google del dueño)

1. Entrar a https://script.google.com → **Nuevo proyecto**. Ponerle nombre `Turnos <negocio>`.
2. Borrar el contenido de `Código.gs`, pegar el de `Code.gs` y cambiar `NEGOCIO_DEFAULT`
   por el nombre del negocio. Guardar (Ctrl+S).
3. Arriba, elegir la función **`setup`** y tocar **Ejecutar**. Va a pedir permisos:
   *Revisar permisos → elegir la cuenta → Configuración avanzada → Ir a Turnos (no seguro) → Permitir*.
   (El aviso "no seguro" aparece porque es un script propio, no publicado en la tienda.)
   Al terminar, en **Registro de ejecución** aparece la URL de la planilla creada.
4. **Implementar → Nueva implementación** → engranaje → **Aplicación web**:
   - Descripción: `v1`
   - Ejecutar como: **Yo**
   - Quién tiene acceso: **Cualquier usuario**
   → Implementar → copiar la **URL de la aplicación web** (termina en `/exec`).
5. En la planilla, pestaña **Config**, ajustar: `calendario` (`primary` = calendario principal de esa
   cuenta; o el ID de otro calendario, que se ve en Configuración del calendario → "ID del calendario",
   por ejemplo uno compartido con el equipo), `email_dueno`, `whatsapp` (549...),
   `direccion`, horarios (`horario_lun_vie`, `horario_sab`, `horario_dom`; se puede agregar
   una fila `horario_mar` etc. para un día puntual), `capacidad` (turnos simultáneos),
   `intervalo_min`, `anticipacion_min_horas`, `anticipacion_max_dias`, `hora_recordatorio`.
   Pestaña **Servicios**: uno por fila (id sin espacios, nombre, duración, descripción, activo).
   Pestaña **Bloqueos**: feriados o franjas sin atención (fecha, desde, hasta; vacíos = todo el día).

Si después se cambia el código: **Implementar → Administrar implementaciones → lápiz →
Versión: Nueva versión → Implementar**. La URL no cambia.

## B. Página de reservas

1. Copiar `cliente-demo/turnos/config.json` a `<slug>/turnos/config.json` y completar:
   `api_url` (la URL `/exec` del paso A.4), `whatsapp`, `direccion`, `volver` (página de
   links del cliente), `horarios`, `intervalo_min` y `servicios` **iguales a la planilla**,
   `campos_extra` (ej. cantidad de personas, patente, obra social) y `notas`.
   Con `api_url` vacío la página corre en modo demo (simula turnos, no manda mails).
2. `python3 _tools/pagina_turnos.py <slug>/turnos/config.json <slug>/turnos/index.html`
3. Publicar en GitHub Pages (flujo habitual: zip → `_upload.zip` → push desde la PC).
4. Agregar el botón en la página de links: `{"tipo": "reservas", "label": "Reservas",
   "sub": "Guardá tu lugar", "url": ".../<slug>/turnos/"}` y regenerar con `--standalone`.

## Adaptar al rubro

Todo se configura en la planilla, sin tocar código:
- **Gastronomía**: servicios = tipos de mesa o eventos, `capacidad` = cantidad de mesas de ese tipo,
  duración 90-120 min, `intervalo_min` 30, campo extra "¿Cuántos son?".
- **Peluquería / estética / barbería**: servicios = corte, color, barba... con su duración real,
  `capacidad` = cantidad de sillas o profesionales, `intervalo_min` 15 o 30.
- **Psicología / consultorio / nutrición**: un servicio "Consulta" de 50-60 min, `capacidad` 1,
  `anticipacion_min_horas` 24, campo extra "Obra social" o "Motivo de consulta", sin WhatsApp de
  confirmación si prefieren discreción (dejar `whatsapp` vacío en el config de la página).
- **Taller / gomería / lavadero**: servicio por tipo de trabajo, campo extra "Patente" o "Modelo".
- **Clases / gimnasio**: servicio = clase, `capacidad` = cupo, horarios fijos con `intervalo_min` = duración.
- **Profesional que atiende algunos días**: filas `horario_lun`, `horario_mar`... en Config (pisan a `horario_lun_vie`).

## C. Probar

1. Abrir `.../<slug>/turnos/`, reservar con un mail propio.
2. Verificar: fila nueva en la pestaña **Turnos**, evento en el calendario del dueño, mail de
   confirmación (con `reserva.ics` y botón de WhatsApp) y mail "[Turnos] Nuevo turno" al dueño.
3. Tocar "Cancelá tu reserva" en el mail: la fila pasa a `cancelado`, el evento se borra.
4. El recordatorio sale a la `hora_recordatorio` del día anterior (disparador cada hora);
   la agenda del día llega a las 8. Para probar sin esperar: ejecutar `enviarRecordatorios`
   a mano con un turno cargado para mañana.

## Cosas que ya nos pasaron

- Probar el API con `curl` da una página de error de Google aunque la reserva **sí** se haya creado
  (curl no sigue bien la redirección de Apps Script en POST). Probar siempre desde la página en el navegador.
- Un teléfono con `+` adelante rompía la celda en Sheets (`#ERROR!`): ahora se guarda solo con dígitos y
  la fila se escribe como texto.
- La primera llamada del día al script demora 2-4 s (arranque en frío): la página muestra un esqueleto
  de carga y precarga los días siguientes; no es un error.
- Si "no aparece en el calendario": está en el calendario de la cuenta donde corre el script (la que
  ejecutó `setup`). Revisar que el celular tenga esa cuenta activa, o poner otro ID en `calendario`.

## Qué le queda al dueño

- Ver y editar turnos en la planilla o en Google Calendar (el celular le avisa).
- Cancelar un turno: cambiar `estado` a `cancelado` en la planilla (el mail al cliente en ese
  caso lo manda él por WhatsApp).
- Cerrar un día o una franja: una fila en **Bloqueos**.
- Cambiar horarios o servicios: pestañas **Config** y **Servicios** (avisar a Gian para
  regenerar la página si cambian servicios o intervalos).
