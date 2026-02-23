import requests
import subprocess
import wmi
import csv
from datetime import datetime
from colorama import Fore, Style

def scanner_ip(ip):
    """Vérifie si une machine répond au ping (-n pour Windows)."""
    try:
        resultat = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True, timeout=2)
        return resultat.returncode == 0
    except Exception:
        return False

def scanner_plage_reseau(base_ip, debut, fin):
    """Objectif 3 : Lister tous les composants sur une plage réseau [cite: 2025-12-16]."""
    machines_detectees = []
    print(f"\n{Fore.BLUE}⏳ Scan de la plage {base_ip}.{debut} à {base_ip}.{fin}...")
    for i in range(debut, fin + 1):
        ip_test = f"{base_ip}.{i}"
        if scanner_ip(ip_test):
            print(f"{Fore.GREEN}[+] Machine détectée : {ip_test}")
            machines_detectees.append(ip_test)
    return machines_detectees

def recuperer_infos_os_auto(ip, username, password):
    """Récupère le nom et l'OS via WMI (Correction de l'erreur timeout) [cite: 2025-12-16]."""
    try:
        # Suppression de l'argument timeout qui causait l'erreur
        c = wmi.WMI(ip, user=username, password=password)
        for os_info in c.Win32_OperatingSystem():
            nom_serveur = os_info.CSName 
            nom_complet = os_info.Caption.lower()
            if "server" in nom_complet:
                produit = "windows-server"
                try:
                    version = nom_complet.split("server ")[1].split(" ")[0]
                except:
                    version = "2019" 
            else:
                produit = "windows"
                version = "10"
            return nom_serveur, produit, version
    except Exception as e:
        raise e

def verifier_eol_api(produit, version):
    """Interroge l'API pour les dates de fin de support."""
    if produit == "windows":
        if version == "10": version = "22h2"
        if version == "11": version = "23h2"
        if version == "7": version = "eos"

    url = f"https://endoflife.date/api/{produit}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for release in data:
                if str(release['cycle']).lower() == str(version).lower():
                    return str(release['eol'])
        return None
    except Exception:
        return "Erreur_Reseau"

def lister_toutes_versions_os(produit):
    """Objectif 2 : Lister versions et dates EOL d'un OS [cite: 2025-12-16]."""
    url = f"https://endoflife.date/api/{produit}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"\n{Fore.CYAN}--- Cycles de vie pour {produit} ---")
            for release in response.json():
                eol = release['eol']
                color = Fore.GREEN if str(eol) == "True" or str(eol) > datetime.now().strftime('%Y-%m-%d') else Fore.RED
                print(f"• Version {Fore.WHITE}{release['cycle']} {Fore.CYAN}: EOL le {color}{eol}")
        else:
            print(f"{Fore.RED}OS non trouvé.")
    except Exception:
        print(f"{Fore.RED}Erreur de connexion API.")

def formater_resultat_eol(os_name, version, eol_date):
    if not eol_date or eol_date == "None":
        return f"{Fore.YELLOW}Inconnu ({os_name} {version}){Style.RESET_ALL}"
    today = datetime.now().strftime('%Y-%m-%d')
    if eol_date == "True":
        return f"{Fore.GREEN}[CONFORME] {os_name} {version} (Support étendu){Style.RESET_ALL}"
    if eol_date < today:
        return f"{Fore.RED}[CRITIQUE] {os_name} {version} obsolète ({eol_date}){Style.RESET_ALL}"
    return f"{Fore.GREEN}[CONFORME] {os_name} {version} supporté jusqu'au {eol_date}{Style.RESET_ALL}"

def traiter_fichier_csv(chemin_csv):
    """Objectif 1 : Audit à partir d'une liste CSV [cite: 2025-12-16]."""
    resultats = []
    try:
        with open(chemin_csv, mode='r', encoding='utf-8') as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                nom, prod, ver = ligne.get('nom'), ligne.get('produit'), ligne.get('version')
                eol = verifier_eol_api(prod, ver)
                statut = formater_resultat_eol(prod, ver, eol)
                resultats.append({"nom": nom, "statut": statut})
        return resultats
    except Exception as e:
        print(f"{Fore.RED}Erreur CSV : {e}")
        return []