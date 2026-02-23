# modules/utils.py
import json
import os
import time

def load_config():
    """Charge les adresses IP du fichier config.json."""
    # On teste les deux chemins possibles pour plus de souplesse
    paths = ['config/config.json', 'config.json']
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur de lecture JSON : {e}")
    
    # Valeurs par défaut si aucun fichier n'est trouvé
    return {
        "WMS_DB_IP": "10.60.178.49",
        "WMS_DB_NAME": "wms_db",
        "WMS_DB_USER": "ntl_admin",
        "WMS_IP_DC": "10.60.178.48",
        "WIN_USER": "Administrateur",
        "WMS_METIER_IP": "192.168.0.20",
        "SSH_USER": "admin_ssh"
    }

def is_timeout_exceeded(last_input_time, duration_seconds=300):
    """
    Vérifie si le délai de session est dépassé.
    Par défaut : 300 secondes = 5 minutes.
    """
    if last_input_time is None:
        return True
    
    elapsed_time = time.time() - last_input_time
    return elapsed_time > duration_seconds

def create_output(module, target, status, message, data):
    """Formate le résultat pour la console et les logs."""
    return {
        "module": module,
        "target": target,
        "status": status, # 0=OK, 1=Warning, 2=Critique
        "message": message,
        "details": data
    }

def print_result(output):
    """Affiche le résultat proprement dans le terminal."""
    colors = {0: "✅ OK", 1: "⚠️ WARN", 2: "❌ CRITIQUE"}
    print(f"\n[{colors.get(output.get('status', 0))}] {output.get('module', 'Inconnu')} sur {output.get('target', 'Inconnue')}")
    print(f"Message : {output.get('message', 'Pas de message')}")
    return output.get('status', 0)