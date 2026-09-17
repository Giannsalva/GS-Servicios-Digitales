/**
 * Turnos online — backend en Google Apps Script.
 * Planilla = base de datos y configuración · Calendario = agenda del dueño · Gmail = mails.
 *
 * Instalación (una vez por cliente, con la cuenta de Google del dueño):
 *  1. script.google.com → Nuevo proyecto → pegar este archivo → guardar.
 *  2. Ejecutar la función setup() (autorizar permisos). Crea la planilla "Turnos - <negocio>"
 *     con las pestañas Config, Servicios, Bloqueos y Turnos, y los disparadores automáticos.
 *  3. Implementar → Nueva implementación → Aplicación web → Ejecutar como "Yo",
 *     acceso "Cualquier usuario" → copiar la URL (termina en /exec) → pegarla en
 *     config.json de la página de turnos ("api_url").
 *  Cada cambio del código requiere: Implementar → Administrar implementaciones → editar → Nueva versión.
 */

var NEGOCIO_DEFAULT = "Bar Central";
var TZ = "America/Argentina/Buenos_Aires";

// ---------- setup ----------

function setup() {
  var props = PropertiesService.getScriptProperties();
  var ss;
  if (props.getProperty("SHEET_ID")) {
    ss = SpreadsheetApp.openById(props.getProperty("SHEET_ID"));
  } else {
    ss = SpreadsheetApp.create("Turnos - " + NEGOCIO_DEFAULT);
    props.setProperty("SHEET_ID", ss.getId());
  }
  var cfg = sheet_(ss, "Config", ["clave", "valor"]);
  if (cfg.getLastRow() < 2) {
    cfg.getRange(2, 1, 13, 2).setValues([
      ["negocio", NEGOCIO_DEFAULT],
      ["email_dueno", Session.getActiveUser().getEmail()],
      ["whatsapp", "5491137845392"],
      ["direccion", "San Martín 1234, Godoy Cruz, Mendoza"],
      ["intervalo_min", 30],
      ["capacidad", 2],
      ["anticipacion_min_horas", 2],
      ["anticipacion_max_dias", 30],
      ["hora_recordatorio", 9],
      ["calendario", "primary"],
      ["horario_lun_vie", "09:00-13:00, 16:00-20:00"],
      ["horario_sab", "09:00-14:00"],
      ["horario_dom", ""]
    ]);
  }
  var srv = sheet_(ss, "Servicios", ["id", "nombre", "duracion_min", "descripcion", "activo"]);
  if (srv.getLastRow() < 2) {
    srv.getRange(2, 1, 3, 5).setValues([
      ["mesa2", "Mesa para 2", 90, "Reserva de mesa para dos personas", "si"],
      ["mesa4", "Mesa para 4", 90, "Reserva de mesa para hasta cuatro personas", "si"],
      ["cumple", "Cumpleaños / grupo", 120, "Grupos de 5 o más, te llamamos para coordinar", "si"]
    ]);
  }
  sheet_(ss, "Bloqueos", ["fecha", "desde", "hasta", "motivo"]);
  sheet_(ss, "Turnos", ["id", "creado", "fecha", "hora", "duracion_min", "servicio", "nombre", "telefono", "email", "notas", "estado", "token", "evento_id", "recordatorio_enviado"]);
  ss.getSheets().forEach(function (s) { if (s.getName() === "Hoja 1" || s.getName() === "Sheet1") ss.deleteSheet(s); });

  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger("enviarRecordatorios").timeBased().everyHours(1).create();
  ScriptApp.newTrigger("agendaDelDia").timeBased().atHour(8).everyDays(1).inTimezone(TZ).create();
  Logger.log("Planilla: " + ss.getUrl());
  return ss.getUrl();
}

function sheet_(ss, name, headers) {
  var s = ss.getSheetByName(name);
  if (!s) {
    s = ss.insertSheet(name);
    s.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight("bold");
    s.setFrozenRows(1);
  }
  return s;
}

// ---------- acceso a datos ----------

