import os, time, getpass, sys
from colorama import Fore, Style, init
from modules.utils import load_config, is_timeout_exceeded
from modules.backup_wms import backup_full_wms, export_table_to_csv
import modules.diagnostic as diagnostic
import modules.audit as audit

# Initialisation colorama
init(autoreset=True)

# --- Variables de Session et Sécurité ---
session_auth = {
    "pwd_win": {"value": None, "last_input": None},
    "pwd_sql": {"value": None, "last_input": None},
    "pwd_ssh": {"value": None, "last_input": None}
}
echecs_auth = 0

def reset_session():
    """Vider la mémoire pour forcer la resaisie."""
    for key in session_auth:
        session_auth[key]["value"] = None
        session_auth[key]["last_input"] = None

def get_session_password(auth_key, prompt_label):
    """Gère la session de 5min et le blocage après 3 échecs."""
    global echecs_auth
    if echecs_auth >= 3:
        print(f"\n{Fore.RED}{Style.BRIGHT}!!! ACCÈS VERROUILLÉ : 3 ÉCHECS D'AUTHENTIFICATION !!!")
        sys.exit(1)

    auth = session_auth[auth_key]
    if auth["value"] is None or is_timeout_exceeded(auth["last_input"], duration_seconds=300):
        print(f"\n{Fore.MAGENTA}[SESSION] Authentification requise : {prompt_label}")
        auth["value"] = getpass.getpass(f"Entrez le mot de passe : ")
        auth["last_input"] = time.time()
    return auth["value"]

# --- Affichage des Menus (Style Original Restauré) ---

def afficher_menu_principal():
    print(f"\n{Fore.CYAN}┌────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│            MENU PRINCIPAL NTL          │")
    print(f"{Fore.CYAN}├────────────────────────────────────────┤")
    print("│ 1 - Module Diagnostic                  │")
    print("│ 2 - Module de sauvegarde WMS           │")
    print("│ 3 - Module d'audit d'obsolescence      │")
    print("│ 4 - Quitter                            │")
    print(f"{Fore.CYAN}└────────────────────────────────────────┘")

def afficher_menu_diagnostic():
    print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.GREEN}║          SOUS-MENU : MODULE DIAGNOSTIC                         ║")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. État AD / DNS (DC01)                                        │")
    print("│ 2. Test Base MySQL (WMS-DB)                                    │")
    print("│ 3. Ressources Windows Server (RAM)                             │")
    print("│ 4. Ressources Ubuntu (SSH)                                     │")
    print("│ 5. Retour au Menu Principal                                    │")
    print(f"{Fore.GREEN}└────────────────────────────────────────────────────────────────┘")

def afficher_menu_sauvegarde():
    print(f"\n{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.YELLOW}║          SOUS-MENU : MODULE SAUVEGARDE                         ║")
    print(f"{Fore.YELLOW}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Sauvegarde complète (SQL)                                   │")
    print("│ 2. Export d'une table (CSV)                                    │")
    print("│ 3. Retour au Menu Principal                                    │")
    print(f"{Fore.YELLOW}└────────────────────────────────────────────────────────────────┘")

def afficher_menu_audit():
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║          SOUS-MENU : MODULE AUDIT & OBSOLESCENCE               ║")
    print(f"{Fore.CYAN}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Audit Cible Unique (WMI)                                    │")
    print("│ 2. Scan Plage Réseau (Inventaire)                              │")
    print("│ 3. Audit de masse via fichier CSV                              │")
    print("│ 4. Consulter toutes les versions d'un OS                       │")
    print("│ 5. Retour au Menu Principal                                    │")
    print(f"{Fore.CYAN}└────────────────────────────────────────────────────────────────┘")

# --- Gestionnaires ---

def gerer_diagnostic(config):
    global echecs_auth
    while True:
        afficher_menu_diagnostic()
        choix = input(f"\n{Fore.YELLOW}Choix (1-5) : ")
        try:
            if choix == '1': diagnostic.check_ad_dns(config, get_session_password("pwd_win", "AD / DNS"))
            elif choix == '2': diagnostic.check_mysql(config, get_session_password("pwd_sql", "MySQL"))
            elif choix == '3': diagnostic.verif_systeme_windows(config, get_session_password("pwd_win", "Windows"))
            elif choix == '4':
                print(f"1. BDD ({config['WMS_DB_IP']}) | 2. Métier ({config['WMS_METIER_IP']})")
                ip = config['WMS_DB_IP'] if input("Cible : ") == '1' else config['WMS_METIER_IP']
                diagnostic.verif_systeme_ubuntu_direct(ip, config['SSH_USER'], get_session_password("pwd_ssh", "SSH"))
            elif choix == '5': break
            echecs_auth = 0
        except Exception as e:
            if "auth_failed" in str(e) or "rejected" in str(e).lower():
                echecs_auth += 1; reset_session()
                print(f"\n{Fore.RED}❌ ÉCHEC AUTH ({echecs_auth}/3)"); input("Entrée...")
            else: print(f"\n{Fore.RED}⚠️ ERREUR : {e}"); input("Entrée...")

