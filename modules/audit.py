import requests
import subprocess
import wmi  # Nécessite 'pip install wmi'
from datetime import datetime
from colorama import Fore, Style

def scanner_ip(ip):
    """Vérifie si une machine répond au ping."""
    try:
        # -n pour Windows
        resultat = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True, timeout=2)
        return resultat.returncode == 0
    except Exception:
        return False

def recuperer_infos_os_auto(ip, username, password):
    """Récupère le nom du serveur et l'OS via WMI."""
    try:
        # Connexion WMI
        c = wmi.WMI(ip, user=username, password=password)
        for os_info in c.Win32_OperatingSystem():
            nom_serveur = os_info.CSName 
            nom_complet = os_info.Caption.lower()
            
            if "server" in nom_complet:
                produit = "windows-server"
                # On extrait l'année (ex: "2019")
                try:
                    version = nom_complet.split("server ")[1].split(" ")[0]
                except:
                    version = "2019" # Valeur par défaut en cas d'erreur de split
            else:
                produit = "windows"
                version = "10"
                
            return nom_serveur, produit, version
    except Exception as e:
        print(f"Erreur technique WMI : {e}")
        return None, None, None

def verifier_eol_api(produit, version):
    """Interroge l'API pour les dates de fin de support."""
    url = f"https://endoflife.date/api/{produit}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # On cherche le cycle correspondant à la version (ex: "2019")
            for release in data:
                if str(release['cycle']) == str(version):
                    return str(release['eol'])
        return None
    except Exception:
        return "Erreur_Reseau"

def formater_resultat_eol(os_name, version, eol_date):
    """Formate le message final avec les couleurs."""
    if not eol_date or eol_date == "None":
        return f"{Fore.YELLOW}Inconnu ({os_name} {version}){Style.RESET_ALL}"
    
    if eol_date == "Erreur_Reseau":
        return f"{Fore.RED}Erreur : API inaccessible{Style.RESET_ALL}"

    # Vérification si le support est fini
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Cas particulier : l'API peut renvoyer 'True' pour dire "toujours supporté"
    if eol_date == "True":
        return f"{Fore.GREEN}[CONFORME] {os_name} {version} (Support à vie/étendu){Style.RESET_ALL}"

    if eol_date < today:
        return f"{Fore.RED}[CRITIQUE] {os_name} {version} obsolète ({eol_date}){Style.RESET_ALL}"
    
    return f"{Fore.GREEN}[CONFORME] {os_name} {version} supporté jusqu'au {eol_date}{Style.RESET_ALL}"