import winrm
import paramiko
import mysql.connector
import warnings
import socket
from colorama import Fore, Style

# On ignore les alertes de sécurité WinRM (HTTP) pour éviter de polluer la console
warnings.filterwarnings("ignore", category=UserWarning)

# --- 1. AD / DNS ---
def check_ad_dns(config, password):
    print(f"\n{Fore.CYAN}[*] Vérification AD / DNS ({config['WMS_IP_DC']})...{Style.RESET_ALL}")
    try:
        session = winrm.Session(config['WMS_IP_DC'], auth=(config['WIN_USER'], password), transport='ntlm')
        # On vérifie si les services critiques de l'infrastructure NTL tournent
        run = session.run_ps("Get-Service NTDS, DNS | Select-Object Name, Status")
        
        if run.status_code == 0:
            print(f"{Fore.GREEN}✅ Services AD/DNS connectés.{Style.RESET_ALL}")
            print(run.std_out.decode().strip())
        else:
            print(f"{Fore.RED}❌ Erreur lors de l'exécution du script PowerShell.{Style.RESET_ALL}")
    except Exception as e:
        if "rejected" in str(e).lower() or "401" in str(e):
            raise Exception("rejected") # Remonte l'erreur au main pour le compteur
        print(f"{Fore.RED}⚠️ Échec WinRM : {e}{Style.RESET_ALL}")

# --- 2. MySQL ---
def check_mysql(config, password):
    print(f"\n{Fore.CYAN}[*] Vérification MySQL ({config['WMS_DB_IP']})...{Style.RESET_ALL}")
    try:
        conn = mysql.connector.connect(
            host=config['WMS_DB_IP'],
            user=config['WMS_DB_USER'],
            password=password,
            database=config['WMS_DB_NAME'],
            connect_timeout=3
        )
        print(f"{Fore.GREEN}✅ Base de données WMS accessible.{Style.RESET_ALL}")
        conn.close()
    except Exception as e:
        if "Access denied" in str(e) or "password" in str(e).lower():
            raise Exception("authentication failed")
        print(f"{Fore.RED}⚠️ Échec MySQL : {e}{Style.RESET_ALL}")

# --- 3. Ressources Windows ---
def verif_systeme_windows(config, password):
    print(f"\n{Fore.CYAN}[DIAGNOSTIC] Ressources Windows ({config['WMS_IP_DC']}){Style.RESET_ALL}")
    print("-" * 50)
    try:
        session = winrm.Session(config['WMS_IP_DC'], auth=(config['WIN_USER'], password), transport='ntlm')
        ps_cmd = "(Get-CimInstance Win32_OperatingSystem).Caption; (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"
        run = session.run_ps(ps_cmd)
        
        if run.status_code == 0:
            output = run.std_out.decode().strip().split('\r\n')
            print(f"OS : {Fore.WHITE}{output[0]}{Style.RESET_ALL}")
            if len(output) > 1:
                ram_mo = int(output[1]) // 1024
                print(f"RAM Libre : {Fore.YELLOW}{ram_mo} Mo{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Status : ERREUR (Problème WinRM){Style.RESET_ALL}")
    except Exception as e:
        if "rejected" in str(e).lower():
            raise Exception("rejected")
        print(f"{Fore.RED}Status : ERREUR DE CONNEXION{Style.RESET_ALL}")
    print("-" * 50)

# --- 4. Ressources Ubuntu (Version Directe pour le nouveau Main) ---
def verif_systeme_ubuntu_direct(ip_cible, user_ssh, password):
    """
    Appelée directement par le main.py après le choix de la machine.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_cible, username=user_ssh, password=password, timeout=5)
        
        stdin, stdout, stderr = ssh.exec_command("uptime -p")
        uptime = stdout.read().decode().strip()
        
        print("-" * 45)
        print(f"Cible   : {ip_cible}")
        print(f"Status  : {Fore.GREEN}SERVEUR JOIGNABLE{Style.RESET_ALL}")
        print(f"Uptime  : {uptime}")
        print("-" * 45)
        ssh.close()
    except paramiko.AuthenticationException:
        raise Exception("authentication failed") # Pour le compteur du main
    except Exception as e:
        print(f"{Fore.RED}Erreur SSH sur {ip_cible} : {e}{Style.RESET_ALL}")

# --- Ancienne fonction (optionnelle, pour compatibilité) ---
def verif_systeme_ubuntu(config, password):
    print(f"\n{Fore.YELLOW}--- Quel serveur Ubuntu diagnostiquer ? ---{Style.RESET_ALL}")
    print(f"1. Serveur BDD ({config['WMS_DB_IP']})")
    print(f"2. Serveur Métier ({config['WMS_METIER_IP']})")
    choix = input("\nVotre choix (1-2) : ")
    ip = config['WMS_DB_IP'] if choix == "1" else config['WMS_METIER_IP']
    verif_systeme_ubuntu_direct(ip, config['SSH_USER'], password)