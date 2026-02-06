---
title: titre de ton projet
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# 🏥 File Health Check

**File Health Check** est une application interactive développée avec **Streamlit** permettant d'analyser instantanément la qualité et la santé de vos jeux de données (CSV ou Google Sheets). L'outil génère un diagnostic complet incluant la complétude, la détection de doublons et les corrélations entre variables.

##  Fonctionnalités

* **Importation Multi-source :** Chargement de fichiers CSV locaux ou connexion directe à Google Sheets.
* **Performance Optimisée :** Utilisation du moteur **PyArrow** et du **Caching Streamlit** pour un chargement ultra-rapide des gros fichiers (jusqu'à 200 Mo).
* **Diagnostic de Complétude :** Analyse détaillée des valeurs manquantes par colonne avec visualisation sous forme de tableau.
* **Détection d'Anomalies :** Identification automatique du nombre de doublons.
* **Analyse Statistique :** Génération d'une matrice de corrélation interactive pour comprendre les liens entre vos données.
* **Interface Personnalisée :** Design moderne avec thème adaptatif et barre latérale intuitive.

## 🛠️ Installation

### Prérequis

* Python 3.13.5
* Pip (gestionnaire de paquets Python)

### Installation locale

1. **Clonez le dépôt :**
```bash
git clone https://github.com/votre-utilisateur/file_health_check.git
cd file_health_check

```


2. **Installez les dépendances :**
```bash
pip install -r requirements.txt

```


3. **Lancez l'application :**
```bash
streamlit run app.py

```



## 🐳 Docker (Optionnel)

Si vous préférez utiliser Docker pour garantir un environnement stable :

```bash
# Construction de l'image
docker build -t file_health_check .

# Lancement du conteneur
docker run -p 8501:8501 file_health_check

```

## 📂 Structure du Projet

```text
├── .streamlit/          # Configuration du thème et du serveur(pour la modification de la taille limite du fichier par exemple)
│   └── config.toml      
├── app.py               # Code principal de l'application Streamlit
├── requirements.txt     # Liste des bibliothèques Python
├── Dockerfile           # Configuration pour le déploiement Docker
└── README.md            # Documentation du projet
