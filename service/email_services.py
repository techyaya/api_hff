import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import ssl
import requests 

from datetime import datetime
load_dotenv()

url = "http://127.0.0.1:8000/analyse"



def structureEmail():
    
    response = requests.get(url)

    table_data = response.json()

    

    html = """
    <table border="1" cellpadding="8" cellspacing="0">
        <thead>
            <tr>
                <th>Type de document</th>
                <th>Numéro document</th>
                <th>Statut DocuWare</th>
                <th>Statut Intranet</th>
                <th>Ecart de temps</th>
                <th>Résultat</th>
            </tr>
        </thead>
        <tbody>
    """
    for info in table_data:
        html += f"""
            <tr>
                <td>{info["type_document"]}</td>
                <td>{info["numero_document"]}</td>
                <td>{info["statut_DW"]}</td>
                <td>{info["statut_intranet"]}</td>
                <td>{info["ecart"]}</td>
                <td>{info["resultat"]}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
"""

    return html

def SendEmail():
    print("envoie d'email en cours ")
    html = structureEmail()

    msg = EmailMessage()
    msg["FROM"] = os.getenv("expediteur")
    msg["To"] = os.getenv("destinataire")
    msg["Subject"] = "analyse des anomalie hff"
    msg.set_content(f"Document non mis à jour le {datetime.now()}")
    msg.add_alternative(html,subtype="html")



    try:
        with smtplib.SMTP(
            "smtp.gmail.com", 587, timeout=20
        ) as smtp:
            #smtp.set_debuglevel(1)

            # smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            # smtp.ehlo()

            print("TLS OK")
            print(os.getenv("expediteur"))
            print(os.getenv("mdp"))

            smtp.login(os.getenv("expediteur"), os.getenv("mdp"))
            print("authentification ok")
    
            smtp.send_message(msg)
            print("Email envoyé avec succès !")

    except (smtplib.SMTPException, OSError) as e:
        print("Erreur :", type(e).__name__, repr(e))


