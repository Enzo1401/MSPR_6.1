# MSPR_6.1
**1) CONTEXTE**
La Direction IT mandate votre équipe pour concevoir, développer et documenter NTL-SysToolbox, un
outil en ligne de commande qui industrialise les vérifications d’exploitation, sécurise la gestion des
sauvegardes de la base métier et produit un audit d’obsolescence. Le choix technologique est libre, à
condition que la solution soit exécutable sous Windows et Linux.

L’outil expose trois modules indépendants. Les sorties sont lisibles par un humain et disponibles en
format structuré (JSON, horodatées), avec codes de retour exploitables en supervision. 
La solution doit superviser le serveur Windows qui s'occupe du DHCP/DNS et le serveur de base de données.

Nous allons développer la solution en Python. 

**2) Struture du développement :**
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