function cal_(cfg) {
  var id = cfg && cfg.calendario && String(cfg.calendario).trim();
  if (id && id !== "primary") { var c = CalendarApp.getCalendarById(id); if (c) return c; }
  return CalendarApp.getDefaultCalendar();
}

function ss_() { return SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty("SHEET_ID")); }

function config_() {
  var rows = ss_().getSheetByName("Config").getDataRange().getValues();
  var c = {};
  rows.slice(1).forEach(function (r) { if (r[0]) c[String(r[0]).trim()] = r[1]; });
  c.intervalo_min = Number(c.intervalo_min) || 30;
  c.capacidad = Number(c.capacidad) || 1;
  c.anticipacion_min_horas = Number(c.anticipacion_min_horas) || 0;
  c.anticipacion_max_dias = Number(c.anticipacion_max_dias) || 30;
  return c;
}

function servicios_() {
  var rows = ss_().getSheetByName("Servicios").getDataRange().getValues();
  return rows.slice(1).filter(function (r) { return r[0] && String(r[4]).toLowerCase() !== "no"; })
    .map(function (r) { return { id: String(r[0]), nombre: String(r[1]), duracion: Number(r[2]) || 30, descripcion: String(r[3] || "") }; });
}

function turnosDe_(fecha) {
  var rows = ss_().getSheetByName("Turnos").getDataRange().getValues();
  return rows.slice(1).filter(function (r) { return fmtFecha_(r[2]) === fecha && r[10] === "confirmado"; })
    .map(function (r) { return { hora: fmtHora_(r[3]), dur: Number(r[4]) }; });
}

function bloqueosDe_(fecha) {
  var rows = ss_().getSheetByName("Bloqueos").getDataRange().getValues();
  return rows.slice(1).filter(function (r) { return r[0] && fmtFecha_(r[0]) === fecha; })
    .map(function (r) { return { desde: r[1] ? fmtHora_(r[1]) : "00:00", hasta: r[2] ? fmtHora_(r[2]) : "23:59" }; });
}

// ---------- disponibilidad ----------

function rangosDelDia_(cfg, fecha) {
  var dow = new Date(fecha + "T12:00:00").getDay(); // 0 dom
  var key = dow === 0 ? "horario_dom" : dow === 6 ? "horario_sab" : "horario_lun_vie";
  var dias = ["dom", "lun", "mar", "mie", "jue", "vie", "sab"];
  if (cfg["horario_" + dias[dow]] !== undefined && cfg["horario_" + dias[dow]] !== "") key = "horario_" + dias[dow];
  var txt = String(cfg[key] || "").trim();
  if (!txt) return [];
  return txt.split(",").map(function (p) {
    var m = p.trim().split("-");
    return [min_(m[0]), min_(m[1])];
  }).filter(function (r) { return r[0] < r[1]; });
}

function disponibilidad(fecha, servicioId) {
  var cfg = config_();
  var srv = servicios_().filter(function (s) { return s.id === servicioId; })[0];
  if (!srv) return { error: "Servicio inválido" };
  var rangos = rangosDelDia_(cfg, fecha);
  if (!rangos.length) return { fecha: fecha, slots: [], cerrado: true };
  var ocupados = turnosDe_(fecha);
  var bloqueos = bloqueosDe_(fecha);
  var ahora = new Date();
  var minInicio = new Date(ahora.getTime() + cfg.anticipacion_min_horas * 3600000);
  var slots = [];
  rangos.forEach(function (r) {
    for (var t = r[0]; t + srv.duracion <= r[1]; t += cfg.intervalo_min) {
      var ini = new Date(fecha + "T" + hhmm_(t) + ":00" + offset_());
      if (ini < minInicio) continue;
      var fin = t + srv.duracion;
      var bloqueado = bloqueos.some(function (b) { return t < min_(b.hasta) && fin > min_(b.desde); });
      if (bloqueado) continue;
      var solapados = ocupados.filter(function (o) { var os = min_(o.hora); return t < os + o.dur && fin > os; }).length;
      if (solapados < cfg.capacidad) slots.push(hhmm_(t));
    }
  });
  return { fecha: fecha, slots: slots };
}

// ---------- reserva ----------

