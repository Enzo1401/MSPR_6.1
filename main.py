import os
import time
import getpass
import sys
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

echecs_auth = 0  # Compteur global d'échecs

def reset_session():
    """Vider la mémoire en cas d'erreur de saisie pour forcer la resaisie."""
    for key in session_auth:
        session_auth[key]["value"] = None
        session_auth[key]["last_input"] = None

def get_session_password(auth_key, prompt_label):
    """Gère la session de 5min et le blocage après 3 échecs."""
    global echecs_auth
    auth = session_auth[auth_key]
    
    # Sécurité : Blocage définitif si 3 erreurs
    if echecs_auth >= 3:
        print(f"\n{Fore.RED}{Style.BRIGHT}!!! ACCÈS VERROUILLÉ : 3 ÉCHECS D'AUTHENTIFICATION !!!")
        print(f"{Fore.RED}Par mesure de sécurité, l'application va s'arrêter.")
        sys.exit(1)

    # Demande du MDP si vide ou timeout de 5min (300s)
    if auth["value"] is None or is_timeout_exceeded(auth["last_input"], duration_seconds=300):
        print(f"\n{Fore.MAGENTA}[SESSION] Authentification requise pour : {prompt_label}")
        auth["value"] = getpass.getpass(f"Entrez le mot de passe : ")
        auth["last_input"] = time.time()
    
    return auth["value"]

# --- Affichage des Menus ---

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
    print(f"{Fore.GREEN}║          SOUS-MENU: Module Diagnostic                          ║")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. État AD / DNS (DC01)                                        │")
    print("│ 2. Test Base MySQL (WMS-DB)                                    │")
    print("│ 3. Ressources Windows Server                                   │")
    print("│ 4. Ressources Ubuntu (Choix cible + SSH)                       │")
    print("│ 5. Retour au Menu Principal                                    │")
    print(f"{Fore.GREEN}└────────────────────────────────────────────────────────────────┘")

def afficher_menu_sauvegarde():
    print(f"\n{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.YELLOW}║          SOUS-MENU: Module Sauvegarde WMS                      ║")
    print(f"{Fore.YELLOW}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Sauvegarde complète (SQL)                                   │")
    print("│ 2. Export d'une table (CSV)                                    │")
    print("│ 3. Retour au Menu Principal                                    │")
    print(f"{Fore.YELLOW}└────────────────────────────────────────────────────────────────┘")

# --- Gestion des Modules ---

def gerer_diagnostic(config):
    global echecs_auth
    while True:
        afficher_menu_diagnostic()
        choix = input(f"{Fore.YELLOW}Choix du diagnostic (1-5) : ")

        try:
            if choix == '1':
                pwd = get_session_password("pwd_win", "AD / DNS")
                diagnostic.check_ad_dns(config, pwd)
            
            elif choix == '2':
                pwd = get_session_password("pwd_sql", "MySQL")
                diagnostic.check_mysql(config, pwd)

            elif choix == '3':
                pwd = get_session_password("pwd_win", "Ressources Windows")
                diagnostic.verif_systeme_windows(config, pwd)

            elif choix == '4':
                print(f"\n{Fore.YELLOW}--- Sélection du serveur Ubuntu ---")
                print(f"1. Serveur BDD ({config['WMS_DB_IP']})")
                print(f"2. Serveur Métier ({config['WMS_METIER_IP']})")
                cible = input("Votre choix (1-2) : ")
                ip_cible = config['WMS_DB_IP'] if cible == "1" else config['WMS_METIER_IP']
                
                pwd = get_session_password("pwd_ssh", f"Accès SSH sur {ip_cible}")
                diagnostic.verif_systeme_ubuntu_direct(ip_cible, config['SSH_USER'], pwd)

            elif choix == '5':
                break
            
            echecs_auth = 0 # Reset si succès

        except Exception as e:
            err_msg = str(e).lower()
            if "rejected" in err_msg or "authentication" in err_msg or "401" in err_msg:
                echecs_auth += 1
                reset_session()
                print(f"\n{Fore.RED}❌ ÉCHEC : Identifiants incorrects ({echecs_auth}/3)")
            else:
                print(f"\n{Fore.RED}⚠️ ERREUR TECHNIQUE : {e}")

        input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

def gerer_sauvegarde_wms(config):
    global echecs_auth
    while True:
        afficher_menu_sauvegarde()
        choix_sauv = input(f"{Fore.YELLOW}Choix de la sauvegarde (1-3) : ")

        try:
            if choix_sauv == '1':
                pwd = get_session_password("pwd_sql", "Dump SQL")
                backup_full_wms(config, pwd)
            elif choix_sauv == '2':
                pwd = get_session_password("pwd_sql", "Export CSV")
                export_table_to_csv(config, pwd)
            elif choix_sauv == '3':
                break
            echecs_auth = 0
        except Exception as e:
            if "password" in str(e).lower() or "denied" in str(e).lower():
                echecs_auth += 1
                reset_session()
                print(f"\n{Fore.RED}❌ ÉCHEC MySQL : Accès refusé ({echecs_auth}/3)")
            else:
                print(f"\n{Fore.RED}⚠️ ERREUR : {e}")
        
        input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

def gerer_audit_obsolescence(config):
    global echecs_auth
    
    # Récupération du MDP via session
    pwd = get_session_password("pwd_win", "Audit d'obsolescence (WMI)")
    ip_ad = config.get("WMS_IP_DC")
    user = config.get("WIN_USER")

    print(f"\n{Fore.CYAN}--- Module d'Audit NTL ---{Style.RESET_ALL}")
    print(f"Cible : {Fore.YELLOW}{ip_ad}")

    try:
        if audit.scanner_ip(ip_ad):
            print(f"\n{Fore.BLUE}🔍 Scan en cours...{Style.RESET_ALL}")
            hostname, produit, version = audit.recuperer_infos_os_auto(ip_ad, user, pwd)
            
            if hostname:
                print(f"🖥️  Nom du Serveur : {Fore.WHITE}{Style.BRIGHT}{hostname}{Style.RESET_ALL}")
                date_eol = audit.verifier_eol_api(produit, version)
                print(audit.formater_resultat_eol(produit, version, date_eol))
                echecs_auth = 0
            else:
                raise Exception("rejected")
        else:
            print(f"{Fore.RED}❌ La machine {ip_ad} ne répond pas au ping.{Style.RESET_ALL}")
            
    except Exception as e:
        if "rejected" in str(e).lower() or "authentication" in str(e).lower():
            echecs_auth += 1
            reset_session()
            print(f"\n{Fore.RED}❌ ÉCHEC Audit : Accès refusé ({echecs_auth}/3)")
        else:
            print(f"\n{Fore.RED}⚠️ ERREUR : {e}")
    
    input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    config_data = load_config()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")
        print(f"{Fore.CYAN}{Style.BRIGHT}    NTL-SysToolbox v1.0 - SESSION SECURE MODE")
        print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")

        afficher_menu_principal()
        user_choix = input(f"\n{Fore.YELLOW}Action (1-4) : ")
        
        if user_choix == "1":
            gerer_diagnostic(config_data)
        elif user_choix == "2":
            gerer_sauvegarde_wms(config_data)
        elif user_choix == "3":
            gerer_audit_obsolescence(config_data)
        elif user_choix == "4":
            print(f"\n{Fore.MAGENTA}Arrêt de NTL-SysToolbox. Au revoir !")
            break
        else:
            print(f"{Fore.RED}[!] Choix non valide.")
            time.sleep(1)