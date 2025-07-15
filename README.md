# 🤖 Veille IA — Agent Automatisé

## 🎯 Objectif

Cet agent a été développé pour réaliser une **veille technologique automatisée** sur le thème de l'**intelligence artificielle**.  
Il collecte régulièrement des articles récents provenant de plusieurs sources fiables, évite les doublons grâce à Airtable et stocke les résultats dans un format structuré.

---

## 🚀 Fonctionnalités

- Collecte des articles récents une fois par jour à 09:00
- Multi‑sources (flux RSS spécialisés en français)
- Collecte de tous les articles sans filtrage par mots-clés
- Déduplication côté serveur grâce à Airtable
- Stockage structuré dans une base Airtable
- Checkpoints détaillés de suivi de la collecte

---

## 🧰 Technologies & Choix techniques

### Langage et environnement
- **Python 3** : langage simple et robuste, idéal pour prototyper un agent léger.
- Bibliothèques Python choisies :
  - `feedparser` pour lire les flux RSS.
  - `pyairtable` pour utiliser l'API REST d'Airtable.
  - `schedule` pour planifier des exécutions récurrentes.
  - `dotenv` pour gérer les variables sensibles.

### Backend de stockage
- **Airtable**, plus adapté que Google Sheets :
  - garantit un identifiant unique par enregistrement.
  - permet de filtrer côté serveur (`filterByFormula`) sans télécharger toutes les données.
  - plus scalable et structuré.

### Stratégie d'automatisation
- **Collecte quotidienne à 09:00** : Optimale pour une veille efficace sans surcharge
- Une première collecte est déclenchée immédiatement au lancement
- Mode manuel disponible (collecte unique sans planification)

**Justification de la fréquence quotidienne :**
- **Équilibre optimal** : Suffisant pour rester à jour sans surcharger les sources
- **Ressources économisées** : Moins de requêtes API et de traitement
- **Qualité des données** : Évite les doublons et articles de faible qualité
- **Horaire matinal** : Capture les articles de la veille et du matin
- **Maintenance simplifiée** : Moins de surveillance et d'interventions nécessaires

---

## 📋 Pré‑requis

- Un compte Airtable
- Une base Airtable avec une table
- Un token API Airtable et l'identifiant de la base (`base_id`)

---

## 📊 Format de données

**Format défini en amont pour la collecte :**

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `URL` | URL | Lien unique de l'article | `https://www.actuia.com/article-ia` |
| `Title` | Texte | Titre de l'article | `Nouveau virage stratégique pour Arlequin AI` |
| `Summary` | Texte long | Résumé de l'article | `La jeune deeptech parisienne annonce...` |
| `Source` | Texte | Nom de la source | `ActuIA` |
| `Published` | Date | Date de publication | `2024-01-15` |
| `Collected` | Date | Date de collecte | `2024-01-15` |

**Caractéristiques essentielles :**
- **Identifiant unique** : URL de l'article
- **Déduplication** : Basée sur l'URL
- **Format standard** : ISO pour les dates
- **Nettoyage** : HTML décodé automatiquement

---

## 🔷 Configuration Airtable

Créez une table dans votre base Airtable avec les colonnes suivantes :

| Nom de la colonne | Type Airtable | Propriétés |
|-------------------|---------------|------------|
| `URL` | URL | Unique, Required |
| `Title` | Single line text | - |
| `Summary` | Long text | - |
| `Source` | Single line text | - |
| `Published` | Date | - |
| `Collected` | Date | - |

---

## 🔧 Installation

### 1️⃣ Cloner le dépôt
```bash
git clone <votre_repo>
cd veille-ia
```

### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3️⃣ Configurer les variables d'environnement
Copiez le fichier `.env.example` vers `.env` et configurez vos variables :

```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos informations Airtable :
- `AIRTABLE_API_KEY` : Votre clé API Airtable (depuis https://airtable.com/account)
- `AIRTABLE_BASE_ID` : L'ID de votre base (visible dans l'URL d'Airtable)
- `AIRTABLE_TABLE_NAME` : Le nom de votre table

### 4️⃣ Configuration des flux RSS

Les flux RSS sont configurés dans le fichier `main.py` dans la variable `RSS_FEEDS`. Chaque flux est défini comme un objet avec :
- `name` : Nom lisible de la source (ex: "ActuIA", "Google News IA")
- `url` : URL du flux RSS

Exemple de configuration :
```python
RSS_FEEDS = [
    {
        "name": "Google News IA",
        "url": "https://news.google.com/rss/search?q=intelligence+artificielle&hl=fr&gl=FR&ceid=FR:fr"
    },
    {
        "name": "ActuIA",
        "url": "https://www.actuia.com/feed"
    },
    {
        "name": "Euronews IA",
        "url": "https://fr.euronews.com/rss?level=tag&name=intelligence-artificielle"
    }
]
```

---

## 🚀 Utilisation

### Mode manuel (collecte unique)
```bash
python main.py
```

### Mode automatique (collecte quotidienne)
L'agent s'exécute automatiquement tous les jours à 09:00 :
```python
schedule.every().day.at("09:00").do(fetch_and_store)
print(f"Agent en veille - prochaine collecte demain à 09:00...\n")
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Suivi de la collecte
L'agent affiche des checkpoints détaillés :
- Configuration chargée
- Progression par flux RSS
- Statistiques par source
- Résumé global de la collecte

**Exemple de sortie :**
```
[2024-01-15 09:00:00] Début de la collecte - 3 flux

[1/3] Google News IA
   Articles trouvés: 25
   Traités: 25 | Doublons: 10 | Ajoutés: 15

[2/3] ActuIA
   Articles trouvés: 8
   Traités: 8 | Doublons: 2 | Ajoutés: 6

[3/3] Euronews IA
   Articles trouvés: 12
   Traités: 12 | Doublons: 5 | Ajoutés: 7

[2024-01-15 09:02:15] Collecte terminée - 28 nouveaux articles ajoutés
```

---