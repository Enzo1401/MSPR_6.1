@echo off
title NTL-SysToolbox - Gestionnaire d'Environnement
cls

echo ==================================================
echo       NTL-SYSTOOLBOX : PREPARATION DU LOGICIEL
echo ==================================================
echo.

:: 1. VERIFICATION / CREATION DU VENV
:: On utilise "py" qui est le lanceur standard Windows pour eviter les conflits
if not exist ".\venv" (
    echo [STEP 1/3] Creation de l'environnement virtuel...
    py -m venv venv
    if errorlevel 1 (
        echo [ERREUR] "py" non trouve, essai avec "python"...
        python -m venv venv
    )
    echo [##########          ] 33%% - VENV CREE
) else (
    echo [STEP 1/3] Environnement virtuel deja present.
    echo [##########          ] 33%% - SKIP
)

:: 2. MISE A JOUR DES DEPENDANCES
echo [STEP 2/3] Installation des modules (requirements.txt)...
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.\venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
echo [####################          ] 66%% - MODULES OK

:: 3. LANCEMENT
echo [STEP 3/3] Demarrage de l'application...
echo [##############################] 100%% - TERMINE !
echo.
echo ==================================================
echo   Lancement de la console NTL-SysToolbox...
echo ==================================================
timeout /t 2 >nul

:: On lance le main.py en utilisant le python du venv directement
.\venv\Scripts\python.exe main.py

pause