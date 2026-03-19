import subprocess
import datetime
import os
import csv
import mysql.connector
from modules.utils import create_output, print_result

def get_db_connection(config, password):
    """Utilitaire interne pour créer une connexion MySQL."""
    return mysql.connector.connect(
        host=config.get('WMS_DB_IP'),
        user=config.get('WMS_DB_USER'),
        password=password,
        database=config.get('WMS_DB_NAME'),
        connect_timeout=5
    )

def backup_full_wms(config, password):
    """Réalise une sauvegarde complète au format SQL via mysqldump."""
    MODULE = "SAUVEGARDE SQL"
    target = config.get('WMS_DB_IP')
    db_name = config.get('WMS_DB_NAME')
    
    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/full_backup_{db_name}_{timestamp}.sql"

    try:
        cmd = [
            "mysqldump", f"--host={target}", f"--user={config.get('WMS_DB_USER')}",
            f"--password={password}", db_name, f"--result-file={filename}"
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            res = create_output(MODULE, target, 0, f"Backup SQL créé : {filename}")
        else:
            # Si mysqldump échoue à cause du MDP, on lève une exception pour le main
            if "Access denied" in process.stderr: raise Exception("auth_failed")
            res = create_output(MODULE, target, 2, f"Erreur mysqldump : {process.stderr}")
            
    except Exception as e:
        if "auth_failed" in str(e): raise e
        res = create_output(MODULE, target, 2, f"Erreur système : {str(e)}")

    return print_result(res)

def export_table_to_csv(config, password):
    """Exporte une table sélectionnée au format CSV."""
    MODULE = "EXPORT CSV"
    target = config.get('WMS_DB_IP')
    db_name = config.get('WMS_DB_NAME')

    try:
        # 1. Récupération des tables
        conn = get_db_connection(config, password)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        all_tables = [t[0] for t in cursor.fetchall()]

        if not all_tables:
            return print_result(create_output(MODULE, target, 2, "Aucune table trouvée."))

        # 2. Sélection utilisateur
        print(f"\n--- TABLES DANS {db_name} ---")
        for i, table in enumerate(all_tables, 1): print(f"{i}. {table}")
        
        choix = int(input("\nNuméro de la table : "))
        table_name = all_tables[choix - 1]

        # 3. Export
        os.makedirs("backups/exports_csv", exist_ok=True)
        filename = f"backups/exports_csv/{table_name}_{datetime.datetime.now().strftime('%H%M%S')}.csv"
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([i[0] for i in cursor.description]) # Headers
            writer.writerows(rows)

        conn.close()
        res = create_output(MODULE, target, 0, f"Export réussi : {filename}")

    except (mysql.connector.Error, Exception) as e:
        if "Access denied" in str(e): raise Exception("auth_failed")
        res = create_output(MODULE, target, 2, f"Erreur : {str(e)}")

    return print_result(res)