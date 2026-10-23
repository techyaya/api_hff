from fastapi import APIRouter
from pydantic import BaseModel
from db_service.dbservices import get_connection
import pyodbc

router = APIRouter()

class historiqueRequest(BaseModel):
    id_recuperation:int



@router.get("/historique")
def getHistoriqueControle():
    connection = None
    cursor = None
    sql = """        
        SELECT
        r.id_recuperation,
        r.date_recuperation,
        COUNT(*) AS recuperer,
        COUNT(c.resultat) AS analyser,
        SUM(
            CASE
                WHEN c.resultat = 'conforme' THEN 1
                ELSE 0
            END
        ) AS conforme,
        SUM(
            CASE
                WHEN c.resultat = 'anomalie' THEN 1
                    ELSE 0
                END
            ) AS anomalie , 
        SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' 
                THEN 1
                ELSE 0
            END	
        ) AS dit_analyser , 
        SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' 
                AND c.resultat = 'conforme'
                THEN 1
                ELSE 0
            END	
        ) AS dit_conforme , 
        SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' 
                AND c.resultat = 'anomalie'  
                THEN 1
                ELSE 0
            END	
        ) dit_anomalie ,
        SUM(
            CASE 
                WHEN d.type_Document = 'DEVIS ATELIER' 
                THEN 1
                ELSE 0
            END	
        ) devis_analyser , 
        SUM(
            CASE 
                WHEN d.type_Document = 'DEVIS ATELIER' 
                AND c.resultat = 'conforme'  
                THEN 1
                ELSE 0
            END	
        ) devis_conforme , 
        SUM(
            CASE 
                WHEN d.type_Document = 'DEVIS ATELIER' 
                AND c.resultat = 'anomalie'  
                THEN 1
                ELSE 0
            END	
        ) devis_anomalie , 
        SUM(
            CASE 
                WHEN d.type_Document = 'Vérification prix devis magasin' 
                THEN 1
                ELSE 0
            END	
        ) AS verif_analyser ,
        SUM(
            CASE 
                WHEN d.type_Document = 'Vérification prix devis magasin' 
                AND c.resultat = 'conforme'  
                THEN 1
                ELSE 0
            END	
        ) AS verif_conforme , 
        SUM(
            CASE 
                WHEN d.type_Document = 'Vérification prix devis magasin' 
                AND c.resultat = 'anomalie'  
                THEN 1
                ELSE 0
            END	
        ) AS verif_anomalie 
        FROM controle c
        JOIN recuperation r ON r.id_recuperation = c.id_recuperation
        JOIN document d ON d.id_document = c. id_document 
        GROUP BY
            r.date_recuperation,r.id_recuperation
        order by r.date_recuperation desc
                
        """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql)

        rows = cursor.fetchall()

        colonnes = [colonne[0] for colonne in cursor.description]

        resultats = [
            dict(zip(colonnes, row))
            for row in rows
        ]

        return resultats
    except pyodbc.Error as e:
        print("erreur historique", e)

    except Exception as e:
        print("exception levée historique", e)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()





@router.post("/historiqueByID")
def get_historique_By_id(data: historiqueRequest):
    print(data.id_recuperation)
    connection = None
    cursor = None 
    #requete à corriger  

    sql = """ 
        select d.type_document,d.numero_document, c.statut_dw, c.statut_intranet, c.resultat ,
        ABS(
            DATEDIFF(
                MINUTE,
                CAST(c.jour_dernier_maj_dw AS DATETIME)
                    + CAST(c.heur_dernier_maj AS DATETIME),
                CAST(c.jour_dernier_maj_intranet AS DATETIME)
                    + CAST(c.heur_dernier_maj_intranet AS DATETIME)
            )
        ) AS ecart
        from controle c 
        join document d on d.id_document = c.id_document
        join recuperation r on r.id_recuperation = c.id_recuperation 
        where r.id_recuperation = ?
        """

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql,(data.id_recuperation))

        rows = cursor.fetchall()
        colonnes = [colonne[0] for colonne in cursor.description]

        resultats = [
            dict(zip(colonnes, row))
            for row in rows
        ]
        
        return resultats

    except pyodbc.Error as e:
        print("erreur Historique par date ", e)

    except Exception as e:
        print("erreur historique by date ", e)

    return {"message ": data.id_recuperation }