def gerer_sauvegarde_wms(config):
    global echecs_auth
    while True:
        afficher_menu_sauvegarde()
        choix = input(f"\n{Fore.YELLOW}Choix (1-3) : ")
        try:
            if choix == '1': backup_full_wms(config, get_session_password("pwd_sql", "Dump SQL"))
            elif choix == '2': export_table_to_csv(config, get_session_password("pwd_sql", "Export CSV"))
            elif choix == '3': break
            echecs_auth = 0
        except Exception as e:
            if "auth_failed" in str(e):
                echecs_auth += 1; reset_session()
                print(f"\n{Fore.RED}❌ ÉCHEC SQL ({echecs_auth}/3)"); input("Entrée...")
            else: print(f"\n{Fore.RED}⚠️ ERREUR : {e}"); input("Entrée...")

def gerer_audit_obsolescence(config):
    global echecs_auth
    while True:
        afficher_menu_audit()
        choix = input(f"\n{Fore.YELLOW}Votre choix (1-5) : ")
        try:
            if choix == '1':
                pwd = get_session_password("pwd_win", "Audit WMI")
                ip, user = config.get("WMS_IP_DC"), config.get("WIN_USER")
                if audit.scanner_ip(ip):
                    host, prod, ver = audit.recuperer_infos_os_auto(ip, user, pwd)
                    if host:
                        eol = audit.verifier_eol_api(prod, ver)
                        msg = audit.formater_resultat_eol(prod, ver, eol)
                        print(f"🖥️  Serveur : {host}\n{msg}")
                        
                        # Génération du rapport structuré JSON (Exigence CDC)
                        from modules.utils import create_output, print_result
                        output = create_output("AUDIT CIBLE", ip, 0, msg, {"host": host, "eol": eol})
                        print_result(output) 
                        
                        echecs_auth = 0
                    else: 
                        raise Exception("auth_failed")
                else: 
                    print(f"{Fore.RED}❌ Injoignable.")

            elif choix == '2':
                base = input("Base IP (ex: 192.168.10) : ")
                debut = int(input("Début : "))
                fin = int(input("Fin : "))
                
                # Étape 1 : Scan de présence (Ping)
                actives = audit.scanner_plage_reseau(base, debut, fin)
                
                # Étape 2 : Identification OS (WMI) - Objectif 3 du CDC
                pwd = get_session_password("pwd_win", "Inventaire OS (WMI)")
                user = config.get("WIN_USER")
                
                print(f"\n{Fore.CYAN}--- RÉSULTATS INVENTAIRE (OS) ---")
                for ip in actives:
                    try:
                        host, prod, ver = audit.recuperer_infos_os_auto(ip, user, pwd)
                        status = f"{Fore.GREEN}{host} ({prod} {ver})" if host else f"{Fore.YELLOW}Accès WMI refusé"
                        print(f" • {ip} : {status}")
                    except Exception:
                        print(f" • {ip} : {Fore.RED}Erreur connexion")
                echecs_auth = 0

            elif choix == '3':
                res = audit.traiter_fichier_csv(input("Fichier CSV : "))
                for r in res: 
                    print(f"• {r['nom']} : {r['statut']}")

            elif choix == '4':
                audit.lister_toutes_versions_os(input("Produit (ex: windows-server) : ").lower())

            elif choix == '5': 
                break
                
            echecs_auth = 0

        except Exception as e:
            if "auth_failed" in str(e) or "rejected" in str(e).lower():
                echecs_auth += 1
                reset_session()
                print(f"\n{Fore.RED}❌ ACCÈS REFUSÉ ({echecs_auth}/3)")
                input("Appuyez sur Entrée pour continuer...")
            else: 
                print(f"\n{Fore.RED}⚠️ ERREUR : {e}")
                input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    conf_data = load_config()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")
        print(f"{Fore.CYAN}{Style.BRIGHT}    NTL-SysToolbox v1.0 - INDUSTRIALISATION")
        print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")
        afficher_menu_principal()
        choix_main = input(f"\n{Fore.YELLOW}Action (1-4) : ")
        if choix_main == "1": gerer_diagnostic(conf_data)
        elif choix_main == "2": gerer_sauvegarde_wms(conf_data)
        elif choix_main == "3": gerer_audit_obsolescence(conf_data)
        elif choix_main == "4": break