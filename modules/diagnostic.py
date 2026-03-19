import winrm
import paramiko
import mysql.connector
import warnings
from colorama import Fore, Style

# Désactive les avertissements HTTPS non certifiés pour WinRM
warnings.filterwarnings("ignore", category=UserWarning)

def check_ad_dns(config, password):
    """Vérifie les services AD et DNS sur le contrôleur de domaine."""
    target = config['WMS_IP_DC']
    print(f"\n{Fore.CYAN}[*] Diagnostic AD/DNS : {target}{Style.RESET_ALL}")
    try:
        session = winrm.Session(target, auth=(config['WIN_USER'], password), transport='ntlm')
        run = session.run_ps("Get-Service NTDS, DNS | Select-Object Name, Status")
        
        if run.status_code == 0:
            print(f"{Fore.GREEN}✅ Services opérationnels :")
            print(run.std_out.decode().strip())
        else:
            print(f"{Fore.RED}❌ Erreur d'exécution PowerShell.")
    except Exception as e:
        if any(msg in str(e).lower() for msg in ["rejected", "401", "unauthorized"]):
            raise Exception("auth_failed")
        print(f"{Fore.RED}⚠️ Erreur connexion : {e}")

def check_mysql(config, password):
    """Teste la connectivité à la base de données MySQL."""
    target = config['WMS_DB_IP']
    print(f"\n{Fore.CYAN}[*] Diagnostic MySQL : {target}{Style.RESET_ALL}")
    try:
        conn = mysql.connector.connect(
            host=target,
            user=config['WMS_DB_USER'],
            password=password,
            database=config['WMS_DB_NAME'],
            connect_timeout=3
        )
        print(f"{Fore.GREEN}✅ Connexion à la base '{config['WMS_DB_NAME']}' réussie.")
        conn.close()
    except Exception as e:
        if "access denied" in str(e).lower():
            raise Exception("auth_failed")
        print(f"{Fore.RED}⚠️ Erreur SQL : {e}")

def verif_systeme_windows(config, password):
    """Récupère les ressources système (RAM) du serveur Windows."""
    target = config['WMS_IP_DC']
    print(f"\n{Fore.CYAN}[*] Ressources Windows : {target}{Style.RESET_ALL}")
    try:
        session = winrm.Session(target, auth=(config['WIN_USER'], password), transport='ntlm')
        ps_cmd = "(Get-CimInstance Win32_OperatingSystem).Caption; (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"
        run = session.run_ps(ps_cmd)
        
        if run.status_code == 0:
            out = run.std_out.decode().strip().split('\r\n')
            ram = int(out[1]) // 1024 if len(out) > 1 else "Inconnu"
            print(f"{Fore.WHITE}OS : {out[0]}\nRAM Libre : {Fore.YELLOW}{ram} Mo")
        else:
            print(f"{Fore.RED}❌ Échec de récupération des données.")
    except Exception as e:
        if "rejected" in str(e).lower():
            raise Exception("auth_failed")
        print(f"{Fore.RED}⚠️ Erreur WinRM : {e}")

def verif_systeme_ubuntu_direct(ip_cible, user_ssh, password):
    """Diagnostic SSH rapide pour les serveurs Linux."""
    print(f"\n{Fore.CYAN}[*] Diagnostic SSH : {ip_cible}{Style.RESET_ALL}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_cible, username=user_ssh, password=password, timeout=5)
        
        _, stdout, _ = ssh.exec_command("uptime -p")
        uptime = stdout.read().decode().strip()
        
        print(f"{Fore.GREEN}✅ Serveur accessible\n{Fore.WHITE}Uptime : {uptime}")
        ssh.close()
    except paramiko.AuthenticationException:
        raise Exception("auth_failed")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Erreur SSH : {e}")