function validar_(p) {
  var nombre = String(p.nombre || "").trim().replace(/\s+/g, " ");
  if (!/^[A-Za-zÀ-ÿ'´.-]{2,}( [A-Za-zÀ-ÿ'´.-]{2,})+$/.test(nombre)) return "Ingresá nombre y apellido";
  var tel = String(p.telefono || "").replace(/\D/g, "");
  if (!/^\d{8,15}$/.test(tel)) return "Ingresá un celular válido (solo números, con código de área)";
  if (!/^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/.test(String(p.email || "").trim())) return "Ingresá un email válido";
  p.nombre = nombre; p.telefono = tel; p.email = String(p.email).trim().toLowerCase();
  return "";
}

function reservar(p) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    if (p.hp) return { ok: true }; // honeypot: bots
    var cfg = config_();
    var srv = servicios_().filter(function (s) { return s.id === p.servicio; })[0];
    if (!srv) return { error: "Servicio inválido" };
    var v = validar_(p); if (v) return { error: v };
    if (!/^\d{4}-\d{2}-\d{2}$/.test(p.fecha) || !/^\d{2}:\d{2}$/.test(p.hora)) return { error: "Fecha u hora inválida" };
    var maxFecha = new Date(); maxFecha.setDate(maxFecha.getDate() + cfg.anticipacion_max_dias);
    if (new Date(p.fecha + "T12:00:00") > maxFecha) return { error: "Solo se puede reservar hasta " + cfg.anticipacion_max_dias + " días adelante" };
    var disp = disponibilidad(p.fecha, p.servicio);
    if (disp.slots.indexOf(p.hora) < 0) return { error: "Ese horario ya no está disponible, elegí otro" };

    var id = Utilities.getUuid().slice(0, 8).toUpperCase();
    var token = Utilities.getUuid().replace(/-/g, "");
    var ini = new Date(p.fecha + "T" + p.hora + ":00" + offset_());
    var fin = new Date(ini.getTime() + srv.duracion * 60000);
    var ev = cal_(cfg).createEvent(srv.nombre + " · " + p.nombre, ini, fin, {
      description: "Turno " + id + "\nTel: " + p.telefono + "\nEmail: " + p.email + (p.notas ? "\nNotas: " + p.notas : ""),
      location: cfg.direccion || ""
    });
    var sh = ss_().getSheetByName("Turnos");
    var fila = [id, new Date(), p.fecha, p.hora, srv.duracion, srv.nombre, p.nombre, p.telefono, p.email, p.notas || "", "confirmado", token, ev.getId(), ""];
    var rng = sh.getRange(sh.getLastRow() + 1, 1, 1, fila.length);
    rng.setNumberFormat("@"); rng.getCell(1, 2).setNumberFormat("yyyy-mm-dd hh:mm"); rng.setValues([fila]);

    var t = { id: id, token: token, fecha: p.fecha, hora: p.hora, dur: srv.duracion, servicio: srv.nombre, nombre: p.nombre, telefono: p.telefono, email: p.email, notas: p.notas || "" };
    mailConfirmacion_(cfg, t);
    mailDuenoTurno_(cfg, "Nuevo turno", t, "Reservó desde la web. Ya está en tu calendario.");
    return { ok: true, id: id, fecha: p.fecha, hora: p.hora, servicio: srv.nombre };
  } finally {
    lock.releaseLock();
  }
}

function cancelar(id, token) {
  var sh = ss_().getSheetByName("Turnos");
  var rows = sh.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] === id && rows[i][11] === token) {
      if (rows[i][10] === "cancelado") return { ok: true, ya: true };
      sh.getRange(i + 1, 11).setValue("cancelado");
      var cfg = config_();
      try { var ev = cal_(cfg).getEventById(rows[i][12]); if (ev) ev.deleteEvent(); } catch (e) {}
      mailDuenoTurno_(cfg, "Turno cancelado", { id: id, fecha: fmtFecha_(rows[i][2]), hora: fmtHora_(rows[i][3]), dur: rows[i][4], servicio: rows[i][5], nombre: rows[i][6], telefono: rows[i][7], email: rows[i][8], notas: rows[i][9] }, "Canceló desde el link del mail. El horario quedó libre y el evento se borró del calendario.");
      return { ok: true };
    }
  }
  return { error: "Turno no encontrado" };
}

