# 🚀 TubeStream Pro — Téléchargeur Vidéo Universel

> **Téléchargez des vidéos et de l'audio depuis 1000+ sites. Gratuit, rapide, sans inscription.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2024-orange.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Railway%20%7C%20Render%20%7C%20PythonAnywhere-brightgreen)](DEPLOY.md)

---

## ✨ Fonctionnalités

- 🌐 **1000+ sites supportés** — YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo, Dailymotion, Reddit, Twitch, SoundCloud et bien plus
- 📦 **Formats avec tailles exactes** — Affichage précis en Mo pour chaque qualité (144p à 8K)
- 🎵 **Extraction audio** — MP3 en 128kbps, 192kbps, 320kbps
- 📋 **Playlists** — Téléchargement de playlists complètes
- 🎨 **Interface moderne** — Design sombre professionnel avec animations
- 📱 **Responsive** — Fonctionne sur desktop, tablette et mobile
- 🔌 **API REST complète** — Intégration facile dans vos applications
- 🔍 **SEO optimisé** — Meta tags, sitemap, structured data, Open Graph

## 🚀 Démarrage rapide

### Installation

```bash
# Cloner le projet
git clone https://github.com/votre-user/tubestream.git
cd tubestream

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python app.py
```

### Utilisation

Ouvrez **http://localhost:5000** dans votre navigateur.

1. Collez l'URL de n'importe quelle vidéo
2. Cliquez sur **Analyser**
3. Choisissez le format et la qualité
4. Téléchargez !

## 📡 API REST

L'API complète est documentée sur **http://localhost:5000/api**.

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/info` | Métadonnées vidéo + formats |
| `POST` | `/api/v1/download` | Lancer un téléchargement |
| `GET` | `/api/v1/progress/{id}` | Suivre la progression |
| `GET` | `/api/v1/file/{id}/{name}` | Télécharger le fichier |
| `GET` | `/api/v1/sites` | Liste des sites supportés |

### Exemple d'utilisation

```bash
# Récupérer les formats d'une vidéo
curl -X POST http://localhost:5000/api/v1/info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

```python
import requests

# 1. Analyser
res = requests.post("http://localhost:5000/api/v1/info", json={
    "url": "https://youtube.com/watch?v=..."
})
info = res.json()

# 2. Télécharger
dl = requests.post("http://localhost:5000/api/v1/download", json={
    "url": "https://youtube.com/watch?v=...",
    "format_id": info["formats"]["combined"][0]["format_id"]
})

# 3. Suivre
session_id = dl.json()["session_id"]
progress = requests.get(f"http://localhost:5000/api/v1/progress/{session_id}")
print(progress.json())
```

## 🏗️ Structure du projet

```
tubestream/
├── app.py                 # Serveur Flask principal
├── downloader.py           # Moteur de téléchargement (yt-dlp)
├── config.py               # Configuration
├── requirements.txt        # Dépendances Python
├── Procfile                # Railway deployment
├── Dockerfile              # Docker / Railway / Render
├── nixpacks.toml           # Render deployment
├── pythonanywhere_wsgi.py  # PythonAnywhere
├── .gitignore
├── DEPLOY.md               # Guide de déploiement complet
├── README.md               # Ce fichier
├── templates/
│   ├── index.html          # Page principale (SEO)
│   ├── api_docs.html       # Documentation API
│   ├── 404.html            # Page d'erreur
│   └── 500.html            # Page d'erreur
└── downloads/              # Fichiers temporaires
```

## 🌐 Déploiement

### Railway (Recommandé)

```bash
railway init
railway up
```

### Render

Connectez votre repo GitHub à Render — le déploiement est automatique.

### PythonAnywhere

Voir [DEPLOY.md](DEPLOY.md) pour les instructions détaillées.

## ⚠️ Notes importantes

- **FFmpeg** est requis pour l'extraction audio MP3 (inclus dans Dockerfile)
- **YouTube** peut bloquer les IPs de datacenter — Railway est recommandé
- Les fichiers téléchargés sont **temporaires** et nettoyés automatiquement

## 📝 License

[MIT](LICENSE) — Utilisation libre et gratuite.

## 🤝 Contribuer

Les pull requests sont les bienvenues ! Pour les changements majeurs, ouvrez d'abord une issue.

---

<p align="center">
  <strong>TubeStream Pro</strong> — Téléchargez tout, depuis partout.
</p>
