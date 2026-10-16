from fastapi import FastAPI
import pyodbc
from db_service.dbservices import get_connection

from routes.historique import router as historique_router
from routes.anomalie import router as anomalie_router      
from routes.detailDit import router as detail_router


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(historique_router)
app.include_router(anomalie_router)
app.include_router(detail_router)


# Autoriser le frontend React à communiquer avec l'API 
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
    )


@app.get("/")
def accueil():
    return {"message": "FastAPI fonctionne correctement !"}

@app.get("/test")
def test():
    return {"statut": "OK"}

@app.get("/statistiques")
def get_statistiques():
    connection = None
    cursor = None

    try:
       
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
            SELECT
                r.date_recuperation,
                COUNT(*) AS recuperer,
                COUNT(resultat) AS analyser,
                SUM(CASE
                    WHEN resultat = 'conforme' THEN 1
                    ELSE 0
                END) AS conforme,
                SUM(CASE
                    WHEN resultat = 'anomalie' THEN 1
                    ELSE 0
                END) AS anomalie
            FROM controle c
            join recuperation r on r.id_recuperation = c.id_recuperation
            WHERE c.id_recuperation = (
                SELECT MAX(id_recuperation)
                FROM recuperation
            )
            GROUP BY r.date_recuperation
        """

        cursor.execute(sql)

        row = cursor.fetchone()

        if row is None:
            return None

        # Conversion en dictionnaire

        statistiques = {
            "date_recuperation": row[0],
            "recuperer": row[1],
            "analyser": row[2],
            "conforme": row[3] or 0,
            "anomalie": row[4] or 0
        }

        return statistiques

    except pyodbc.Error as e:
        print(f"Erreur SQL Server : {e}")
        return None

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None

    finally:
        # Fermeture des ressources
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()




@app.get("/consultation")
def getDerniersControles():
    connection = None
    cursor = None

    sql = """
        SELECT
            d.numero_document,
            c.statut_dw,
            c.statut_intranet,
            ABS(
                DATEDIFF(
                    MINUTE,
                    CAST(c.jour_dernier_maj_dw AS DATETIME)
                        + CAST(c.heur_dernier_maj AS DATETIME),
                    CAST(c.jour_dernier_maj_intranet AS DATETIME)
                        + CAST(c.heur_dernier_maj_intranet AS DATETIME)
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