// ---------- mails ----------

function mailConfirmacion_(cfg, t) {
  var url = ScriptApp.getService().getUrl();
  var cancel = url + "?action=cancelar&id=" + t.id + "&token=" + t.token;
  var wa = "https://wa.me/" + cfg.whatsapp + "?text=" + encodeURIComponent("Hola! Confirmo mi turno " + t.id + ": " + t.servicio + ", " + fechaLarga_(t.fecha) + " a las " + t.hora + ". " + t.nombre);
  var html = plantilla_(cfg, "Tu reserva está confirmada",
    "<p>Hola " + esc_(t.nombre.split(" ")[0]) + ", te esperamos.</p>" + tarjeta_(cfg, t) +
    "<div style='margin:20px 0 8px'>" + boton_(wa, "Confirmar por WhatsApp", "#25D366") + "</div>" +
    "<p style='color:#6B645D;font-size:13px'>¿No podés venir? <a href='" + cancel + "'>Cancelá tu reserva acá</a> y liberás el lugar para otra persona.</p>");
  GmailApp.sendEmail(t.email, "Reserva confirmada · " + cfg.negocio + " · " + fechaLarga_(t.fecha) + " " + t.hora, textoPlano_(html), {
    htmlBody: html, name: cfg.negocio, replyTo: cfg.email_dueno,
    attachments: [Utilities.newBlob(ics_(cfg, t), "text/calendar", "reserva.ics")]
  });
}

function mailRecordatorio_(cfg, t) {
  var url = ScriptApp.getService().getUrl();
  var cancel = url + "?action=cancelar&id=" + t.id + "&token=" + t.token;
  var wa = "https://wa.me/" + cfg.whatsapp + "?text=" + encodeURIComponent("Hola! Confirmo mi turno " + t.id + " de mañana " + t.hora + ". " + t.nombre);
  var html = plantilla_(cfg, "Te esperamos mañana",
    "<p>Hola " + esc_(t.nombre.split(" ")[0] ) + ", te recordamos tu reserva:</p>" + tarjeta_(cfg, t) +
    "<div style='margin:20px 0 8px'>" + boton_(wa, "Confirmar por WhatsApp", "#25D366") + "</div>" +
    "<p style='color:#6B645D;font-size:13px'>Si no podés venir, <a href='" + cancel + "'>cancelá acá</a>. Gracias!</p>");
  GmailApp.sendEmail(t.email, "Recordatorio · " + cfg.negocio + " · mañana " + t.hora, textoPlano_(html), { htmlBody: html, name: cfg.negocio, replyTo: cfg.email_dueno });
}

function mailDuenoTurno_(cfg, titulo, t, nota) {
  if (!cfg.email_dueno) return;
  var wa = "https://wa.me/" + String(t.telefono).replace(/\D/g, "") + "?text=" + encodeURIComponent("Hola " + t.nombre.split(" ")[0] + "! Te escribo de " + cfg.negocio + " por tu reserva del " + fechaLarga_(t.fecha) + " a las " + t.hora + ".");
  var html = plantilla_(cfg, titulo + ": " + t.servicio,
    tarjeta_(cfg, t) +
    "<div style='border:1px solid #E8E3DD;border-radius:14px;padding:14px 16px;background-color:#FAF8F5;color:#1E1B18'>" +
    "<div><b>" + esc_(t.nombre) + "</b></div>" +
    "<div style='margin-top:4px'>" + esc_(t.telefono) + " · " + esc_(t.email) + "</div>" +
    (t.notas ? "<div style='margin-top:8px;color:#6B645D'>" + esc_(t.notas) + "</div>" : "") + "</div>" +
    "<p style='color:#6B645D;font-size:13px;margin:14px 0 0'>" + esc_(nota) + "</p>" +
    "<div style='margin:18px 0 0'>" + boton_(wa, "Escribirle por WhatsApp", "#25D366") + "</div>" +
    "<p style='color:#6B645D;font-size:12px;margin:6px 0 0'>Si el botón no abre: <a href='" + wa + "' style='color:#0E7490'>wa.me/" + String(t.telefono).replace(/\D/g, "") + "</a> · <a href='" + ss_().getUrl() + "' style='color:#0E7490'>Ver planilla de turnos</a></p>");
  GmailApp.sendEmail(cfg.email_dueno, "[Turnos] " + titulo + " · " + t.servicio + " · " + fechaLarga_(t.fecha) + " " + t.hora, textoPlano_(html), { htmlBody: html, name: cfg.negocio + " · Turnos" });
}

