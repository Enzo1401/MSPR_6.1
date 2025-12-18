# Fichier: main.py (ou ntl_systoolbox.py)
from modules.utils import load_config
from modules.backup_wms import backup_full_wms, export_table_to_csv # Ajout de l'export CSV ici

# --- Fonctions d'affichage des menus ---

def afficher_menu_principal():
    """Affiche les options principales de NTL-SysToolbox avec un style amélioré."""
    print("┌────────────────────────────────────────┐")
    print("│ 1 - Module Diagnostic                  │")
    print("│ 2 - Module de sauvegarde WMS           │")
    print("│ 3 - Module d'audit d'obsolescence      │")
    print("│ 4 - Quitter                            │")
    print("└────────────────────────────────────────┘")

def afficher_menu_diagnostic():
    """Affiche les options du Module Diagnostic avec un style amélioré."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║ SOUS-MENU: Module Diagnostic                                   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Vérifier l'état AD / DNS (DC01 & DC02)                      │")
    print("│ 2. Tester le bon fonctionnement de la base MySQL (WMS-DB)      │")
    print("│ 3. Vérifier l'état d'une machine Windows Server                │")
    print("│ 4. Vérifier l'état d'une machine Ubuntu                        │")
    print("│ 5. Retour au Menu Principal                                    │")
    print("└────────────────────────────────────────────────────────────────┘")

def afficher_menu_sauvegarde():
    """Affiche les options du Module de sauvegarde WMS avec un style amélioré."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║ SOUS-MENU: Module Sauvegarde WMS                               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Sauvegarde complète de la base WMS (format SQL)             │")
    print("│ 2. Export d'une table spécifique (format CSV)                  │")
    print("│ 3. Retour au Menu Principal                                    │")
    print("└────────────────────────────────────────────────────────────────┘")

def afficher_menu_audit():
    """Affiche les options du Module d'audit d'obsolescence avec un style amélioré."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║ SOUS-MENU: Module Audit d'Obsolescence                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Lister les composants sur une plage réseau                  │")
    print("│ 2. Afficher les dates de fin de vie (EOL) d'un OS donné        │")
    print("│ 3. Générer un rapport d'obsolescence (à partir d'un fichier CSV)│")
    print("│ 4. Retour au Menu Principal                                    │")
    print("└────────────────────────────────────────────────────────────────┘")

# --- Fonctions de gestion des modules ---

def gerer_diagnostic():
    """Gère le sous-menu interactif pour le Module Diagnostic."""
    while True:
        afficher_menu_diagnostic()
        choix_diag = input("Choix du diagnostic (1-5) : ")
        if choix_diag in ('1', '2', '3', '4'):
            print(f"\n[DIAGNOSTIC] Option {choix_diag} sélectionnée. Logique en cours de développement.")
            input("Appuyez sur Entrée pour continuer...") 
        elif choix_diag == '5':
            break
        else:
            print("\nChoix non valide.")

def gerer_sauvegarde_wms():
    config = load_config()
    while True:
        afficher_menu_sauvegarde()
        choix_sauv = input("Choix de la sauvegarde (1-3) : ")

        if choix_sauv == '1':
            backup_full_wms(config)
            input("\nAppuyez sur Entrée pour revenir au menu...")
        
        elif choix_sauv == '2':
            # --- AJOUT DE LA LOGIQUE EXPORT CSV ICI ---
            export_table_to_csv(config)
            input("\nAppuyez sur Entrée pour revenir au menu...")
            
        elif choix_sauv == '3':
            break
        else:
            print("\nChoix non valide.")

def gerer_audit_obsolescence():
    """Gère le sous-menu interactif pour le Module d'audit d'obsolescence."""
    while True:
        afficher_menu_audit()
        choix_audit = input("Choix de l'audit (1-4) : ")
        if choix_audit in ('1', '2', '3'):
            print(f"\n[AUDIT EOL] Option {choix_audit} sélectionnée. Logique en cours de développement.")
            input("Appuyez sur Entrée pour continuer...")
        elif choix_audit == '4':
            break
        else:
            print("\nChoix non valide.")

#########################
### Début du programme ###
#########################

print("==================================================")
print("Bienvenue dans NTL-SysToolbox, l'outil d'industrialisation NTL.")
print("==================================================")

while True:
    print("\nMENU PRINCIPAL NTL-SYSTOOLBOX")
    afficher_menu_principal()
    user_choix = input("\nQue souhaitez vous faire ? Taper le numéro (1-4) : ")
    
    if user_choix == "1":
        gerer_diagnostic()
    elif user_choix == "2":
        gerer_sauvegarde_wms()
    elif user_choix == "3":
        gerer_audit_obsolescence()
    elif user_choix == "4":
        print("\nArrêt de NTL-SysToolbox. Au revoir !")
        break
    else:
        print("\nChoix non valide.")
    