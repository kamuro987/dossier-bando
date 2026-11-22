/**
 * Trasferimento automatico della proprietà dei file
 * dalla cartella condivisa "Piano di rendita Claude" a kamuro987@gmail.com.
 *
 * Lo stesso file va incollato in DUE progetti Apps Script:
 *   - nell'account feilongjkd@gmail.com → eseguire una volta  setupFeilong()
 *   - nell'account kamuro987@gmail.com  → eseguire una volta  setupKamuro()
 *
 * In entrambi i progetti: Servizi (+) → aggiungere "Drive API" (versione v3).
 *
 * Cosa succede poi, da solo, ogni ora:
 *   1. feilong propone kamuro come nuovo proprietario dei file che ha creato nella cartella;
 *   2. kamuro accetta la proprietà.
 * Lo script agisce SOLO dentro la cartella del progetto e le sue sottocartelle.
 */

const CARTELLA_PROGETTO = '1lCO-axmAnok-3gyXz0txJ_VQQaSchA80';
const NUOVO_PROPRIETARIO = 'kamuro987@gmail.com';

/* ---------- account feilongjkd ---------- */

function setupFeilong() {
  creaTrigger_('proponiTrasferimento');
  proponiTrasferimento();
}

function proponiTrasferimento() {
  const io = Session.getActiveUser().getEmail().toLowerCase();
  perOgniElemento_(CARTELLA_PROGETTO, function (id) {
    const permessi = Drive.Permissions.list(id, {
      fields: 'permissions(id,emailAddress,role,pendingOwner)'
    }).permissions || [];
    const proprietario = permessi.find(p => p.role === 'owner');
    if (!proprietario || (proprietario.emailAddress || '').toLowerCase() !== io) return;

    const kamuro = permessi.find(p => (p.emailAddress || '').toLowerCase() === NUOVO_PROPRIETARIO);
    if (kamuro && kamuro.pendingOwner) return; // già proposto

    if (kamuro) {
      Drive.Permissions.update({ role: 'writer', pendingOwner: true }, id, kamuro.id);
    } else {
      Drive.Permissions.create(
        { type: 'user', role: 'writer', emailAddress: NUOVO_PROPRIETARIO, pendingOwner: true },
        id,
        { sendNotificationEmail: false }
      );
    }
  });
}

/* ---------- account kamuro987 ---------- */

function setupKamuro() {
  creaTrigger_('accettaTrasferimento');
  accettaTrasferimento();
}

function accettaTrasferimento() {
  const io = Session.getActiveUser().getEmail().toLowerCase();
  perOgniElemento_(CARTELLA_PROGETTO, function (id) {
    const permessi = Drive.Permissions.list(id, {
      fields: 'permissions(id,emailAddress,role,pendingOwner)'
    }).permissions || [];
    const mio = permessi.find(p => (p.emailAddress || '').toLowerCase() === io);
    if (mio && mio.pendingOwner && mio.role !== 'owner') {
      Drive.Permissions.update({ role: 'owner' }, id, mio.id, { transferOwnership: true });
    }
  });
}

/* ---------- comuni ---------- */

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
