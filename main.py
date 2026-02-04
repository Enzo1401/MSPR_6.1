import os
import getpass
from colorama import Fore, Style, init
from modules.utils import load_config
from modules.backup_wms import backup_full_wms, export_table_to_csv
import modules.diagnostic as diagnostic
import modules.audit as audit

# Initialisation colorama pour les couleurs sous Windows
init(autoreset=True)

# --- Fonctions d'affichage des menus ---

def afficher_menu_principal():
    print(f"\n{Fore.CYAN}┌────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│            MENU PRINCIPAL              │")
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
    print("│ 1. Vérifier l'état AD / DNS (DC01)                             │")
    print("│ 2. Tester le bon fonctionnement de la base MySQL (WMS-DB)      │")
    print("│ 3. Vérifier l'état d'une machine Windows Server (Ressources)   │")
    print("│ 4. Vérifier l'état d'une machine Ubuntu (Multi-serveurs)       │")
    print("│ 5. Retour au Menu Principal                                    │")
    print(f"{Fore.GREEN}└────────────────────────────────────────────────────────────────┘")

def afficher_menu_sauvegarde():
    print(f"\n{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.YELLOW}║          SOUS-MENU: Module Sauvegarde WMS                      ║")
    print(f"{Fore.YELLOW}╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Sauvegarde complète de la base WMS (format SQL)             │")
    print("│ 2. Export d'une table spécifique (format CSV)                  │")
    print("│ 3. Retour au Menu Principal                                    │")
    print(f"{Fore.YELLOW}└────────────────────────────────────────────────────────────────┘")

# --- Fonctions de gestion des modules ---

def gerer_diagnostic(config):
    """Gère les tests de diagnostic en utilisant les MDP du JSON."""
    while True:
        afficher_menu_diagnostic()
        choix = input(f"{Fore.YELLOW}Choix du diagnostic (1-5) : ")

        if choix == '1':
            diagnostic.check_ad_dns(config, config.get('WIN_PASS'))
        elif choix == '2':
            diagnostic.check_mysql(config, config.get('WMS_DB_PASS'))
        elif choix == '3':
            diagnostic.verif_systeme_windows(config, config.get('WIN_PASS'))
        elif choix == '4':
            diagnostic.verif_systeme_ubuntu(config, config.get('SSH_PASS'))
        elif choix == '5':
            break
        else:
            print(f"{Fore.RED}[!] Choix non valide.")
        input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

def gerer_sauvegarde_wms(config):
    """Gère les options de sauvegarde de la base MySQL."""
    while True:
        afficher_menu_sauvegarde()
        choix_sauv = input(f"{Fore.YELLOW}Choix de la sauvegarde (1-3) : ")

        if choix_sauv == '1':
            backup_full_wms(config)
        elif choix_sauv == '2':
            export_table_to_csv(config)
        elif choix_sauv == '3':
            break
        else:
            print(f"{Fore.RED}[!] Choix non valide.")
        input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

def gerer_audit_obsolescence(config):
    """Intégration de la logique d'audit de ton collègue."""
    IP_AD = config.get("WMS_IP_DC")
    user = config.get("WIN_USER")
    pwd = config.get("WIN_PASS")

    print(f"\n{Fore.CYAN}--- Module d'Audit NTL ---{Style.RESET_ALL}")
    print(f"Cible : {Fore.YELLOW}{IP_AD}")

    if audit.scanner_ip(IP_AD):
        print(f"\n{Fore.BLUE}🔍 Scan en cours...{Style.RESET_ALL}")
        hostname, produit, version = audit.recuperer_infos_os_auto(IP_AD, user, pwd)
        
        if hostname:
            print(f"🖥️  Nom du Serveur : {Fore.WHITE}{Style.BRIGHT}{hostname}{Style.RESET_ALL}")
            date_eol = audit.verifier_eol_api(produit, version)
            print(audit.formater_resultat_eol(produit, version, date_eol))
        else:
            print(f"{Fore.RED}❌ Échec de l'authentification ou du flux RPC/WMI.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ La machine {IP_AD} ne répond pas au ping.{Style.RESET_ALL}")
    
    input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")

#########################
### Début du programme ###
#########################

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")
    print(f"{Fore.CYAN}{Style.BRIGHT}     NTL-SysToolbox v1.0 - Industrialisation")
    print(f"{Fore.CYAN}{Style.BRIGHT}==================================================")

    # Chargement de la configuration
    try:
        config_data = load_config()
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur critique : Impossible de charger config.json ({e})")
        exit(1)

    while True:
        afficher_menu_principal()
        user_choix = input(f"\n{Fore.YELLOW}Que souhaitez-vous faire ? (1-4) : {Style.RESET_ALL}")
        
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