function mailDueno_(cfg, asunto, cuerpo) {
  if (cfg.email_dueno) GmailApp.sendEmail(cfg.email_dueno, "[Turnos] " + asunto, cuerpo);
}

function enviarRecordatorios() {
  var cfg = config_();
  var h = Number(cfg.hora_recordatorio);
  var ahora = new Date();
  if (!isNaN(h) && Number(Utilities.formatDate(ahora, TZ, "H")) !== h) return;
  var manana = new Date(ahora.getTime() + 86400000);
  var f = Utilities.formatDate(manana, TZ, "yyyy-MM-dd");
  var sh = ss_().getSheetByName("Turnos");
  var rows = sh.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (fmtFecha_(rows[i][2]) === f && rows[i][10] === "confirmado" && !rows[i][13]) {
      mailRecordatorio_(cfg, { id: rows[i][0], token: rows[i][11], fecha: f, hora: fmtHora_(rows[i][3]), dur: rows[i][4], servicio: rows[i][5], nombre: rows[i][6], telefono: rows[i][7], email: rows[i][8], notas: rows[i][9] });
      sh.getRange(i + 1, 14).setValue(new Date());
    }
  }
}

function agendaDelDia() {
  var cfg = config_();
  var hoy = Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd");
  var rows = ss_().getSheetByName("Turnos").getDataRange().getValues().slice(1)
    .filter(function (r) { return fmtFecha_(r[2]) === hoy && r[10] === "confirmado"; })
    .sort(function (a, b) { return min_(fmtHora_(a[3])) - min_(fmtHora_(b[3])); });
  if (!rows.length) return;
  var cuerpo = rows.map(function (r) { return fmtHora_(r[3]) + "  " + r[5] + "  ·  " + r[6] + "  ·  " + r[7] + (r[9] ? "  ·  " + r[9] : ""); }).join("\n");
  mailDueno_(cfg, "Agenda de hoy " + fechaLarga_(hoy) + " (" + rows.length + ")", cuerpo);
}

// ---------- web app ----------

function doGet(e) {
  var p = e.parameter || {};
  if (p.action === "cancelar") {
    var r = cancelar(p.id, p.token);
    var cfg = config_();
    var msg = r.error ? "No encontramos esa reserva." : r.ya ? "Esa reserva ya estaba cancelada." : "Tu reserva fue cancelada. Gracias por avisar!";
    return HtmlService.createHtmlOutput(plantilla_(cfg, r.error ? "Ups" : "Listo", "<p>" + msg + "</p>")).setTitle(cfg.negocio);
  }
  var out;
  if (p.action === "disponibilidad") out = disponibilidad(p.fecha, p.servicio);
  else if (p.action === "servicios") out = { servicios: servicios_(), config: publico_(config_()) };
  else out = { ok: true, negocio: config_().negocio };
  return json_(out);
}

function doPost(e) {
  var p;
  try { p = JSON.parse(e.postData.contents); } catch (err) { return json_({ error: "Datos inválidos" }); }
  return json_(reservar(p));
}

function publico_(cfg) {
  return { negocio: cfg.negocio, intervalo_min: cfg.intervalo_min, anticipacion_max_dias: cfg.anticipacion_max_dias,
    horario_lun_vie: cfg.horario_lun_vie, horario_sab: cfg.horario_sab, horario_dom: cfg.horario_dom };
}

function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// ---------- helpers ----------

