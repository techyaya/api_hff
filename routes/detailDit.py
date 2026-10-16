
import pyodbc
from db_service.dbservices import get_connection
from fastapi import APIRouter
from pydantic import BaseModel 
router = APIRouter()


class detailRequest(BaseModel):
    numero_document : str

@router.get("/list_document")
def list_document():
    connection = None
    cursor = None
    rq = """        
        select DISTINCT (d.numero_document) from controle c
        join document d on d.id_document = c.id_document
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(rq)
        rows = cursor.fetchall()

        colonnes = [colonne[0] for colonne in cursor.description]

        resultat = [dict(zip(colonnes, row)) for row in rows]

        return resultat
    except pyodbc as e:
        print("erreur liste document :",e)

    except Exception as e: 
        print("exception error list_document",e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.post("/search_document")
def Search_document(data : detailRequest):

    connection = None
    cursor = None

    rq = """        
        select DISTINCT (d.numero_document) from controle c
        join document d on d.id_document = c.id_document
        where d.numero_document = ? 

    """

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(rq,(data.numero_document))
        rows = cursor.fetchall()

        colonnes = [colonne[0] for colonne in cursor.description]

        resultat = [dict(zip(colonnes, row)) for row in rows]

        return resultat
    except pyodbc as e:
        print("erreur liste document :",e)

    except Exception as e: 
        print("exception error list_document",e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




@router.post("/detailDocument")
def detailDocument(data : detailRequest):
    print("detailDocument executé",data.numero_document)
   
    connection = None
    cursor = None

    rq = """
    select r.date_recuperation, r.id_recuperation , d.numero_document ,c.statut_DW, c.statut_intranet , c.resultat
    from controle c
    join recuperation r on r.id_recuperation = c.id_recuperation
    join document d on d.id_document = c.id_document
    where d.numero_document = ?
    order by r.date_recuperation
    """

    try:
        connction = get_connection()
        cursor = connction.cursor()

        cursor.execute(rq,(data.numero_document))

        rows = cursor.fetchall()
        print(rows)

        colonnes = [colonne[0] for colonne in cursor.description]

        resultat = [
            dict(zip(colonnes,row)) for row in rows
        ]

        print(resultat)

        return resultat

    except pyodbc.Error as e:
        print("erreur detail document", e)

    except Exception as e: 
            print("exception error Detail Document",e)
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

