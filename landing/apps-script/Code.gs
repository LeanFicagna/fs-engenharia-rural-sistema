/**
 * Recebe os pedidos de atendimento do site, registra na planilha e avisa a empresa por email.
 * Publicar como Web App (ver README.md desta pasta).
 */

// Email que recebe os avisos (troque se for outro)
const RECIPIENT_EMAIL = "engenharfs@gmail.com";
const SHEET_NAME = "Solicitações";
const HEADERS = ["Data", "Nome", "Email", "Cidade", "UF", "Telefone", "Mensagem"];
const MAX_LENGTH = 2000;

function doPost(e) {
  const lock = LockService.getScriptLock();

  try {
    lock.waitLock(10000);

    const lead = parseLead(e);
    if (!lead) return jsonResponse({ ok: false, error: "invalid" });

    const sheet = getOrCreateSheet();
    sheet.appendRow([
      new Date(),
      safeCell(lead.name),
      safeCell(lead.email),
      safeCell(lead.city),
      safeCell(lead.uf),
      safeCell(lead.phone),
      safeCell(lead.message),
    ]);

    sendNotificationEmail(lead);
    return jsonResponse({ ok: true });
  } catch (error) {
    return jsonResponse({ ok: false, error: String(error) });
  } finally {
    lock.releaseLock();
  }
}

function parseLead(e) {
  if (!e || !e.postData || !e.postData.contents) return null;

  let data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (error) {
    return null;
  }

  const lead = {
    name: clean(data.name),
    email: clean(data.email),
    city: clean(data.city),
    uf: clean(data.uf).slice(0, 2).toUpperCase(),
    phone: clean(data.phone),
    message: clean(data.message),
  };

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email);
  if (!lead.name || !emailOk || !lead.phone || !lead.message) return null;

  return lead;
}

function clean(value) {
  return String(value == null ? "" : value).trim().slice(0, MAX_LENGTH);
}

// Evita que o Sheets interprete o texto como fórmula (=, +, -, @)
function safeCell(value) {
  return /^[=+\-@]/.test(value) ? "'" + value : value;
}

function getOrCreateSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = spreadsheet.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = spreadsheet.insertSheet(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function sendNotificationEmail(lead) {
  const body = [
    "Novo pedido de atendimento pelo site:",
    "",
    "Nome: " + lead.name,
    "Email: " + lead.email,
    "Telefone: " + lead.phone,
    "Cidade/UF: " + lead.city + " - " + lead.uf,
    "",
    "Mensagem:",
    lead.message,
  ].join("\n");

  MailApp.sendEmail({
    to: RECIPIENT_EMAIL,
    replyTo: lead.email,
    subject: "Novo pedido de atendimento - " + lead.name,
    body: body,
  });
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload)).setMimeType(
    ContentService.MimeType.JSON
  );
}
