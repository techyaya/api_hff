from fastapi import FastAPI
from service.schedule_service import demarrer_scheduler, arreter_scheduler
from routes.historique import router as historique_router
from routes.anomalie import router as anomalie_router      
from routes.detailDocument import router as detail_router
from routes.analyse import router as analyse_router
from routes.consultation import router as consultation_router
from routes.email import router as email_router
from routes.statitistiques import router as statistique_router

from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app):
    demarrer_scheduler()  
    yield
    arreter_scheduler()   

app = FastAPI(lifespan=lifespan)

app.include_router(historique_router)
app.include_router(anomalie_router)
app.include_router(detail_router)
app.include_router(analyse_router)
app.include_router(consultation_router)
app.include_router(email_router)
app.include_router(statistique_router)

# Autoriser le frontend React à communiquer avec l'API 
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:4173","http://172.20.11.80:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
    )


@app.get("/")
def accueil():
    return {"message": "FastAPI fonctionne correctement !"}
















































# @app.get("/consultation")
# def getDerniersControles():
#     connection = None
#     cursor = None

#     sql = """
#         SELECT
#             d.type_document,
#             d.numero_document,
#             d.numero_version,
#             c.statut_dw,
#             c.statut_intranet,
#             ABS(
#                 DATEDIFF(
#                     MINUTE,
#                     GETDATE(),
#                     CAST(c.jour_dernier_maj_dw AS DATETIME)
#                         + CAST(c.heur_dernier_maj AS DATETIME)
#                 )
#             ) AS ecart,
#             c.resultat
#         FROM controle c
#         JOIN document d
#             ON d.id_document = c.id_document
#         WHERE c.id_recuperation = (
#             SELECT TOP (1) id_recuperation
#             FROM controle
#             ORDER BY id_recuperation DESC
#         );
#     """

#     try:
        
#         connection = get_connection()

#         if connection is None:
#             raise ConnectionError(
#                 "La connexion à SQL Server est indisponible."
#             )

#         cursor = connection.cursor()

#         cursor.execute(sql)

#         rows = cursor.fetchall()

#         # Transformation des lignes en dictionnaires
#         colonnes = [colonne[0] for colonne in cursor.description]

#         donnees = [
#             dict(zip(colonnes, row))
#             for row in rows
#         ]

#         return donnees

#     except pyodbc.Error as e:
#         print("erreur consulation ", e)
        
#     except Exception as e:
#         print("exception dans consulation ", e)
#     finally:
#         if cursor is not None:
#             cursor.close()

#         if connection is not None:
#             connection.close()




#  sql = """
#             SELECT
#                 r.date_recuperation,
#                 COUNT(*) AS recuperer,
#                 COUNT(resultat) AS analyser,
#                 SUM(CASE
#                     WHEN resultat = 'conforme' THEN 1
#                     ELSE 0
#                 END) AS conforme,
#                 SUM(CASE
#                     WHEN resultat = 'anomalie' THEN 1
#                     ELSE 0
#                 END) AS anomalie
#             FROM controle c
#             join recuperation r on r.id_recuperation = c.id_recuperation
#             WHERE c.id_recuperation = (
#                 SELECT MAX(id_recuperation)
#                 FROM recuperation
#             )
#             GROUP BY r.date_recuperation
#         """