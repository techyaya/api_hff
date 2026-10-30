
import pyodbc 

from service.db_services import get_connection
from fastapi import APIRouter



router = APIRouter()



@router.get("/consultation")
def getDerniersControles():
    connection = None
    cursor = None

    sql = """
        SELECT
            d.type_document,
            d.numero_document,
            d.numero_version,
            c.statut_dw,
            c.statut_intranet,
            ABS(
                DATEDIFF(
                    MINUTE,
                    GETDATE(),
                    CAST(c.jour_dernier_maj_dw AS DATETIME)
                        + CAST(c.heur_dernier_maj AS DATETIME)
                )
            ) AS ecart,
            c.resultat
        FROM controle c
        JOIN document d
            ON d.id_document = c.id_document
        WHERE c.id_recuperation = (
            SELECT TOP (1) id_recuperation
            FROM controle
            ORDER BY id_recuperation DESC
        );
    """

    try:
        
        connection = get_connection()

        if connection is None:
            raise ConnectionError(
                "La connexion à SQL Server est indisponible."
            )

        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        # Transformation des lignes en dictionnaires
        colonnes = [colonne[0] for colonne in cursor.description]

        donnees = [
            dict(zip(colonnes, row))
            for row in rows
        ]

        return donnees

    except pyodbc.Error as e:
        print("erreur consulation ", e)
        
    except Exception as e:
        print("exception dans consulation ", e)
    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


