/**
 * Trasferimento automatico della proprietà dei file
 * dalla cartella condivisa "Piano di rendita Claude" a kamuro987@gmail.com.
 *
 * Lo stesso codice gira in DUE progetti Apps Script:
 *   - account feilongjkd@gmail.com → eseguire una volta setupFeilong()
 *   - account kamuro987@gmail.com  → eseguire una volta setupKamuro()
 * Poi, ogni ora: feilong propone kamuro come proprietario, kamuro accetta.
 * Agisce SOLO dentro la cartella del progetto e le sue sottocartelle.
 * Usa l'API REST di Drive v3 (nessun servizio avanzato da attivare).
 */

const CARTELLA_PROGETTO = '1lCO-axmAnok-3gyXz0txJ_VQQaSchA80';
const NUOVO_PROPRIETARIO = 'kamuro987@gmail.com';
const API = 'https://www.googleapis.com/drive/v3/files/';

function setupFeilong() { creaTrigger_('proponiTrasferimento'); proponiTrasferimento(); }
function setupKamuro() { creaTrigger_('accettaTrasferimento'); accettaTrasferimento(); }

function proponiTrasferimento() {
  const io = Session.getActiveUser().getEmail().toLowerCase();
  if (io === NUOVO_PROPRIETARIO) return; // non va eseguita nell'account kamuro
  perOgniElemento_(CARTELLA_PROGETTO, function (id) {
    const permessi = permessi_(id);
    const proprietario = permessi.find(p => p.role === 'owner');
    if (!proprietario || (proprietario.emailAddress || '').toLowerCase() !== io) return;
    const k = permessi.find(p => (p.emailAddress || '').toLowerCase() === NUOVO_PROPRIETARIO);
    if (k && k.pendingOwner) return;
    // Il permesso di kamuro di solito è ereditato dalla cartella: non si può modificare,
    // quindi se ne crea uno diretto con pendingOwner (Drive lo accetta anche se esiste già).
    chiama_('post', id + '/permissions?sendNotificationEmail=false',
      { type: 'user', role: 'writer', emailAddress: NUOVO_PROPRIETARIO, pendingOwner: true });
  });
}

function accettaTrasferimento() {
  const io = Session.getActiveUser().getEmail().toLowerCase();
  perOgniElemento_(CARTELLA_PROGETTO, function (id) {
    const mio = permessi_(id).find(p => (p.emailAddress || '').toLowerCase() === io);
    if (mio && mio.pendingOwner && mio.role !== 'owner') {
      chiama_('patch', id + '/permissions/' + mio.id + '?transferOwnership=true', { role: 'owner' });
    }
  });
}

function permessi_(id) {
  return chiama_('get', id + '/permissions?fields=permissions(id,emailAddress,role,pendingOwner)').permissions || [];
}

function chiama_(metodo, percorso, corpo) {
  const opzioni = {
    method: metodo,
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
    muteHttpExceptions: true
  };
  if (corpo) { opzioni.contentType = 'application/json'; opzioni.payload = JSON.stringify(corpo); }
  const r = UrlFetchApp.fetch(API + percorso, opzioni);
  if (r.getResponseCode() >= 300) throw new Error(r.getResponseCode() + ' ' + r.getContentText());
  return JSON.parse(r.getContentText() || '{}');
}

function perOgniElemento_(idCartella, azione) {
  const cartella = DriveApp.getFolderById(idCartella);
  const file = cartella.getFiles();
  while (file.hasNext()) prova_(azione, file.next().getId());
  const sotto = cartella.getFolders();
  while (sotto.hasNext()) {
    const f = sotto.next();
    prova_(azione, f.getId());
    perOgniElemento_(f.getId(), azione);
  }
}

function prova_(azione, id) {
  try { azione(id); } catch (e) { console.warn('Salto ' + id + ': ' + e.message); }
}

function creaTrigger_(nomeFunzione) {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === nomeFunzione)
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger(nomeFunzione).timeBased().everyHours(1).create();
}
