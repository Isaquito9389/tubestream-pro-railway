# ============================================================
# 🚀 Guide de Déploiement — TubeStream Pro
# ============================================================

## 📁 Structure du projet

```
tubestream/
├── web_app.py              ← Serveur Flask principal (SEO + API REST)
├── downloader.py           ← Moteur de téléchargement (yt-dlp)
├── config.py               ← Configuration
├── requirements.txt        ← Dépendances Python
├── Procfile                ← Railway
├── Dockerfile              ← Railway / Render
├── nixpacks.toml           ← Render (ffmpeg)
├── pythonanywhere_wsgi.py  ← PythonAnywhere
├── .gitignore
├── templates/
│   ├── index.html          ← Page principale (SEO-optimisée)
│   ├── api_docs.html       ← Documentation API interactive
│   ├── 404.html            ← Page d'erreur 404
│   └── 500.html            ← Page d'erreur 500
├── static/                 ← Ressources statiques (si besoin)
└── downloads/              ← Fichiers temporaires (git-ignored)
```

## 🟢 Option 1 : Railway (Recommandé)

```bash
# 1. Installer Railway CLI
npm i -g @railway/cli

# 2. Se connecter
railway login

# 3. Initialiser le projet
railway init

# 4. Lier au repo
railway link

# 5. Déployer
railway up
```

Railway détecte automatiquement le `Dockerfile` et `Procfile`.
Variables d'environnement configurées dans `Dockerfile`.

## 🔴 Option 2 : Render

```bash
# 1. Créer un "Web Service" sur render.com
# 2. Connecter le repo GitHub
# 3. Build Command: pip install -r requirements.txt
# 4. Start Command: gunicorn web_app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 4

# OU utiliser nixpacks (automatique si fichier nixpacks.toml présent)
```

## 🟠 Option 3 : PythonAnywhere

```bash
# 1. Compte PythonAnywhere (payant requis pour yt-dlp)
# 2. Dashboard → Web → Add new web app
# 3. Flask → Python 3.10+
# 4. Source code: /home/[username]/tubestream
# 5. WSGI file: copier pythonanywhere_wsgi.py
# 6. pip install yt-dlp flask pillow werkzeug
# 7. Reload
```

## 🔧 Test local

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer
python web_app.py

# 3. Ouvrir http://localhost:5000
# 4. API Docs: http://localhost:5000/api
```

## 📊 Endpoints API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/info` | Récupérer métadonnées + formats avec tailles |
| POST | `/api/v1/formats` | Formats uniquement (léger) |
| POST | `/api/v1/download` | Lancer un téléchargement |
| GET | `/api/v1/progress/{id}` | Vérifier la progression |
| GET | `/api/v1/file/{id}/{name}` | Télécharger le fichier |
| GET | `/api/v1/sites` | Liste des sites supportés |
| POST | `/api/v1/cleanup/{id}` | Nettoyage session |

## ⚠️ Notes importantes

1. **YouTube bloque les IPs de datacenter** — Certains hébergeurs gratuits voient leurs IPs blacklistées. Solutions :
   - Utiliser Railway (moins bloqué)
   - Configurer des cookies YouTube via `--cookies`
   - Utiliser un proxy

2. **FFmpeg requis** pour l'extraction audio MP3 — Inclus dans Dockerfile/nixpacks.

3. **Stockage éphémère** — Sur Railway/Render, les fichiers sont supprimés au redéploiement.

4. **SEO optimisé** — Sitemap XML, robots.txt, meta tags, Open Graph, structured data JSON-LD, canonical URLs.
