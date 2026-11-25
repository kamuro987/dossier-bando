"""Invia la proposta di partnership (contatto unico) alle organizzazioni in partner.json.

Scrive solo alle voci senza "inviato", una email per destinatario tramite l'API
transazionale di Brevo, poi segna la data di invio. Usato dal workflow
.github/workflows/invia-partner.yml.
"""
import datetime
import html
import json
import os
import urllib.error
import urllib.request

FILE = "automazioni/partner.json"
SITO = "https://dossierbando.it/"


def testo(p):
    return f"""<p>Alla cortese attenzione di {html.escape(p['nome'])},</p>
<p>mi chiamo Fabio De Angelis e curo Dossier Bando, un servizio dedicato ad associazioni ed enti del terzo settore. Vi scrivo perché tra i vostri compiti c'è informare e sostenere le associazioni {html.escape(p['territorio'])}.</p>
<p>Pubblichiamo ogni settimana un <b>bollettino gratuito dei bandi</b> aperti per associazioni, APS, ODV e ASD, con scadenze, requisiti e importi in forma sintetica. Vi proponiamo di girarlo ai vostri iscritti o di inserirlo nella vostra newsletter, senza alcun costo: <a href="{SITO}bollettino.html">dossierbando.it/bollettino.html</a>.</p>
<p>Per le associazioni che vogliono candidarsi prepariamo anche il dossier di candidatura. Ai vostri associati possiamo riservare uno sconto del 10% sui dossier, con un codice dedicato alla vostra rete.</p>
<p>L'idea è semplice: <b>più finanziamenti per le vostre associazioni, senza la parte complicata</b>. L'esito dei bandi dipende naturalmente dagli enti finanziatori: non promettiamo vittorie, ma aiutiamo a presentare candidature complete e curate.</p>
<p>Se vi interessa, basta rispondere a questa email: vi invio volentieri un esempio del bollettino o fissiamo una breve telefonata.</p>
<p>Questo è un contatto unico: se la proposta non è di vostro interesse, non vi scriveremo più.</p>
<p>Cordiali saluti,<br>Dossier Bando – a cura di Fabio De Angelis<br>
<a href="{SITO}">dossierbando.it</a> · <a href="{SITO}privacy.html">Informativa privacy</a></p>"""


def invia(p, mittente):
    corpo = {
        "sender": {"name": "Dossier Bando – Fabio De Angelis", "email": mittente},
        "replyTo": {"email": "info@dossierbando.it", "name": "Dossier Bando"},
        "to": [{"email": p["email"], "name": p["nome"]}],
        "subject": f"Un bollettino gratuito dei bandi per le associazioni {p['territorio']}",
        "htmlContent": f'<!DOCTYPE html><html lang="it"><body style="font-family:Arial,Helvetica,sans-serif;color:#1d2433;font-size:15px;line-height:1.5">{testo(p)}</body></html>',
        "tags": ["partner"],
    }
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", method="POST",
        data=json.dumps(corpo).encode(),
        headers={"api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json", "accept": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"{}").get("messageId", "")


def main():
    dati = json.load(open(FILE, encoding="utf-8"))
    mittente = os.environ["BREVO_SENDER_EMAIL"]
    oggi = datetime.date.today().isoformat()
    inviati = errori = 0
    for p in dati["partner"]:
        if p.get("inviato"):
            continue
        try:
            mid = invia(p, mittente)
            p["inviato"] = oggi
            p["message_id"] = mid
            inviati += 1
            print(f"OK  {p['nome']} <{p['email']}>")
        except urllib.error.HTTPError as e:
            errori += 1
            p["errore"] = f"{e.code}: {e.read().decode(errors='replace')[:200]}"
            print(f"ERR {p['nome']} <{p['email']}> {p['errore']}")
    json.dump(dati, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Inviate {inviati}, errori {errori}.")


if __name__ == "__main__":
    main()
