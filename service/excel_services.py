
# from routes.historique import getHistoriqueControle

import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from io import BytesIO

def generer_excel_historique(resultats):

    # resultats = getHistoriqueControle()

    if not resultats:
        print("Aucune donnée à exporter")
        return None

    # Création du classeur
    wb = Workbook()
    ws = wb.active
    ws.title = "Historique"

    # Récupération des colonnes
    colonnes = list(resultats[0].keys())

    # Titres, nombre de colonnes et couleurs
    groupes = [
        ("GENERALE", 5, "D9EAF7"),
        ("DEMANDE D'INTERVENTION", 3, "E2F0D9"),
        ("DEVIS ATELIER", 3, "FCE4D6"),
        ("VÉRIFICATION PRIX DEVIS", 3, "FFF2CC"),
        ("ORDRE DE RÉPARATION", 3, "E4DFEC"),
        ("BADM", 3, "DDEBF7"),
        ("DEMANDE D'ACHAT", 3, "F4CCCC"),
        ("ORDRE DE MISSION", 3, "C9DAF8"),
        ("Vérification prix magasin", 3, "D9EAD3"),  # Vert pastel
        ("Devis Magasin", 3, "FCE5CD"),              # Orange pastel
        ("BC Client Magasin", 3, "EADCF8"),         # Violet pastel
    ]

    # Création des titres regroupés à partir de la colonne B
    debut = 2

    for titre, largeur, couleur in groupes:

        fin = debut + largeur - 1

        if fin <= len(colonnes):

            # Fusion des cellules
            ws.merge_cells(
                start_row=1,
                start_column=debut,
                end_row=1,
                end_column=fin
            )

            # Ajout du titre
            ws.cell(
                row=1,
                column=debut,
                value=titre
            )

            # Application de la couleur
            remplissage = PatternFill(
                start_color=couleur,
                end_color=couleur,
                fill_type="solid"
            )

            for col in range(debut, fin + 1):
                ws.cell(row=1, column=col).fill = remplissage

        debut = fin + 1

    # Ajout des en-têtes à la deuxième ligne
    for index, colonne in enumerate(colonnes, start=1):
        ws.cell(row=2, column=index, value=colonne)

    # Ajout des données à partir de la troisième ligne
    for ligne in resultats:
        ws.append([
            ligne.get(colonne)
            for colonne in colonnes
        ])

    # Création du dossier Downloads
    # chemin = os.path.join(
    #     os.path.expanduser("~"),
    #     "Downloads"
    # )

    # os.makedirs(chemin, exist_ok=True)

    # Nom du fichier

   
    # nom_fichier = f"historique_{datetime.now():%Y%m%d_%H%M%S}.xlsx"

    # fichier = os.path.join(chemin, nom_fichier)

    # # Enregistrement
    # wb.save(fichier)

    fichier = BytesIO()
    wb.save(fichier)

   

    fichier.seek(0)
    print("Taille :", len(fichier.getvalue()))
    print("Signature :", fichier.getvalue()[:4])
    print("Export Excel terminé avec succès")

    return fichier