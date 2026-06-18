# ============================================================
# 🚀 Guide de Déploiement — TubeStream Pro
# ============================================================

## 📁 Structure du projet

```
tubestream/
├── app.py                  ← Serveur Flask principal (SEO + API REST)
├── downloader.py           ← Moteur de téléchargement (yt-dlp)
├── config.py               ← Configuration
├── requirements.txt        ← Dépendances Python
├── start.sh                ← Script de démarrage (résout $PORT à runtime)
├── Dockerfile              ← Railway (builder principal) / Render
├── railway.json            ← Configuration Railway explicite
├── nixpacks.toml           ← Fallback Nixpacks (Render / Railway sans Dockerfile)
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

> **Note importante** : il n'y a PAS de `Procfile`. Railway scanne
> statiquement le Procfile pour extraire le port, et ne sait pas
> interpréter les variables d'environnement — d'où l'erreur
> `'$PORT' is not a valid port number`. La résolution du port se fait
> dans `start.sh`, exécuté par le shell à runtime.

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

Railway détecte automatiquement le `Dockerfile` et exécute `start.sh`
qui résout la variable `PORT` injectée par Railway au démarrage du conteneur.

**NE PAS définir de variable `PORT` dans Railway** — elle est injectée
automatiquement par la plateforme.

Variables importantes (Railway → Variables) :

| Variable | Valeur | Commentaire |
|----------|--------|-------------|
| `SECRET_KEY` | une chaîne aléatoire | À définir en production |
| `SITE_URL` | `https://<ton-domaine>.up.railway.app` | Pour le SEO/sitemap |
| `ADMIN_TOKEN` | (optionnel) un secret long aléatoire | Active les endpoints admin `/api/v1/cookies` |
| `COOKIES_FILE` | (optionnel) `/app/cookies.txt` | Chemin où stocker le cookies.txt uploadé |

## 🍪 Cookies YouTube (optionnel, pour contenus bloqués)

Quand YouTube détecte une IP de datacenter (Railway), il peut exiger
une authentification. Le downloader essaie en premier les clients
`android → ios → tv_embedded → web` qui contournent la plupart des
murs d'auth. Pour les vidéos vraiment bloquées, tu peux uploader un
fichier cookies (format Netscape) :

1. **Sur ton navigateur** : installe l'extension "Get cookies.txt"
   (Chrome/Firefox), va sur youtube.com connecté, exporte les cookies.
2. **Active `ADMIN_TOKEN`** dans Railway → Variables (mets une valeur
   secrète longue et aléatoire).
3. **Upload via API** :

```bash
curl -X POST https://<ton-app>.up.railway.app/api/v1/cookies \
  -H "X-Admin-Token: <ton-admin-token>" \
  -F "file=@youtube_cookies.txt"
```

4. **Vérifie le statut** :

```bash
curl https://<ton-app>.up.railway.app/api/v1/cookies/status
# → {"configured": true, "size_bytes": 1234, ...}
```

5. **Pour supprimer** :

```bash
curl -X DELETE https://<ton-app>.up.railway.app/api/v1/cookies \
  -H "X-Admin-Token: <ton-admin-token>"
```

⚠️ **Note** : sur Railway sans volume persistant, le cookies.txt est
perdu à chaque redéploiement. Pour le rendre persistant, monte un
volume Railway et change `COOKIES_FILE` pour pointer vers ce volume.

Si tu rencontres `'$PORT' is not a valid port number` :
1. Vérifie qu'il n'y a pas de `Procfile` à la racine.
2. Vérifie que `Dockerfile` ne contient pas `EXPOSE $PORT`.
3. Vérifie que `railway.json` ne contient pas `startCommand` avec `$PORT`.

## 🔴 Option 2 : Render

```bash
# 1. Créer un "Web Service" sur render.com
# 2. Connecter le repo GitHub
# 3. Build Command: pip install -r requirements.txt
# 4. Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 4

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
python app.py

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
