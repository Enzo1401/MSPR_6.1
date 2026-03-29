import platform, requests, subprocess, csv, os, json
from datetime import datetime, timedelta
from colorama import Fore, Style

if platform.system() == "Windows":
    import wmi

SEUIL_EOL_JOURS = 180


# ─── Réseau 

def scanner_ip(ip):
    try:
        param = '-n' if os.name == 'nt' else '-c'
        return subprocess.run(['ping', param, '1', ip], capture_output=True, timeout=2).returncode == 0
    except:
        return False

def scanner_plage_reseau(base_ip, debut, fin):
    print(f"\n{Fore.BLUE}⏳ Scan {base_ip}.{debut} → {base_ip}.{fin}...{Style.RESET_ALL}")
    detectees = [f"{base_ip}.{i}" for i in range(debut, fin+1) if scanner_ip(f"{base_ip}.{i}")]
    for ip in detectees:
        print(f"{Fore.GREEN}[+] {ip}")
    print(f"\n{Fore.CYAN}{len(detectees)} machine(s) trouvée(s).")
    return detectees


# ─── WMI

def recuperer_infos_os_auto(ip, username, password):
    if platform.system() != "Windows":
        print(f"{Fore.YELLOW}⚠️  WMI non disponible sous Linux.")
        return None, None, None
    try:
        c = wmi.WMI(ip, user=username, password=password)
        for o in c.Win32_OperatingSystem():
            nom = o.Caption.lower()
            produit = "windows-server" if "server" in nom else "windows"
            version = next((x for x in nom.split() if x.isdigit()), "2019" if "server" in nom else "10")
            return o.CSName, produit, version
    except Exception as e:
        if "0x80070005" in str(e) or "rejected" in str(e).lower():
            raise Exception("auth_failed")
        return None, None, None


# ─── EOL API 

def verifier_eol_api(produit, version):
    if produit == "windows":
        version = {"10": "22h2", "11": "23h2"}.get(version, version)
    try:
        data = requests.get(f"https://endoflife.date/api/{produit}.json", timeout=5).json()
        for r in data:
            if str(r['cycle']).lower() == str(version).lower():
                return str(r['eol'])
    except:
        return "Erreur_API"
    return None

def lister_toutes_versions_os(produit):
    try:
        data = requests.get(f"https://endoflife.date/api/{produit}.json", timeout=5).json()
        print(f"\n{Fore.CYAN}--- Cycles de vie : {produit} ---")
        today = datetime.now().strftime('%Y-%m-%d')
        for r in data:
            c = Fore.GREEN if str(r['eol']) == "True" or (isinstance(r['eol'], str) and r['eol'] > today) else Fore.RED
            print(f"• {Fore.WHITE}{r['cycle']} {Fore.CYAN}: EOL {c}{r['eol']}")
    except:
        print(f"{Fore.RED}Erreur de connexion à l'API.")

def classifier_statut(eol):
    if not eol or eol == "None":   return "INCONNU",    "Date inconnue"
    if eol == "Erreur_API":        return "INCONNU",    "API injoignable"
    if eol == "True":              return "ETENDU",     "Support étendu actif"
    today = datetime.now().date()
    try:
        eol_dt = datetime.strptime(eol, "%Y-%m-%d").date()
    except:
        return "INCONNU", f"Format inattendu : {eol}"
    if eol_dt < today:
        return "OBSOLETE",    f"Obsolète depuis le {eol} ({(today-eol_dt).days}j)"
    if eol_dt <= today + timedelta(days=SEUIL_EOL_JOURS):
        return "BIENTOT_EOL", f"EOL le {eol} (dans {(eol_dt-today).days}j)"
    return "CONFORME", f"Supporté jusqu'au {eol}"

def formater_resultat_eol(produit, version, eol):
    code, label = classifier_statut(eol)
    couleurs  = {"OBSOLETE": Fore.RED, "BIENTOT_EOL": Fore.YELLOW, "CONFORME": Fore.GREEN, "ETENDU": Fore.GREEN, "INCONNU": Fore.YELLOW}
    prefixes  = {"OBSOLETE": "[CRITIQUE]", "BIENTOT_EOL": "[ATTENTION]", "CONFORME": "[CONFORME]", "ETENDU": "[CONFORME]", "INCONNU": "[INCONNU]"}
    return f"{couleurs.get(code, Fore.WHITE)}{prefixes.get(code, '')} {produit} {version} — {label}"


