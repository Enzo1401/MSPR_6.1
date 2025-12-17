# modules/utils.py
import json
import os
import getpass

def load_config():
    """Charge les adresses IP du fichier config.json."""
    try:
        with open('config/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Valeurs par défaut si le fichier n'existe pas encore
        return {
            "WMS_DB_IP": "10.60.176.201",
            "WMS_DB_NAME": "wms_db",
            "WMS_DB_USER": "ntl_admin"
        }

def get_credentials(key_user, key_pass, config, prompt_label):
    """Récupère l'utilisateur et demande le mot de passe de façon sécurisée."""
    user = config.get(key_user, "ntl_admin")
    # On demande le mot de passe en masqué (comme sur Linux)
    print(f"\n--- Authentification : {prompt_label} ---")
    password = getpass.getpass(f"Entrez le mot de passe pour {user}@{config.get('WMS_DB_IP')} : ")
    return user, password

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
    print(f"\n[{colors.get(output['status'])}] {output['module']} sur {output['target']}")
    print(f"Message : {output['message']}")
    return output['status']