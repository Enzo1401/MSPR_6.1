@echo off
title NTL-SysToolbox - Installation et Lancement
cls

echo ======================================================
echo          GESTIONNAIRE NTL-SYSTOOLBOX
echo ======================================================
echo.

:: 1. Vérification du dossier venv
if not exist ".\venv" (
    echo [INFO] Environnement virtuel absent. Creation en cours...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERREUR] Python n'est pas installe sur cette machine ou n'est pas dans le PATH.
        pause
        exit
    )
    echo [OK] Environnement cree.
)

:: 2. Installation/Mise a jour des dependances
echo [INFO] Verification des dependances (requirements.txt)...
.\venv\Scripts\python.exe -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] L'installation des dependances a echoue. Verifiez votre connexion internet.
    pause
    exit
)
echo [OK] Dependances a jour.

:: 3. Lancement du programme
echo.
echo [LANCEMENT] Demarrage de l'outil...
echo.
.\venv\Scripts\python.exe main.py

echo.
echo ======================================================
echo Session terminee.
pause