from service.db_services import get_connection , get_connection_informix
from fastapi import APIRouter, HTTPException
router = APIRouter()

from pydantic import BaseModel

class UpdateData(BaseModel):
   update : str

class documenModel(BaseModel):
    numero: str
   
class OrdreReparation(BaseModel):
    numeroOr:str
    numeroVersion:int
  

class verificationPrixDevisAndDevisAtelier(BaseModel):
    numero: str
    typedocument: str
    numeroversion : int 

# update de controle
rq = """
    WITH doc_classer AS (
        SELECT
            r.id_recuperation,
            d.id_document,
            d.numero_document,
            c.statut_dw,
            c.statut_intranet,
            c.resultat,
            ROW_NUMBER() OVER (
                PARTITION BY d.numero_document
                ORDER BY r.id_recuperation DESC
            ) AS classement
        FROM controle c
        JOIN recuperation r
            ON r.id_recuperation = c.id_recuperation
        JOIN document d
            ON d.id_document = c.id_document
    )
    UPDATE c
    SET c.statut_intranet = dc.statut_dw , c.resultat = 'conforme'
    FROM controle c
    INNER JOIN doc_classer dc
        ON dc.id_document = c.id_document
        AND dc.id_recuperation = c.id_recuperation
    WHERE dc.classement = 1
        AND dc.resultat = 'anomalie'
        AND dc.numero_document = ?;
"""

#selection de statut controle statut_dw
select_statut = """
    WITH doc_classer AS (
        SELECT
            d.type_document,
            d.numero_document,
            c.statut_dw,
            c.statut_intranet,
            c.resultat,
            ROW_NUMBER() OVER (
                PARTITION BY d.numero_document
                ORDER BY r.id_recuperation DESC
            ) AS classement
        FROM controle c
        JOIN recuperation r
            ON r.id_recuperation = c.id_recuperation
        JOIN document d
            ON d.id_document = c.id_document
    )
    SELECT statut_dw
    FROM doc_classer
    WHERE classement = 1
        AND resultat = 'conforme'
        AND numero_document = ?;
"""

