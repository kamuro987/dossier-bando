"""Crea e invia via Brevo una campagna email con il bollettino corrente.

Legge bollettino.html, estrae il contenuto principale e lo impagina in un'email
con link al sito. Usato dal workflow .github/workflows/invia-bollettino.yml.
"""
import json
import os
import re
import urllib.request

SITO = "https://kamuro987.github.io/dossier-bando/"
API = "https://api.brevo.com/v3"


def chiama(metodo, percorso, dati=None):
    req = urllib.request.Request(
        API + percorso,
        method=metodo,
        data=json.dumps(dati).encode() if dati is not None else None,
        headers={
            "api-key": os.environ["BREVO_API_KEY"],
            "content-type": "application/json",
            "accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        corpo = r.read()
        return json.loads(corpo) if corpo else {}


def main():
    html = open("bollettino.html", encoding="utf-8").read()
    numero = re.search(r'<span class="tag">([^<]*Numero[^<]*)</span>', html)
    titolo = numero.group(1).strip() if numero else "Nuovo bollettino"
    corpo = re.search(r"<main>(.*)</main>", html, re.S).group(1)
    corpo = corpo.replace('href="dossier.html"', f'href="{SITO}dossier.html"')

    email = f"""<!DOCTYPE html><html lang="it"><body style="margin:0;background:#fbfaf7;
font-family:Arial,Helvetica,sans-serif;color:#1d2433">
<div style="max-width:640px;margin:0 auto;padding:24px">
<p style="font-size:20px;font-weight:bold;margin:0 0 4px">Dossier<span style="color:#0f6b5c">Bando</span></p>
<p style="color:#5b6475;margin:0 0 20px">Il bollettino dei bandi per associazioni e terzo settore</p>
{corpo}
<p style="margin-top:28px"><a href="{SITO}bollettino.html" style="background:#0f6b5c;color:#fff;
padding:12px 20px;border-radius:999px;text-decoration:none">Leggi sul sito</a></p>
<p style="font-size:12px;color:#5b6475;margin-top:28px">Le schede non sostituiscono gli avvisi ufficiali.
Dossier Bando – a cura di Fabio De Angelis, Viterbo.
<a href="{{{{ unsubscribe }}}}">Cancella l'iscrizione</a></p>
</div></body></html>"""

    campagna = chiama("POST", "/emailCampaigns", {
        "name": f"Bollettino – {titolo}",
        "subject": f"Bandi della settimana – {titolo}",
        "sender": {"name": "Dossier Bando", "email": os.environ["BREVO_SENDER_EMAIL"]},
        "htmlContent": email,
        "recipients": {"listIds": [int(os.environ["BREVO_LIST_ID"])]},
    })
    chiama("POST", f"/emailCampaigns/{campagna['id']}/sendNow")
    print(f"Campagna {campagna['id']} inviata.")


if __name__ == "__main__":
    main()
