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
    """Récupère la version OS, l'uptime, le CPU, la RAM et les disques du serveur Windows."""
    target = config['WMS_IP_DC']
    print(f"\n{Fore.CYAN}[*] Ressources Windows : {target}{Style.RESET_ALL}")
    try:
        session = winrm.Session(target, auth=(config['WIN_USER'], password), transport='ntlm')

        ps_cmd = """
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$os  = Get-CimInstance Win32_OperatingSystem
$cpu = (Get-CimInstance Win32_Processor).LoadPercentage

$os.Caption + " | Build " + $os.BuildNumber
[string]((Get-Date) - $os.LastBootUpTime).Days + "j " + ((Get-Date) - $os.LastBootUpTime).Hours + "h " + ((Get-Date) - $os.LastBootUpTime).Minutes + "min"
[string][math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1) + " Go / " + [math]::Round($os.TotalVisibleMemorySize / 1MB, 1) + " Go"
[string]$cpu + "%"

Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $u = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 1)
    $t = [math]::Round($_.Size / 1GB, 1)
    $_.DeviceID + " | " + $u + " Go / " + $t + " Go (" + [math]::Round($u/$t*100) + "% utilise)"
}
"""
        run = session.run_ps(ps_cmd)

        if run.status_code == 0:
            lines = run.std_out.decode('utf-8', errors='replace').strip().split('\r\n')
            # Les 4 premières lignes sont fixes, le reste sont les disques
            os_ver  = lines[0] if len(lines) > 0 else "Inconnu"
            uptime  = lines[1] if len(lines) > 1 else "Inconnu"
            ram     = lines[2] if len(lines) > 2 else "Inconnu"
            cpu     = lines[3] if len(lines) > 3 else "Inconnu"
            disques = lines[4:] if len(lines) > 4 else []

            print(f"{Fore.WHITE}{'─'*50}")
            print(f"  {Fore.CYAN}OS      {Fore.WHITE}: {os_ver}")
            print(f"  {Fore.CYAN}Uptime  {Fore.WHITE}: {uptime}")
            print(f"  {Fore.CYAN}CPU     {Fore.WHITE}: {Fore.YELLOW}{cpu}{Fore.WHITE} utilisation")
            print(f"  {Fore.CYAN}RAM     {Fore.WHITE}: {Fore.YELLOW}{ram}{Fore.WHITE} utilisée")
            print(f"  {Fore.CYAN}Disques {Fore.WHITE}:")
            for d in disques:
                if d.strip():
                    print(f"    {Fore.YELLOW}• {d.strip()}")
            print(f"{Fore.WHITE}{'─'*50}")
        else:
            stderr = run.std_err.decode().strip()
            print(f"{Fore.RED}❌ Échec de récupération des données.")
            if stderr:
                print(f"{Fore.RED}   Détail : {stderr}")
    except Exception as e:
        if "rejected" in str(e).lower():
            raise Exception("auth_failed")
        print(f"{Fore.RED}⚠️ Erreur WinRM : {e}")


def verif_systeme_ubuntu_direct(ip_cible, user_ssh, password):
    """Récupère la version OS, l'uptime, le CPU, la RAM et les disques du serveur Ubuntu."""
    print(f"\n{Fore.CYAN}[*] Diagnostic SSH : {ip_cible}{Style.RESET_ALL}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_cible, username=user_ssh, password=password, timeout=5)

        # Une commande par info, séparées par |||
        cmd = (
            "cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2"
            " && echo '|||'"
            " && uptime -p"
            " && echo '|||'"
            " && vmstat 1 2 | tail -1 | awk '{print 100-$15\"%\"}'"
            " && echo '|||'"
            " && free -m | awk '/^Mem:/{printf \"%d Mo / %d Mo\", $3, $2}'"
            " && echo '|||'"
            " && df -h --output=target,used,size,pcent -x tmpfs -x devtmpfs -x udev | tail -n +2"
        )

        _, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()
        err    = stderr.read().decode().strip()
        ssh.close()

        # Découpage sur le séparateur |||
        parts   = [p.strip() for p in output.split('|||')]
        os_ver  = parts[0] if len(parts) > 0 else "Inconnu"
        uptime  = parts[1] if len(parts) > 1 else "Inconnu"
        cpu     = parts[2] if len(parts) > 2 else "Inconnu"
        ram     = parts[3] if len(parts) > 3 else "Inconnu"
        disques = parts[4].split('\n') if len(parts) > 4 else []

        print(f"{Fore.GREEN}✅ Serveur accessible")
        print(f"{Fore.WHITE}{'─'*50}")
        print(f"  {Fore.CYAN}OS      {Fore.WHITE}: {os_ver}")
        print(f"  {Fore.CYAN}Uptime  {Fore.WHITE}: {uptime}")
        print(f"  {Fore.CYAN}CPU     {Fore.WHITE}: {Fore.YELLOW}{cpu}{Fore.WHITE} utilisation")
        print(f"  {Fore.CYAN}RAM     {Fore.WHITE}: {Fore.YELLOW}{ram}{Fore.WHITE} utilisée")
        print(f"  {Fore.CYAN}Disques {Fore.WHITE}:")
        for d in disques:
            if d.strip():
                print(f"    {Fore.YELLOW}• {d.strip()}")
        print(f"{Fore.WHITE}{'─'*50}")

        if err:
            print(f"{Fore.YELLOW}⚠️  Avertissements SSH : {err}")

    except paramiko.AuthenticationException:
        raise Exception("auth_failed")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Erreur SSH : {e}")