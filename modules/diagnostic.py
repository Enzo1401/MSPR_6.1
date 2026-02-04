import winrm
import paramiko
import mysql.connector
import warnings
import socket

# On ignore les alertes de sécurité WinRM (HTTP)
warnings.filterwarnings("ignore", category=UserWarning)

# --- 1. AD / DNS ---
def check_ad_dns(config, password):
    print(f"\n[*] Vérification AD / DNS ({config['WMS_IP_DC']})...")
    try:
        session = winrm.Session(config['WMS_IP_DC'], auth=(config['WIN_USER'], password), transport='ntlm')
        run = session.run_ps("Get-Service NTDS, DNS | Select-Object Name, Status")
        if run.status_code == 0:
            print("✅ Services AD/DNS connectés.")
            print(run.std_out.decode().strip())
        else:
            print("❌ Erreur lors de l'exécution du script PowerShell.")
    except Exception as e:
        print(f"⚠️ Échec WinRM : {e}")

# --- 2. MySQL ---
def check_mysql(config, password):
    print(f"\n[*] Vérification MySQL ({config['WMS_DB_IP']})...")
    try:
        conn = mysql.connector.connect(
            host=config['WMS_DB_IP'],
            user=config['WMS_DB_USER'],
            password=password,
            database=config['WMS_DB_NAME'],
            connect_timeout=3
        )
        print("✅ Base de données WMS accessible.")
        conn.close()
    except Exception as e:
        print(f"⚠️ Échec MySQL : {e}")

# --- 3. Ressources Windows ---
def verif_systeme_windows(config, password):
    print(f"\n[DIAGNOSTIC] Ressources Windows ({config['WMS_IP_DC']})")
    print("-" * 50)
    try:
        session = winrm.Session(config['WMS_IP_DC'], auth=(config['WIN_USER'], password), transport='ntlm')
        # On récupère le nom de l'OS et la RAM libre pour tester
        ps_cmd = "(Get-CimInstance Win32_OperatingSystem).Caption; (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"
        run = session.run_ps(ps_cmd)
        if run.status_code == 0:
            output = run.std_out.decode().strip().split('\r\n')
            print(f"OS : {output[0]}")
            if len(output) > 1:
                print(f"RAM Libre : {int(output[1]) // 1024} Mo")
        else:
            print("Status : ERREUR (Problème WinRM)")
    except Exception as e:
        if "rejected" in str(e).lower():
            print("Status : ERREUR D'AUTHENTIFICATION")
        else:
            print("Status : ERREUR DE CONNEXION (Serveur éteint ou pare-feu)")
    print("-" * 50)

# --- 4. Ressources Ubuntu ---
def verif_systeme_ubuntu(config, password):
    print("\n--- Quel serveur Ubuntu diagnostiquer ? ---")
    print(f"1. Serveur BDD ({config['WMS_DB_IP']})")
    print(f"2. Serveur Métier ({config['WMS_METIER_IP']})")
    
    choix = input("Votre choix (1-2) : ")
    ip_cible = config['WMS_DB_IP'] if choix == "1" else config['WMS_METIER_IP']
    
    # On utilise l'utilisateur du JSON et le mot de passe passé en argument (clair ou getpass)
    user_ssh = config['SSH_USER']

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_cible, username=user_ssh, password=password, timeout=5)
        
        stdin, stdout, stderr = ssh.exec_command("uptime -p")
        print("-" * 45)
        print(f"Cible   : {ip_cible}")
        print(f"Status  : SERVEUR JOIGNABLE")
        print(f"Uptime  : {stdout.read().decode().strip()}")
        print("-" * 45)
        ssh.close()
    except socket.timeout:
        print(f"Erreur SSH sur {ip_cible} : Serveur injoignable (VM éteinte)")
    except paramiko.AuthenticationException:
        print(f"Erreur SSH sur {ip_cible} : Identifiants incorrects (Accès refusé)")
    except Exception as e:
        print(f"Erreur SSH sur {ip_cible} : {e}")