# ─── Rapport 

def generer_rapport(resultats):
    os.makedirs("docs", exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    hod = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    cats = {"OBSOLETE": [], "BIENTOT_EOL": [], "CONFORME": [], "ETENDU": [], "INCONNU": []}
    for r in resultats:
        cats[r["statut_code"]].append(r)

    # JSON
    with open(f"docs/audit_eol_{ts}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "rapport": "NTL-SysToolbox — Audit d'obsolescence", "genere_le": hod,
            "seuil_jours": SEUIL_EOL_JOURS,
            "resume": {"total": len(resultats), "obsoletes": len(cats["OBSOLETE"]),
                       "bientot_eol": len(cats["BIENTOT_EOL"]),
                       "conformes": len(cats["CONFORME"]) + len(cats["ETENDU"]),
                       "inconnus": len(cats["INCONNU"])},
            "composants": resultats
        }, f, ensure_ascii=False, indent=2)

    # TXT
    lines = ["=" * 60, "  NTL-SysToolbox — Audit d'obsolescence", f"  Généré le : {hod}",
             f"  Seuil alerte : {SEUIL_EOL_JOURS} jours", "=" * 60, "",
             "RÉSUMÉ", "-" * 40,
             f"  Total     : {len(resultats)}",
             f"  Obsolètes : {len(cats['OBSOLETE'])}",
             f"  Bientôt   : {len(cats['BIENTOT_EOL'])}",
             f"  Conformes : {len(cats['CONFORME']) + len(cats['ETENDU'])}",
             f"  Inconnus  : {len(cats['INCONNU'])}", ""]
    for code, titre in [("OBSOLETE", "OBSOLÈTES"), ("BIENTOT_EOL", "BIENTÔT EOL"),
                        ("CONFORME", "CONFORMES"), ("ETENDU", "SUPPORT ÉTENDU"), ("INCONNU", "INCONNUS")]:
        if cats[code]:
            lines += [titre, "-" * 40]
            lines += [f"  * {r['nom']} ({r['produit']} {r['version']}) — {r['statut_label']}" for r in cats[code]]
            lines.append("")
    lines += ["=" * 60, "Fin du rapport"]

    with open(f"docs/audit_eol_{ts}.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n{Fore.CYAN}{'─'*50}")
    print(f"  Rapport généré dans docs/audit_eol_{ts}.[json|txt]")
    print(f"  {Fore.RED}Obsolètes : {len(cats['OBSOLETE'])}  "
          f"{Fore.YELLOW}Bientôt EOL : {len(cats['BIENTOT_EOL'])}  "
          f"{Fore.GREEN}Conformes : {len(cats['CONFORME'])+len(cats['ETENDU'])}")
    print(f"{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")


# ─── CSV 

def traiter_fichier_csv(chemin_csv):
    resultats_affichage, resultats_bruts = [], []
    try:
        if not os.path.exists(chemin_csv):
            print(f"{Fore.RED}Fichier introuvable : {chemin_csv}")
            return []
        with open(chemin_csv, 'r', encoding='utf-8') as f:
            for ligne in csv.DictReader(f):
                nom, prod, ver = ligne.get('nom','Inconnu'), ligne.get('produit','windows'), ligne.get('version','10')
                eol = verifier_eol_api(prod, ver)
                code, label = classifier_statut(eol)
                resultats_affichage.append({"nom": nom, "statut": formater_resultat_eol(prod, ver, eol)})
                resultats_bruts.append({"nom": nom, "produit": prod, "version": ver,
                                        "eol_date": eol or "N/A", "statut_code": code, "statut_label": label})
        if resultats_bruts:
            generer_rapport(resultats_bruts)
        return resultats_affichage
    except Exception as e:
        print(f"{Fore.RED}Erreur CSV : {e}")
        return []