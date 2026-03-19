import requests
import subprocess
import wmi
import csv
import os
from datetime import datetime
from colorama import Fore, Style

def scanner_ip(ip):
    """Vérifie si la cible répond au ping."""
    try:
        param = '-n' if subprocess.os.name == 'nt' else '-c'
        res = subprocess.run(['ping', param, '1', ip], capture_output=True, text=True, timeout=2)
        return res.returncode == 0
    except Exception:
        return False

def scanner_plage_reseau(base_ip, debut, fin):
    """Scan de détection d'actifs sur une plage donnée."""
    print(f"\n{Fore.BLUE}⏳ Scan de la plage {base_ip}.{debut} à {base_ip}.{fin}...{Style.RESET_ALL}")
    detectees = []
    for i in range(debut, fin + 1):
        ip_test = f"{base_ip}.{i}"
        if scanner_ip(ip_test):
            print(f"{Fore.GREEN}[+] Machine active : {ip_test}")
            detectees.append(ip_test)
    print(f"\n{Fore.CYAN}Fin du scan. {len(detectees)} machine(s) trouvée(s).")
    return detectees

def recuperer_infos_os_auto(ip, username, password):
    """Récupère les détails de l'OS via WMI."""
    try:
        c = wmi.WMI(ip, user=username, password=password)
        for os_info in c.Win32_OperatingSystem():
            nom_serveur = os_info.CSName 
            nom_complet = os_info.Caption.lower()
            
            if "server" in nom_complet:
                produit = "windows-server"
                version = next((x for x in nom_complet.split() if x.isdigit()), "2019")
            else:
                produit = "windows"
                version = "10"
                
            return nom_serveur, produit, version
    except Exception as e:
        # Signal pour le compteur d'échecs du main.py
        if "0x80070005" in str(e) or "rejected" in str(e).lower():
            raise Exception("auth_failed")
        return None, None, None

def verifier_eol_api(produit, version):
    """Consulte l'API endoflife.date."""
    # Normalisation pour l'API
    if produit == "windows":
        if version == "10": version = "22h2"
        elif version == "11": version = "23h2"
    
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
        return "Erreur_API"

def lister_toutes_versions_os(produit):
    """Affiche tous les cycles de vie pour un produit donné (Option 4 du menu)."""
    url = f"https://endoflife.date/api/{produit}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"\n{Fore.CYAN}--- Cycles de vie pour {produit} ---")
            for release in response.json():
                eol = release['eol']
                today = datetime.now().strftime('%Y-%m-%d')
                color = Fore.GREEN if str(eol) == "True" or (isinstance(eol, str) and eol > today) else Fore.RED
                print(f"• Version {Fore.WHITE}{release['cycle']} {Fore.CYAN}: EOL le {color}{eol}")
        else:
            print(f"{Fore.RED}Produit '{produit}' non trouvé dans la base EOL.")
    except Exception:
        print(f"{Fore.RED}Erreur de connexion à l'API.")

def formater_resultat_eol(produit, version, eol_date):
    """Retourne le diagnostic coloré."""
    if not eol_date or eol_date == "None":
        return f"{Fore.YELLOW}Support : Date inconnue pour {produit} {version}"
    if eol_date == "Erreur_API":
        return f"{Fore.RED}Support : API injoignable."

    today = datetime.now().strftime('%Y-%m-%d')
    if eol_date == "True":
        return f"{Fore.GREEN}[CONFORME] {produit} {version} (Support étendu actif)"
    if eol_date < today:
        return f"{Fore.RED}[CRITIQUE] {produit} {version} obsolète depuis le {eol_date}"
    return f"{Fore.GREEN}[CONFORME] {produit} {version} supporté jusqu'au {eol_date}"

def traiter_fichier_csv(chemin_csv):
    """Audit à partir d'une liste CSV (Option 3 du menu)."""
    resultats = []
    try:
        if not os.path.exists(chemin_csv):
            print(f"{Fore.RED}Fichier introuvable : {chemin_csv}")
            return []
            
        with open(chemin_csv, mode='r', encoding='utf-8') as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                nom = ligne.get('nom', 'Inconnu')
                prod = ligne.get('produit', 'windows')
                ver = ligne.get('version', '10')
                eol = verifier_eol_api(prod, ver)
                statut = formater_resultat_eol(prod, ver, eol)
                resultats.append({"nom": nom, "statut": statut})
        return resultats
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la lecture du CSV : {e}")
        return []