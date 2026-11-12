
import pyodbc

from service.db_services import get_connection
from fastapi import APIRouter
router = APIRouter()

@router.get("/statistiques")
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
            SUM(
            CASE
                WHEN resultat = 'conforme' THEN 1
                ELSE 0
            END) AS conforme,
            SUM(
            CASE
                WHEN resultat = 'anomalie' THEN 1
                ELSE 0
            END) AS anomalie,
            SUM(
            CASE
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' THEN 1
                ELSE 0
            END) AS nb_dit,
            SUM(CASE 
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_dit_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''INTERVENTION' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_dit_anomalie,
            SUM(
            CASE
                WHEN d.type_Document = 'DEVIS ATELIER' THEN 1
                ELSE 0
            END) AS nb_devis,
            SUM(
            CASE 
                WHEN d.type_Document = 'DEVIS ATELIER' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) as nb_devis_conforme ,
            SUM(
            CASE 
                WHEN d.type_Document = 'DEVIS ATELIER' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) as nb_devis_anomalie ,
            SUM(CASE 
                WHEN d.type_Document = 'Vérification prix devis' THEN 1
                ELSE 0
            END) AS nb_verification_prix_magasin,
            SUM(
            CASE 
                WHEN d.type_Document = 'Vérification prix devis' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_verification_prix_magasin_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'Vérification prix devis' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_verification_prix_magasin_anomalie,
            SUM(CASE 
                WHEN d.type_Document = 'ordre de réparation' THEN 1
                ELSE 0
            END) AS nb_OR,
            SUM(
            CASE 
                WHEN d.type_Document = 'ordre de réparation' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_OR_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'ordre de réparation' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_OR_anomalie,
            SUM(CASE 
                WHEN d.type_Document = 'BADM' THEN 1
                ELSE 0
            END) AS nb_BADM,
            SUM(
            CASE 
                WHEN d.type_Document = 'BADM' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_BADM_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'BADM' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_BADM_anomlie, 
            SUM(CASE 
                WHEN d.type_Document = 'DEMANDE D''ACHAT' THEN 1
                ELSE 0
            END) AS nb_demande_achat,
            SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''ACHAT' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_demande_achat_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'DEMANDE D''ACHAT' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_demande_achat_anomalie,
            SUM(CASE 
                WHEN d.type_Document = 'Ordre de mission' THEN 1
                ELSE 0
            END) AS nb_Ordre_mission,
            SUM(
            CASE 
                WHEN d.type_Document = 'Ordre de mission' AND c.resultat = 'conforme' 
                THEN 1
                ELSE 0
            END) AS nb_Ordre_mission_conforme,
            SUM(
            CASE 
                WHEN d.type_Document = 'Ordre de mission' AND c.resultat = 'anomalie' 
                THEN 1
                ELSE 0
            END) AS nb_Ordre_mission_anomalie
        FROM controle c 
        join recuperation r on r.id_recuperation = c.id_recuperation
        join document d on d.id_document = c.id_document
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
        statistiques = [
            {
            "date_recuperation": row[0]
            },
            {   
            "recuperer": row[1],
            "type_document":'global',
            "analyser": row[2],
            "conforme": row[3],
            "anomalie": row[4]
            },
            {
            "type_document": "dit",
            "recuperer": row[5],
            "analyser": row[5],
            "conforme": row[6],
            "anomalie": row[7],
            },
            {
            "type_document": "devis",
            "recuperer":row[8],
            "analyser": row[8],
            "conforme": row[9],
            "anomalie": row[10],
            },
            {
            "type_document":"verification prix",
            "recuperer":row[11],
            "analyser": row[11],
            "conforme": row[12],
            "anomalie": row[13],
            },
            {
            "type_document":"ordre de réparation",
            "recuperer":row[14],
            "analyser": row[14],
            "conforme": row[15],
            "anomalie": row[16],
            },
            {
            "type_document":"BADM",
            "recuperer":row[17],
            "analyser": row[17],
            "conforme": row[18],
            "anomalie": row[19]
            }, 
            {
            "type_document":"Demande d'achat",
            "recuperer":row[20],
            "analyser": row[20],
            "conforme": row[21],
            "anomalie": row[22]
            },{
            "type_document":"Ordre de mission",
            "recuperer":row[23],
            "analyser": row[23],
            "conforme": row[24],
            "anomalie": row[25]
            }]

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
