import subprocess
import datetime
import os
import csv
import mysql.connector
from modules.utils import create_output, print_result

def get_tables_list(target_ip, user, password, db_name):
    """Interroge la base pour lister les tables disponibles dynamiquement."""
    try:
        conn = mysql.connector.connect(
            host=target_ip,
            user=user,
            password=password,
            database=db_name,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        print(f"\n[!] Erreur lors de la récupération des tables : {e}")
        return []

def backup_full_wms(config, password):
    """Réalise une sauvegarde complète au format SQL (via mysqldump)."""
    MODULE = "SAUVEGARDE WMS (SQL)"
    target_ip = config.get('WMS_DB_IP', '10.60.176.201')
    db_name = config.get('WMS_DB_NAME', 'wms_db')
    user = config.get('WMS_DB_USER', 'ntl_admin')

    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/full_backup_{db_name}_{timestamp}.sql"

    try:
        # On utilise le password passé en paramètre par le main (logique de session)
        cmd = [
            "mysqldump",
            f"--host={target_ip}",
            f"--user={user}",
            f"--password={password}",
            db_name,
            f"--result-file={filename}"
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            res = create_output(MODULE, target_ip, 0, f"Succès : Backup SQL créé -> {filename}", {"file": filename})
        else:
            res = create_output(MODULE, target_ip, 2, f"Erreur mysqldump : {process.stderr}", {})
            
    except Exception as e:
        res = create_output(MODULE, target_ip, 2, f"Erreur système : {str(e)}", {})

    return print_result(res)

def export_table_to_csv(config, password):
    """Exporte une table sélectionnée par l'utilisateur au format CSV."""
    MODULE = "EXPORT TABLE (CSV)"
    target_ip = config.get('WMS_DB_IP', '10.60.176.201')
    db_name = config.get('WMS_DB_NAME', 'wms_db')
    user = config.get('WMS_DB_USER', 'ntl_admin')

    # Récupération et affichage de la liste des tables
    print(f"\nConnexion à {target_ip} pour lister les tables...")
    all_tables = get_tables_list(target_ip, user, password, db_name)
    
    if not all_tables:
        res = create_output(MODULE, target_ip, 2, "Impossible de lister les tables. Vérifiez vos accès ou session expirée.", {})
        return print_result(res)

    print(f"\n--- TABLES DISPONIBLES DANS '{db_name}' ---")
    for i, table in enumerate(all_tables, 1):
        print(f"{i}. {table}")

    # Sélection de la table
    try:
        choix = int(input("\nEntrez le numéro de la table à exporter : "))
        table_name = all_tables[choix - 1]
    except (ValueError, IndexError):
        print("\n[!] Sélection invalide. Retour au menu.")
        return

    # Exécution de l'exportation
    os.makedirs("backups/exports_csv", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/exports_csv/{table_name}_export_{timestamp}.csv"

    try:
        conn = mysql.connector.connect(
            host=target_ip,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        
        column_names = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(column_names)
            writer.writerows(rows)

        cursor.close()
        conn.close()
        res = create_output(MODULE, target_ip, 0, f"Succès : {len(rows)} lignes exportées ({table_name})", {"file": filename})

    except Exception as e:
        res = create_output(MODULE, target_ip, 2, f"Erreur lors de l'export : {str(e)}", {})

    return print_result(res)