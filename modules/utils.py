import json
import os
import time
from colorama import Fore, Style

def load_config():
    """Charge la configuration depuis le dossier config."""
    config_path = os.path.join('config', 'config.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de format dans config.json : {e}")

def is_timeout_exceeded(last_input_time, duration_seconds=300):
    """Vérifie si la session de 5 minutes est expirée."""
    if last_input_time is None:
        return True
    return (time.time() - last_input_time) > duration_seconds

def create_output(module, target, status, message, data=None):
    """Structure les données de retour pour tous les modules."""
    return {
        "module": module,
        "target": target,
        "status": status, # 0=OK, 2=Erreur
        "message": message,
        "details": data or {}
    }

def print_result(output):
    """Affiche le résultat de manière standardisée dans la console."""
    status_icon = f"{Fore.GREEN}✅ OK" if output['status'] == 0 else f"{Fore.RED}❌ ERREUR"
    
    print(f"\n{status_icon} {Fore.CYAN}[{output['module']}]{Style.RESET_ALL}")
    print(f"Cible   : {output['target']}")
    print(f"Message : {output['message']}")
    
    return output['status']