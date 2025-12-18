# Fichier: modules/backup_wms.py
import subprocess
import datetime
import os
import csv
import mysql.connector
from modules.utils import create_output, print_result, get_credentials

def backup_full_wms(config):
    """
    Réalise une sauvegarde complète au format SQL (via mysqldump).
    Utile pour la restauration complète en cas de crash.
    """
    MODULE = "SAUVEGARDE WMS (SQL)"
    target_ip = config.get('WMS_DB_IP', '192.168.10.21')
    db_name = config.get('WMS_DB_NAME', 'wms_db')
    
    # Récupération sécurisée des accès
    user, password = get_credentials('WMS_DB_USER', 'WMS_DB_PASS', config, "Dump SQL complet")

    # Préparation du dossier et du nom de fichier
    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/full_backup_{db_name}_{timestamp}.sql"

    try:
        # Construction de la commande mysqldump
        cmd = [
            "mysqldump",
            f"--host={target_ip}",
            f"--user={user}",
            f"--password={password}",
            db_name,
            f"--result-file={filename}"
        ]
        
        # Exécution de la commande système
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            res = create_output(MODULE, target_ip, 0, f"Succès : Backup SQL créé -> {filename}", {"file": filename})
        else:
            # En cas d'erreur de mysqldump (ex: mauvais mot de passe)
            res = create_output(MODULE, target_ip, 2, f"Erreur mysqldump : {process.stderr}", {})
            
    except Exception as e:
        res = create_output(MODULE, target_ip, 2, f"Erreur système : {str(e)}", {})

    return print_result(res)


def export_table_to_csv(config):
    """
    Exporte une table précise au format CSV (via mysql-connector).
    Utile pour l'analyse de données dans Excel.
    """
    MODULE = "EXPORT TABLE (CSV)"
    target_ip = config.get('WMS_DB_IP', '192.168.10.21')
    db_name = config.get('WMS_DB_NAME', 'wms_db')
    
    # Demander quelle table exporter à l'utilisateur
    table_name = input("\nNom de la table à exporter (ex: stocks) : ")
    
    # Récupération des accès
    user, password = get_credentials('WMS_DB_USER', 'WMS_DB_PASS', config, f"Export CSV - {table_name}")

    os.makedirs("backups/exports_csv", exist_ok=True)
    filename = f"backups/exports_csv/{table_name}_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv"

    try:
        # Connexion à la base via le connecteur Python
        conn = mysql.connector.connect(
            host=target_ip,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()

        # Requête pour récupérer toutes les données de la table
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Extraction des noms de colonnes pour l'en-tête CSV
        column_names = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

        # Écriture du fichier CSV avec séparateur ';' (standard Excel FR)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(column_names)
            writer.writerows(rows)

        conn.close()
        res = create_output(MODULE, target_ip, 0, f"Succès : {len(rows)} lignes exportées dans {filename}", {"file": filename})

    except mysql.connector.Error as err:
        res = create_output(MODULE, target_ip, 2, f"Erreur MySQL : {err}", {})
    except Exception as e:
        res = create_output(MODULE, target_ip, 2, f"Erreur système : {str(e)}", {})

    return print_result(res)