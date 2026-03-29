#!/bin/bash

# ─────────────────────────────────────────────
#  NTL-SysToolbox — Lanceur Linux
#  Equivalent du lancer_toolbox.bat pour Ubuntu
# ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=================================================="
echo "   NTL-SysToolbox v1.0 - INDUSTRIALISATION"
echo "=================================================="
echo ""

# 1 — Création du venv si absent
if [ ! -d "venv" ]; then
    echo "[*] Création de l'environnement virtuel..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERREUR] Impossible de créer le venv. Vérifiez que python3-venv est installé."
        echo "         sudo apt install python3-venv"
        exit 1
    fi
    echo "[OK] Environnement virtuel créé."
fi

# 2 — Activation du venv
source venv/bin/activate

# 3 — Installation / mise à jour des dépendances
echo "[*] Vérification des dépendances..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de l'installation des dépendances."
    exit 1
fi
echo "[OK] Dépendances à jour."
echo ""

# 4 — Lancement de l'outil
python main.py