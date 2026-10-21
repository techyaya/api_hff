import pyodbc 
from pydantic import BaseModel
from db_service.dbservices import get_connection
from fastapi import APIRouter



router = APIRouter()

class AnomalieRequest(BaseModel):
    id_recuperation: int

# class AnomalieDocument(BaseModel):
    

@router.get("/majAnomalie")
def getMajAnomalie():
    connection = None
    cursor = None
    rq = """ 
            select d.type_document, d.numero_document, c.statut_dw, c.statut_intranet, c.resultat ,
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
            where r.id_recuperation = (select MAX(id_recuperation )  from recuperation)  and c.resultat ='anomalie'
        """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(rq)
        rows = cursor.fetchall()

        colonnes = [ colonne[0] for colonne in cursor.description]

        answer = [dict(zip(colonnes, row)) for row in rows]
        return answer
    
    except pyodbc.Error as e:
        print("erreur Historique par date ", e)

    except Exception as e:
        print("erreur historique by date ", e)
   
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.post("/anomalieById")
def getAnomalieByDate(data: AnomalieRequest):

    print(data.id_recuperation)
    connection = None
    cursor = None

    rq = """
        SELECT
            d.type_document,
            d.numero_document,
            c.statut_dw,
            c.statut_intranet,
            c.resultat,
            ABS(
                DATEDIFF(
                    MINUTE,
                    CAST(c.jour_dernier_maj_dw AS DATETIME)
                        + CAST(c.heur_dernier_maj AS DATETIME),
                    CAST(c.jour_dernier_maj_intranet AS DATETIME)
                        + CAST(c.heur_dernier_maj_intranet AS DATETIME)
                )
            ) AS ecart
        FROM controle c
        JOIN document d
            ON d.id_document = c.id_document
        JOIN recuperation r
            ON r.id_recuperation = c.id_recuperation
        WHERE r.id_recuperation = ?
          AND c.resultat = 'anomalie';
    """

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(rq, (data.id_recuperation))

        rows = cursor.fetchall()

        colonnes = [colonne[0] for colonne in cursor.description]

        resultat = [
            dict(zip(colonnes, row))
            for row in rows
        ]

        return resultat

    except pyodbc.Error as e:
        print("Erreur getAnomalieByDate :", e)
        raise

    except Exception as e:
        print("Exception getAnomalieByDate :", e)
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.get("/anomalieEvolution")
def AnomalieEvolution():
   #print("evolution anomalie éxecuter")
    connection = None
    cursor = None

    rq = """ 
        select count(*) as anomalie_count, r.date_recuperation from controle c
        join recuperation r on r.id_recuperation = c.id_recuperation
        where c.resultat = 'anomalie' and r.date_recuperation > DATEADD(DAY,-8,GETDATE()) 
        group by r.id_recuperation , r.date_recuperation
        order by r.date_recuperation asc
    """

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(rq)

        rows = cursor.fetchall()

        colonnes = [ colonne[0] for colonne in cursor.description]

        resultat = [ dict(zip(colonnes,row)) for row in rows]

        return resultat

    except pyodbc.Error as e:
        print("erreur anomalie evolution ", e)

    except Exception as e:
        print("erreur excepiton anomalie evolution ", e)

    finally:
        if cursor is None:
            cursor.close()
        if connection is None:
            connection.close()
        

# @router.post("/anomalieEvolution_par_type_document")
# def AnomlieTypeDocumentEvolution():
#     return resultat