function min_(hhmm) { var m = String(hhmm).split(":"); return Number(m[0]) * 60 + Number(m[1] || 0); }
function hhmm_(m) { return ("0" + Math.floor(m / 60)).slice(-2) + ":" + ("0" + (m % 60)).slice(-2); }
function fmtFecha_(v) { return v instanceof Date ? Utilities.formatDate(v, TZ, "yyyy-MM-dd") : String(v); }
function fmtHora_(v) { return v instanceof Date ? Utilities.formatDate(v, TZ, "HH:mm") : String(v).slice(0, 5); }
function offset_() { var o = Utilities.formatDate(new Date(), TZ, "Z"); return o.slice(0, 3) + ":" + o.slice(3); }
function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
function fechaLarga_(f) {
  var d = new Date(f + "T12:00:00");
  var dias = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  var meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  return dias[d.getDay()] + " " + d.getDate() + " de " + meses[d.getMonth()];
}
function btn_(color) { return "display:inline-block;padding:12px 20px;border-radius:999px;background-color:" + color + ";color:#ffffff;text-decoration:none;font-weight:700"; }
function boton_(url, texto, color) {
  return "<table role='presentation' cellpadding='0' cellspacing='0' border='0' style='display:inline-table;margin:0 6px 8px 0'><tr>" +
    "<td bgcolor='" + color + "' style='background-color:" + color + ";border-radius:999px;mso-padding-alt:12px 20px'>" +
    "<a href='" + url + "' target='_blank' style='display:inline-block;padding:12px 20px;color:#ffffff !important;text-decoration:none;font-weight:700;font-family:Segoe UI,Helvetica,Arial,sans-serif;font-size:15px'>" +
    "<span style='color:#ffffff'>" + texto + "</span></a></td></tr></table>";
}
function tarjeta_(cfg, t) {
  return "<div style='border:1px solid #E8E3DD;border-radius:14px;padding:16px;margin:12px 0;background-color:#FAF8F5;color:#1E1B18'>" +
    "<div style='font-size:18px;font-weight:700'>" + esc_(t.servicio) + "</div>" +
    "<div style='font-size:16px;margin-top:6px'>" + fechaLarga_(t.fecha) + " · <b>" + t.hora + "</b> hs</div>" +
    (cfg.direccion ? "<div style='color:#6B645D;margin-top:6px'>" + esc_(cfg.direccion) + "</div>" : "") +
    "<div style='color:#6B645D;font-size:12px;margin-top:10px'>Reserva " + t.id + "</div></div>";
}
function plantilla_(cfg, titulo, cuerpo) {
  return "<div style='font-family:Segoe UI,Helvetica,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#1E1B18;background-color:#FFFFFF'>" +
    "<div style='font-size:13px;color:#6B645D;letter-spacing:.06em;text-transform:uppercase'>" + esc_(cfg.negocio) + "</div>" +
    "<h1 style='font-size:24px;margin:6px 0 14px'>" + esc_(titulo) + "</h1>" + cuerpo +
    "<p style='color:#A79F95;font-size:11px;margin-top:28px'>" + esc_(cfg.negocio) + (cfg.direccion ? " · " + esc_(cfg.direccion) : "") + "</p></div>";
}
function textoPlano_(html) { return html.replace(/<style[\s\S]*?<\/style>/g, "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim(); }
function ics_(cfg, t) {
  var ini = new Date(t.fecha + "T" + t.hora + ":00" + offset_());
  var fin = new Date(ini.getTime() + t.dur * 60000);
  var f = function (d) { return Utilities.formatDate(d, "UTC", "yyyyMMdd'T'HHmmss'Z'"); };
  return ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//" + cfg.negocio + "//Turnos//ES", "BEGIN:VEVENT",
    "UID:" + t.id + "@turnos", "DTSTAMP:" + f(new Date()), "DTSTART:" + f(ini), "DTEND:" + f(fin),
    "SUMMARY:" + t.servicio + " · " + cfg.negocio, "LOCATION:" + (cfg.direccion || ""),
    "DESCRIPTION:Reserva " + t.id, "END:VEVENT", "END:VCALENDAR"].join("\r\n");
}
