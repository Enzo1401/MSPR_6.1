# MSPR_6.1

**1) CONTEXTE** :

La Direction IT mandate votre équipe pour concevoir, développer et documenter NTL-SysToolbox, un
outil en ligne de commande qui industrialise les vérifications d’exploitation, sécurise la gestion des
sauvegardes de la base métier et produit un audit d’obsolescence. Le choix technologique est libre, à
condition que la solution soit exécutable sous Windows et Linux.

L’outil expose trois modules indépendants. Les sorties sont lisibles par un humain et disponibles en
format structuré (JSON, horodatées), avec codes de retour exploitables en supervision. 
La solution doit superviser le serveur Windows qui s'occupe du DHCP/DNS et le serveur de base de données.

Nous allons développer la solution en Python. 

**2) Structure du développement :**
- On développe la solution sur la branche **dev** puis on réalise une pull request sur GitHub (Explication des fonctionnalités ajoutées). Une fois approuvé, on fera des test sur la branche **test**. Enfin, une fois validé par l'ensemble de l'équipe, on pourra merger la pull request sur la branche principale.
- Merci de respecter ces étapes pour le bon déroulement du projet.

**3) Pour cloner le projet votre projet sur VSCode :**
- git clone https://github.com/Enzo1401/MSPR_6.1.git ==> puis ouvrir le dossier du projet dans votre IDE

**4) Commandes utiles (CMD VSCODE):**
- git branch ==> voir les branches disponibles 
- git checkout nom_branche ==> pour changer de branche
- git status ==> voir le status des fichiers
- git add fichier.py ==> ajouter un fichier 
- git commit -m "Description rapide du commit" ==> faire le commit sur la branche
- git push -u origin dev ==> pousser le code sur la branche

---

### ⚠️ PRÉREQUIS À INSTALLER (AVANT DÉVELOPPEMENT)

Pour que le module de sauvegarde fonctionne (SQL et CSV), vous devez installer et configurer les outils suivants sur votre machine locale :

1. **Outils Système MySQL (mysqldump)** :
   - Téléchargez et installez [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) ou [MySQL Community Server](https://dev.mysql.com/downloads/installer/).
   - **Important** : Ajoutez le chemin du dossier `bin` (ex: `C:\Program Files\MySQL\MySQL Workbench 8.0\`) à votre variable d'environnement **PATH** de Windows.
   - **Vérification** : Tapez `mysqldump --version` dans un terminal. Si la commande n'est pas reconnue, le module de sauvegarde SQL ne fonctionnera pas.

2. **Connecteur Python MySQL** :
   - Pour l'exportation des tables en CSV, l'outil utilise la bibliothèque [mysql-connector-python](https://pypi.org/project/mysql-connector-python/).
   - **Installation** : Ce module est listé dans le fichier `requirements.txt`. Il s'installera automatiquement lors de l'étape d'initialisation de l'environnement virtuel.

---

---

**5) Initialisation et Lancement :**

Il existe deux façons de lancer l'outil après avoir récupéré le repo :

### **A. Méthode Automatique (Recommandée)**
Double-cliquez simplement sur le fichier à la racine du projet :
> `lancer_toolbox.bat`

Ce script s'occupe de **tout** : il crée l'environnement virtuel s'il est absent, installe ou met à jour les dépendances automatiquement, puis lance l'outil. C'est la méthode la plus rapide.

### **B. Méthode Manuelle (Pour le développement)**
Si vous préférez gérer votre environnement manuellement dans le terminal :

1. **Création de l'environnement virtuel** (à faire une seule fois) :
   `python -m venv venv`

2. **Activation de l'environnement virtuel** (à faire à chaque nouveau terminal avant d'exécuter le code) :
   `.\venv\Scripts\activate`

3. **Installation des dépendances** (à faire à la première installation ou si le fichier `requirements.txt` est modifié) :
   `pip install -r requirements.txt`

4. **Exécution de l'outil** :
   `python main.py`

