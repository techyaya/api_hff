
from service.db_services import get_connection
import pyodbc
from fastapi import APIRouter
from pydantic import BaseModel 

router = APIRouter()


class detailRequest(BaseModel):
    ecart_recuperation : int

@router.get('/analyse')
def analyse():
    connection = None
    cursor = None
    sql = """ 
    WITH doc_classer as (
    select r.date_recuperation,
    r.id_recuperation,
    d.type_document,
    d.numero_document,
    c.statut_dw, 
    c.statut_intranet ,
    c.resultat ,ABS(DATEDIFF(MINUTE,GETDATE(),CAST(c.jour_dernier_maj_dw AS DATETIME) + CAST(c.heur_dernier_maj AS DATETIME))) as ecart,
    ROW_NUMBER() OVER(
        PARTITION BY d.numero_document 
        ORDER BY r.id_recuperation DESC 
    ) as classement
    from controle c
    join recuperation r on r.id_recuperation = c.id_recuperation
    join document d on d.id_document = c.id_document
    )
    SELECT * from doc_classer where classement = 1 and resultat = 'anomalie' and  ecart >= 30
    """
    
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        colonnes = [ colonne[0] for colonne in cursor.description]

        resultat =[ dict(zip(colonnes, row)) for row in rows]

        return resultat
        
    except pyodbc.Error as e:
        print("erreur analyse",e)
