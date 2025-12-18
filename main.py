from modules.utils import load_config
from modules.backup_wms import backup_full_wms, export_table_to_csv

# --- Fonctions d'affichage des menus ---

def afficher_menu_principal():
    print("\n┌────────────────────────────────────────┐")
    print("│ 1 - Module Diagnostic                  │")
    print("│ 2 - Module de sauvegarde WMS           │")
    print("│ 3 - Module d'audit d'obsolescence      │")
    print("│ 4 - Quitter                            │")
    print("└────────────────────────────────────────┘")

def afficher_menu_sauvegarde():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║ SOUS-MENU: Module Sauvegarde WMS                               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("│ 1. Sauvegarde complète de la base WMS (format SQL)             │")
    print("│ 2. Export d'une table spécifique (format CSV)                  │")
    print("│ 3. Retour au Menu Principal                                    │")
    print("└────────────────────────────────────────────────────────────────┘")

# (Les autres fonctions d'affichage afficher_menu_diagnostic et afficher_menu_audit restent identiques à ta version)

def gerer_sauvegarde_wms():
    config = load_config()
    while True:
        afficher_menu_sauvegarde()
        choix_sauv = input("Choix de la sauvegarde (1-3) : ")

        if choix_sauv == '1':
            backup_full_wms(config)
            input("\nAppuyez sur Entrée pour revenir au menu...")
        
        elif choix_sauv == '2':
            # Cette fonction gère maintenant elle-même le listage des tables
            export_table_to_csv(config)
            input("\nAppuyez sur Entrée pour revenir au menu...")
            
        elif choix_sauv == '3':
            break
        else:
            print("\nChoix non valide.")

# (Les fonctions gerer_diagnostic et gerer_audit_obsolescence restent identiques)

#########################
### Début du programme ###
#########################

print("==================================================")
print("Bienvenue dans NTL-SysToolbox, l'outil d'industrialisation NTL.")
print("==================================================")

while True:
    afficher_menu_principal()
    user_choix = input("\nQue souhaitez vous faire ? Taper le numéro (1-4) : ")
    
    if user_choix == "1":
        # gerer_diagnostic()
        print("\n[DIAGNOSTIC] En développement...")
    elif user_choix == "2":
        gerer_sauvegarde_wms()
    elif user_choix == "3":
        # gerer_audit_obsolescence()
        print("\n[AUDIT] En développement...")
    elif user_choix == "4":
        print("\nArrêt de NTL-SysToolbox. Au revoir !")
        break
    else:
        print("\nChoix non valide.")