@router.put("/updatedit")
def update_dit(data: documenModel):

    # Recherche de l'identifiant du statut
    recherche_id = """
    SELECT ID_Statut_Demande 
    FROM Statut_demande
    WHERE Description =?;
    """

    # Mise à jour de l'intranet
    sql = """
    UPDATE di
    SET di.ID_statut_Demande = ?
    FROM demande_intervention di
    WHERE di.numero_demande_dit = ?;
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # 1. Première mise à jour
        cursor.execute(rq, data.numero)

        # 2. Récupération du statut DW
        cursor.execute(select_statut, data.numero)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DW introuvable")

        statut_dw = resultat[0]

        # 3. Recherche de l'identifiant du statut
        cursor.execute(recherche_id, statut_dw)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception(f"Statut introuvable dans Statut_demande : {statut_dw}")

        id_statut = resultat[0]

        # 4. Deuxième mise à jour
        cursor.execute(sql, id_statut, data.numero)

        # 5. Validation
        conn.commit()

        return {
            "success": True,
            "message": f"Mise à jour effectuée avec succès {data.numero} "}

    except Exception as e:
        conn.rollback()
        print("ERREUR SQL :", repr(e))
        raise e

    finally:
        cursor.close()
        conn.close()

@router.put("/updateOrdreReparation")
def update_ors_soumis_a_validation(data: OrdreReparation):

    sql = """
        UPDATE osav
        SET statut = ?
        FROM ors_soumis_a_validation osav
        WHERE numeroOr = ? AND numeroVersion = ?;
    """

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Mise à jour du contrôle
        cursor.execute(rq, data.numeroOr)

        cursor.execute(select_statut, data.numeroOr)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DW introuvable")

        statut_dw = resultat[0]

        print(statut_dw , "  ", data.numeroOr , " " , data.numeroVersion)
        # 2. Mise à jour de l'intranet
        cursor.execute(sql, statut_dw , data.numeroOr , data.numeroVersion)

        print("Nombre de lignes modifiées :", cursor.rowcount)
        print("Statut envoyé :", statut_dw)

        # 3. Validation des deux mises à jour
        conn.commit()

        return {
            "success": True,
            "message": f"Mise à jour effectuée avec succès Ordre de réparation {data.numeroOr} "}

    except Exception as e:

        if conn:
            conn.rollback()

        raise Exception(f"Erreur lors de la mise à jour : {str(e)}")

    finally:
        if conn:
            conn.close()

@router.put("/updateDemandeAchat")
def update_demande_achat(data: documenModel):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Mettre à jour le dernier contrôle anomalie
        cursor.execute(rq, data.numero)

        # 2. Récupérer le statut DocuWare
        cursor.execute(select_statut, data.numero)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable")

        statut_dw = resultat[0]

        # 3. Mettre à jour la demande d'achat
        sql = """
            UPDATE d
            SET d.statut_or = ?
            FROM da_afficher d
            WHERE d.numero_demande_appro = ?;
        """

        cursor.execute(sql, statut_dw, data.numero)

        conn.commit()

        return {
            "success": True,
            "message": "Demande d'achat mise à jour avec succès",
            "numero": data.numero
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise e

    finally:
        if conn:
            conn.close()

@router.put("/updateBADM")
def update_BADM(data: documenModel):

    recherche_id = """
        SELECT ID_Statut_Demande
        FROM Statut_demande
        WHERE Description = ? AND Code_Application = 'BDM';
    """
    sql = """
        UPDATE dmm
        SET ID_Statut_Demande = ?
        FROM Demande_Mouvement_Materiel dmm
        WHERE dmm.Numero_Demande_BADM = ?; 
    """

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Mise à jour de la table controle
        cursor.execute(rq, data.numero)

        # 2. Récupération du statut DocuWare
        cursor.execute(select_statut, data.numero)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable ou anomalie non éligible")

        statut_dw = resultat[0]

        # 3. Récupération de l'identifiant du statut
        cursor.execute(recherche_id, statut_dw)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception(f"Statut intranet introuvable : {statut_dw}")

        id_statut = resultat[0]

        # 4. Mise à jour de l'intranet
        cursor.execute(sql, id_statut, data.numero)

        if cursor.rowcount == 0:
            raise Exception("Aucune demande BADM trouvée")

        # 5. Validation de la transaction
        conn.commit()

        return {
            "success": True,
            "message": "Mise à jour effectuée avec succès BADM"
            }

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Erreur lors de la mise à jour BADM : {str(e)}")

    finally:
        if conn:
            conn.close()

@router.put("/verificationprixdevisatelier")
def update_verif_prix_and_devisAtelier(data: verificationPrixDevisAndDevisAtelier):

    sql = """
        UPDATE dsav
        SET dsav.statut = ?
        FROM devis_soumis_a_validation dsav
        WHERE dsav.type = ? AND dsav.numerodevis = ? AND dsav.numeroVersion = ?;
    """

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Mise à jour de controle
        cursor.execute(rq, data.numero)

        # 2. Récupération du statut DocuWare
        cursor.execute(select_statut, data.numero)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable ou anomalie non éligible")

        statut_dw = resultat[0]

        # 3. Mise à jour du devis dans l'intranet
        print(statut_dw, "   " , data.typedocument , "  ", data.numero , " " , data.numeroversion)
        cursor.execute(sql, statut_dw, data.typedocument, data.numero,data.numeroversion)

        print("Nombre de lignes modifiées :", cursor.rowcount)
        print("Statut envoyé :", statut_dw)
        

        if cursor.rowcount == 0:
            raise Exception("Aucun devis correspondant trouvé dans l'intranet")

        # 4. Validation de la transaction
        conn.commit()

        return {
            "success": True,
            "message": "Mise à jour effectuée avec succès (Devis) atelier"
        }

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Erreur lors de la mise à jour du devis : {str(e)}"
        )

    finally:
        if conn:
            conn.close()

@router.put("/verificationprixmagasin")
def update_verification_prix_magasin(data: documenModel):

    sql_informix = """
        UPDATE devis_soumis_a_validation_neg
        SET statut_dw = ?
        WHERE numero_devis = ?;
    """

    conn_sql = None
    conn_informix = None

    try:
        # 1. Connexion SQL Server
        conn_sql = get_connection()
        cursor_sql = conn_sql.cursor()

        # 2. Mise à jour de controle
        cursor_sql.execute(rq, data.numero)

        # 3. Récupération du statut DW
        cursor_sql.execute(select_statut, data.numero)
        resultat = cursor_sql.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable ou anomalie non éligible")

        statut_dw = resultat[0]

        # 4. Connexion Informix
        conn_informix = get_connection_informix()
        cursor_informix = conn_informix.cursor()

        # 5. Mise à jour Informix
        cursor_informix.execute(sql_informix,statut_dw, data.numero)

        if cursor_informix.rowcount == 0:
            raise Exception("Aucun devis correspondant trouvé dans Informix")

        # 6. Validation des transactions
        conn_informix.commit()
        conn_sql.commit()

        return {
            "success": True,
            "message": "Mise à jour effectuée avec succès devis magasin "
        }

    except Exception as e:

        if conn_sql:
            conn_sql.rollback()

        if conn_informix:
            conn_informix.rollback()

        raise Exception(
            f"Erreur lors de la mise à jour : {str(e)}"
        )

    finally:

        if conn_sql:
            conn_sql.close()
        if conn_informix:
            conn_informix.close()

@router.put("/updateOrdreDeMission")
def update_ordreMission(data: documenModel):
    recherche_id = """
        SELECT ID_Statut_Demande
        FROM Statut_demande
        WHERE Description = ? and Code_Application = 'DOM';
    """

    sql = """
        UPDATE dom
        SET dom.ID_Statut_Demande = ?
        FROM Demande_ordre_mission dom
        WHERE dom.Numero_Ordre_Mission = ?;
    """

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Mise à jour de controle
        cursor.execute(rq, data.numero)

        # 2. Récupération du statut DW
        cursor.execute(select_statut, data.numero)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable ou anomalie non éligible")

        statut_dw = resultat[0]

        # 3. Recherche de l'identifiant du statut
        cursor.execute(recherche_id, statut_dw)
        resultat = cursor.fetchone()

        if not resultat:
            raise Exception(f"Statut intranet introuvable : {statut_dw}")

        id_statut = resultat[0]

        # 4. Mise à jour de l'ordre de mission
        cursor.execute(sql, id_statut, data.numero)

        if cursor.rowcount == 0:
            raise Exception("Aucun ordre de mission trouvé")

        # 5. Validation
        conn.commit()

        return {
            "success": True,
            "message": "Mise à jour effectuée avec succès (Ordre de mission)"
        }

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Erreur lors de la mise à jour : {str(e)}")

    finally:
        if conn:
            conn.close()

@router.put("/devisMagasin")
def update_devis_magasin(data: documenModel):

    sql_informix = """
        UPDATE bc_client_soumis_neg
        SET statut_bc = ?
        WHERE numero_bc = ?;
    """
    conn_sql = None
    conn_informix = None

    try:
        # 1. Connexion SQL Server
        conn_sql = get_connection()
        cursor_sql = conn_sql.cursor()

        # 2. Mise à jour de controle
        cursor_sql.execute(rq, data.numero)

        # 3. Récupération du statut DW
        cursor_sql.execute(select_statut, data.numero)
        resultat = cursor_sql.fetchone()

        if not resultat:
            raise Exception("Statut DocuWare introuvable ou anomalie non éligible")

        statut_dw = resultat[0]

        # 4. Connexion Informix
        conn_informix = get_connection_informix()
        cursor_informix = conn_informix.cursor()

        # 5. Mise à jour du bon de commande
        cursor_informix.execute(sql_informix,statut_dw, data.numero)

        if cursor_informix.rowcount == 0:
            raise Exception("Aucun bon de commande correspondant trouvé") 

        # 6. Validation
        conn_informix.commit()
        conn_sql.commit()

        return {
            "success": True,
            "message": "Mise à jour effectuée avec succès (Devis magasin)"
        }

    except Exception as e:

        if conn_sql:
            conn_sql.rollback()

        if conn_informix:
            conn_informix.rollback()

        raise Exception(f"Erreur lors de la mise à jour : {str(e)}")

    finally:

        if conn_sql:
            conn_sql.close()

        if conn_informix:
            conn_informix.close()




print("NOMBRE DE ROUTES :", len(router.routes))

for route in router.routes:
    print(route.path, route.methods)