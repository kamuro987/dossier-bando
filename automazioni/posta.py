"""Casella info@dossierbando.it tramite la Hostinger Mail API.

Il token NON è nel repository: si legge dalla variabile d'ambiente POSTA_TOKEN
(il valore è nel documento Drive "Riservato – casella info@dossierbando.it").

Uso:
  python3 automazioni/posta.py nuovi                 # messaggi non letti in INBOX (json)
  python3 automazioni/posta.py leggi UID             # testo del messaggio
  python3 automazioni/posta.py letto UID             # segna come letto
  python3 automazioni/posta.py invia A OGGETTO FILE_HTML [UID_DA_RISPONDERE]
"""
import json
import os
import re
import sys
import urllib.request

BASE = "https://api.mail.hostinger.com/api/v1/mailboxes/AC3f84b920775642a0a9b657188377"


def chiama(metodo, percorso, dati=None):
    req = urllib.request.Request(
        BASE + percorso, method=metodo,
        data=json.dumps(dati).encode() if dati is not None else None,
        headers={"Authorization": "Bearer " + os.environ["POSTA_TOKEN"],
                 "Accept": "application/json", "Content-Type": "application/json",
                 "User-Agent": "dossierbando-posta/1.0"},
    )
    with urllib.request.urlopen(req) as r:
        corpo = r.read()
        return json.loads(corpo) if corpo else {}


def nuovi():
    msg = chiama("POST", "/folders/INBOX/messages/search", {})["data"]
    return [m for m in msg if m.get("unseen")]


def main():
    cmd = sys.argv[1]
    if cmd == "nuovi":
        print(json.dumps([{k: m[k] for k in ("uid", "date", "subject", "from", "replyTo", "inReplyTo")} for m in nuovi()],
                         ensure_ascii=False, indent=1))
    elif cmd == "leggi":
        print(chiama("GET", f"/folders/INBOX/messages/{int(sys.argv[2])}/text")["data"]["text"])
    elif cmd == "letto":
        chiama("PATCH", f"/folders/INBOX/messages/{int(sys.argv[2])}", {"addFlags": ["\\Seen"]})
        print("ok")
    elif cmd == "invia":
        a, oggetto, file_html = sys.argv[2:5]
        html = open(file_html, encoding="utf-8").read()
        dati = {"to": [a], "subject": oggetto, "html": html,
                "text": re.sub(r"<[^>]+>", "", html.replace("<br>", "\n").replace("</p>", "\n\n"))}
        if len(sys.argv) > 5:
            dati["inReplyTo"] = {"folder": "INBOX", "uid": int(sys.argv[5])}
        chiama("POST", "/send", dati)
        print("inviata")


if __name__ == "__main__":
    main()
