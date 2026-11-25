"""Invia una singola email (es. risposta a un partner) via Brevo transazionale.

Parametri da variabili d'ambiente: A, NOME_A, OGGETTO, HTML, RISPONDI_A.
Usato dal workflow manuale .github/workflows/invia-email.yml.
"""
import json
import os
import urllib.request

mittente = os.environ["BREVO_SENDER_EMAIL"]
corpo = {
    "sender": {"name": "Dossier Bando – Fabio De Angelis", "email": mittente},
    "replyTo": {"email": os.environ.get("RISPONDI_A") or mittente, "name": "Dossier Bando"},
    "to": [{"email": os.environ["A"], "name": os.environ.get("NOME_A") or os.environ["A"]}],
    "subject": os.environ["OGGETTO"],
    "htmlContent": '<!DOCTYPE html><html lang="it"><body style="font-family:Arial,Helvetica,sans-serif;color:#1d2433;font-size:15px;line-height:1.5">'
    + os.environ["HTML"] + "</body></html>",
    "tags": ["risposta"],
}
req = urllib.request.Request(
    "https://api.brevo.com/v3/smtp/email", method="POST", data=json.dumps(corpo).encode(),
    headers={"api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json", "accept": "application/json"},
)
with urllib.request.urlopen(req) as r:
    print("Inviata:", r.read().decode())
