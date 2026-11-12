from service.db_services import get_connection
from fastapi import APIRouter, HTTPException
from service.email_services import SendEmail
router = APIRouter()

from pydantic import BaseModel, EmailStr

class EmailModel(BaseModel):
    email: EmailStr


@router.get("/emails")
def getEmails():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_email, email
        FROM email_monitoring
        ORDER BY id_email DESC
    """)

    resultats = cursor.fetchall()

    emails = [
        {
            "id_email": row[0],
            "email": row[1]
        }
        for row in resultats
    ]

    cursor.close()
    conn.close()

    return emails


@router.post("/emails")
def ajouter_email(data: EmailModel):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO email_monitoring (email) VALUES (?)",
            (str(data.email).lower())
        )

        conn.commit()
        return {"message": "Email ajouté"}

    except Exception:
        conn.rollback()
        raise HTTPException(400, "Email déjà existant ou erreur SQL")

    finally:
        cursor.close()
        conn.close()



@router.delete("/emails/{id}")
def supprimer_email(id: int):
    print(id)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM email_monitoring WHERE id_email = ?",
            (id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(404, "Email introuvable")

        conn.commit()
        return {"message": "Email supprimé"}

    finally:
        cursor.close()
        conn.close()



class DestinatairesModel(BaseModel):
    destinataires: list[EmailStr]


@router.post("/envoyerRapport")
def envoyer_rapport(data: DestinatairesModel):

    destinataires = [str(e) for e in data.destinataires]

    # Ta fonction existante d'envoi SMTP
    SendEmail(destinataires)

    return {"message": "Envoi effectué"}