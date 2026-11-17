import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import ssl
import requests 

from datetime import datetime
load_dotenv()

url = "http://127.0.0.1:8000/analyse"




# def ConvertionEcart(minutes):
    
#         if minutes < 60 :
#             return f"{minutes} min"
        
#         heures = minutes / 60
#         if heures < 24 :
#             return f"{round(heures,2)} h"
        
#         jours = round(heures / 24, 2)
#         if  jours < 7 :
#             return f"{jours} jours"
        
#         semaines = round(jours / 7,2 )
#         if semaines < 4: 
#             return f"{semaines} semaines"

#         mois = round(jours / 30 , 2)
#         return f"{mois} mois"



def ConvertionEcart(minutes):
    if minutes is None or minutes == "":
        return "__"

    if minutes < 60:
        return f"{minutes} min"

    heures = int(minutes // 60)
    min_restantes = int(minutes % 60)

    if heures < 24:
        return f"{heures} h {min_restantes} min"

    jours = heures // 24
    heures_restantes = heures % 24

    if jours < 7:
        return f"{jours} jours {heures_restantes} h {min_restantes} min"

    semaines = jours // 7

    if semaines < 4:
        return f"{semaines} semaines"

    mois = minutes / (60 * 24 * 30)

    return f"{mois:.1f} mois"




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
                <td>{ConvertionEcart(info["ecart"])}</td>
                <td>{info["resultat"]}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
"""

    return html

# def SendEmail(destinataire=None):
#     print("envoie d'email en cours ")
#     html = structureEmail()

#     msg = EmailMessage()
#     msg["FROM"] = os.getenv("expediteur")
#     if destinataire is None :
#         msg["To"] = os.getenv("destinataire")
#     else:
#         msg["To"] = ", ".join(destinataire)
    
#     msg["Subject"] = "analyse des anomalie hff"
#     msg.set_content(f"Document non mis à jour le {datetime.now()}")
#     msg.add_alternative(html,subtype="html")

#     try:
#         with smtplib.SMTP(
#             "smtp.gmail.com", 587, timeout=20
#         ) as smtp:
#             #smtp.set_debuglevel(1)

#             # smtp.ehlo()
#             smtp.starttls(context=ssl.create_default_context())
#             # smtp.ehlo()

#             print("TLS OK")
#             print(os.getenv("expediteur"))
#             print(os.getenv("mdp"))

#             if destinataire is None:
#                 smtp.login(os.getenv("expediteur"), os.getenv("mdp"))
#                 smtp.send_message(msg)
#             else:
#                 smtp.login(os.getenv("expediteur"), os.getenv("mdp"))
#                 smtp.send_message(msg, to_addrs=destinataire)
                
#             print("authentification ok")
    
            
#             print("Email envoyé avec succès !")

#     except (smtplib.SMTPException, OSError) as e:
#         print("Erreur :", type(e).__name__, repr(e))



def SendEmail(destinataire=None):
    print("Envoi d'email en cours")

    html = structureEmail()

    msg = EmailMessage()
    msg["From"] = os.getenv("expediteur")

    if destinataire is None:
        destinataire = [os.getenv("destinataire")]
    elif isinstance(destinataire, str):
        destinataire = [destinataire]

    msg["To"] = ", ".join(destinataire)
    msg["Subject"] = "Analyse des anomalies HFF"

    msg.set_content(f"Document non mis à jour le {datetime.now()}")
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            print("TLS OK")

            smtp.login(os.getenv("expediteur"), os.getenv("mdp"))
            print("Authentification OK")

            smtp.send_message(msg, to_addrs=destinataire)

            print("Email envoyé avec succès !")
          

           

    except (smtplib.SMTPException, OSError) as e:
        print("Erreur :", type(e).__name__, repr(e))
        raise
