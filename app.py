"""
TubeStream Pro — Application Web Complète
==========================================
🎯 Objectifs:
- Interface moderne et intelligente
- SEO optimisé pour ranker #1 sur Google
- API REST complète et documentée
- Support 1000+ sites via yt-dlp

🚀 Compatible: PythonAnywhere, Railway, Render
"""

import os
import re
import uuid
import json
import shutil
import threading
import urllib.request
import datetime
from flask import (
    Flask, render_template, request, jsonify,
    send_file, Response, redirect, url_for
)
from werkzeug.utils import secure_filename
from downloader import Downloader

# ============================================================
# Configuration
# ============================================================

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static',
    template_folder='templates'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tubestream-pro-secret-change-me')
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024 * 1024  # 3GB max

# Dossiers
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# SEO Configuration
SITE_NAME = 'TubeStream Pro'
SITE_URL = os.environ.get('SITE_URL', 'https://tubestream.app')
SITE_DESCRIPTION = 'Téléchargez gratuitement des vidéos et audio depuis YouTube, TikTok, Instagram, Twitter, Facebook et 1000+ sites. MP4, MP3, HD, 4K, 8K. Rapide et sans inscription.'
SITE_KEYWORDS = 'télécharger vidéo youtube, télécharger tiktok, downloader instagram, twitter video download, vimeo download, dailymotion, convertisseur vidéo, mp4, mp3, 1080p, 4K, 8K, gratuit, sans inscription'

# Session de téléchargement active
active_downloads = {}

# Liste des sites populaires (pour SEO et UX)
POPULAR_SITES = [
    {'name': 'YouTube', 'url': 'https://youtube.com', 'emoji': '🔴', 'count': '1M+ vidéos'},
    {'name': 'TikTok', 'url': 'https://tiktok.com', 'emoji': '🎵', 'count': '500K+ vidéos'},
    {'name': 'Instagram', 'url': 'https://instagram.com', 'emoji': '📸', 'count': '100K+ vidéos'},
    {'name': 'Twitter / X', 'url': 'https://x.com', 'emoji': '🐦', 'count': '200K+ vidéos'},
    {'name': 'Facebook', 'url': 'https://facebook.com', 'emoji': '📘', 'count': '300K+ vidéos'},
    {'name': 'Vimeo', 'url': 'https://vimeo.com', 'emoji': '🎥', 'count': '50K+ vidéos'},
    {'name': 'Dailymotion', 'url': 'https://dailymotion.com', 'emoji': '📺', 'count': '80K+ vidéos'},
    {'name': 'Reddit', 'url': 'https://reddit.com', 'emoji': '🤖', 'count': '150K+ vidéos'},
    {'name': 'Twitch', 'url': 'https://twitch.tv', 'emoji': '🎮', 'count': '10K+ streams'},
    {'name': 'SoundCloud', 'url': 'https://soundcloud.com', 'emoji': '🎶', 'count': '200K+ audio'},
    {'name': 'Pinterest', 'url': 'https://pinterest.com', 'emoji': '📌', 'count': '50K+ vidéos'},
    {'name': 'Tumblr', 'url': 'https://tumblr.com', 'emoji': '🎭', 'count': '30K+ vidéos'},
    {'name': 'LinkedIn', 'url': 'https://linkedin.com', 'emoji': '💼', 'count': '20K+ vidéos'},
    {'name': 'Snapchat', 'url': 'https://snapchat.com', 'emoji': '👻', 'count': '10K+ stories'},
    {'name': 'Bilibili', 'url': 'https://bilibili.com', 'emoji': '📺', 'count': '100K+ vidéos'},
    {'name': 'Odysee', 'url': 'https://odysee.com', 'emoji': '🍓', 'count': '50K+ vidéos'},
    {'name': 'Rumble', 'url': 'https://rumble.com', 'emoji': '🔊', 'count': '30K+ vidéos'},
    {'name': 'Bandcamp', 'url': 'https://bandcamp.com', 'emoji': '🎸', 'count': '100K+ audio'},
    {'name': 'Mixcloud', 'url': 'https://mixcloud.com', 'emoji': '🎧', 'count': '50K+ mixes'},
    {'name': 'Spotify', 'url': 'https://spotify.com', 'emoji': '🟢', 'count': '100M+ titres'},
    {'name': 'Deezer', 'url': 'https://deezer.com', 'emoji': '🔵', 'count': '90M+ titres'},
    {'name': 'TED', 'url': 'https://ted.com', 'emoji': '💡', 'count': '4K+ talks'},
    {'name': 'Kickstarter', 'url': 'https://kickstarter.com', 'emoji': '🚀', 'count': '5K+ projets'},
    {'name': 'Youku', 'url': 'https://youku.com', 'emoji': '🔵', 'count': '500K+ vidéos'},
    {'name': 'Niconico', 'url': 'https://nicovideo.jp', 'emoji': '🇯🇵', 'count': '100K+ vidéos'},
    {'name': 'PeerTube', 'url': 'https://peertube.tv', 'emoji': '🌐', 'count': '100K+ vidéos'},
    {'name': 'Imgur', 'url': 'https://imgur.com', 'emoji': '🖼️', 'count': '50K+ GIFs'},
    {'name': 'Streamable', 'url': 'https://streamable.com', 'emoji': '📹', 'count': '10K+ vidéos'},
    {'name': 'VLive', 'url': 'https://vlive.tv', 'emoji': '🇰🇷', 'count': '20K+ lives'},
    {'name': 'Naver', 'url': 'https://naver.com', 'emoji': '🇰🇷', 'count': '100K+ vidéos'},
]

ALL_SITES_COUNT = 1000  # yt-dlp supports 1000+ extractors


# ============================================================
# Helpers
# ============================================================

def get_downloader(session_id):
    """Crée une instance Downloader pour une session."""
    session_dir = os.path.join(DOWNLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return Downloader(download_path=session_dir)


def is_valid_url(url):
    """Validation basique d'URL."""
    return bool(re.match(r'^https?://', url))


# ============================================================
# Pages Principales (SEO)
# ============================================================

@app.route('/')
def index():
    """Page d'accueil optimisée SEO."""
    return render_template(
        'index.html',
        site_name=SITE_NAME,
        site_desc=SITE_DESCRIPTION,
        site_url=SITE_URL,
        popular_sites=POPULAR_SITES,
        all_sites_count=ALL_SITES_COUNT
    )


@app.route('/api')
def api_docs():
    """Documentation interactive de l'API REST."""
    return render_template(
        'api_docs.html',
        site_name=SITE_NAME,
        site_desc=SITE_DESCRIPTION,
        site_url=SITE_URL
    )


@app.route('/screenshot')
def screenshot_tool():
    """Outil de capture d'écran de page web (bonus SEO)."""
    return render_template('screenshot.html', site_name=SITE_NAME)


# ============================================================
# SEO Files
# ============================================================

@app.route('/sitemap.xml')
def sitemap():
    """Sitemap XML pour Google."""
    today = datetime.date.today().isoformat()
    sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE_URL}/api</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{SITE_URL}/screenshot</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <!-- Pages pour chaque site populaire -->
  {"  ".join(f"""
  <url>
    <loc>{SITE_URL}/telecharger-{site["name"].lower().replace(" ", "-").replace("/", "-")}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""" for site in POPULAR_SITES)}
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    """Fichier robots.txt pour les crawlers."""
    robots_txt = f'''User-agent: *
Allow: /
Allow: /api
Allow: /sitemap.xml
Disallow: /downloads/
Disallow: /api/download
Disallow: /api/progress/
Disallow: /api/cleanup/
Disallow: /api/file/
Disallow: /static/

Sitemap: {SITE_URL}/sitemap.xml

User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 2
'''
    return Response(robots_txt, mimetype='text/plain')


@app.route('/.well-known/security.txt')
def security_txt():
    """Politique de sécurité pour les chercheurs."""
    return Response(
        "Contact: mailto:security@tubestream.app\n"
        "Preferred-Languages: en, fr\n"
        "Policy: https://tubestream.app/privacy\n",
        mimetype='text/plain'
    )


@app.route('/ads.txt')
def ads_txt():
    """Fichier ads.txt pour la monétisation."""
    return Response("", mimetype='text/plain')


# ============================================================
# Pages spécifiques par site (SEO Long-tail)
# ============================================================

@app.route('/telecharger-<site_name>')
def download_page(site_name):
    """Page dédiée par site pour le SEO long-tail."""
    site = next((s for s in POPULAR_SITES if s['name'].lower().replace(' ', '-') == site_name), None)
    if not site:
        return redirect('/', 301)

    return render_template(
        'site_page.html',
        site=site,
        site_name=SITE_NAME,
        site_desc=f"Téléchargez des vidéos {site['name']} gratuitement en MP4 et MP3.",
        site_url=SITE_URL
    )


# ============================================================
# REST API v1
# ============================================================

@app.route('/api/v1/info', methods=['POST'])
def api_v1_info():
    """
    Récupère les métadonnées complètes d'une vidéo.

    Requête:
        {
            "url": "https://youtube.com/watch?v=..."
        }

    Réponse:
        {
            "id": "...",
            "title": "...",
            "type": "video|playlist",
            "duration": 300,
            "duration_formatted": "5:00",
            "thumbnail": "...",
            "uploader": "...",
            "view_count": 1000000,
            "formats": {
                "combined": [{"format_id": "22", "resolution": "720p", "ext": "mp4", "size_mb": 25.3, ...}],
                "video": [...],
                "audio": [...]
            },
            "format_count": 15,
            "audio_count": 3
        }
    """
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL est requise', 'code': 400}), 400

    if not is_valid_url(url):
        return jsonify({'error': 'URL invalide. Doit commencer par http:// ou https://', 'code': 400}), 400

    dl = get_downloader('api-temp')
    info = dl.get_info(url)

    if 'error' in info:
        return jsonify({'error': info['error'], 'code': 422}), 422

    return jsonify(info)


@app.route('/api/v1/formats', methods=['POST'])
def api_v1_formats():
    """
    Récupère uniquement les formats disponibles (réponse légère).

    Requête:
        {"url": "https://youtube.com/watch?v=..."}
    """
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL est requise', 'code': 400}), 400

    dl = get_downloader('api-temp')
    info = dl.get_info(url)

    if 'error' in info:
        return jsonify({'error': info['error'], 'code': 422}), 422

    return jsonify({
        'formats': info.get('formats', {}),
        'format_count': info.get('format_count', 0),
        'audio_count': info.get('audio_count', 0),
    })


@app.route('/api/v1/download', methods=['POST'])
def api_v1_download():
    """
    Lance un téléchargement avec un format spécifique.

    Requête:
        {
            "url": "https://youtube.com/watch?v=...",
            "format_id": "22"  // optionnel, utilise le meilleur si absent
        }

    Réponse:
        {
            "session_id": "abc123",
            "status": "started",
            "progress_url": "/api/v1/progress/abc123"
        }
    """
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    format_id = data.get('format_id')

    if not url:
        return jsonify({'error': 'URL est requise', 'code': 400}), 400

    session_id = str(uuid.uuid4())[:8]
    dl = get_downloader(session_id)

    active_downloads[session_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initialisation...',
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    def run_download():
        try:
            def progress_cb(d):
                if d['status'] == 'downloading':
                    active_downloads[session_id] = {
                        'status': 'downloading',
                        'progress': d.get('percent', 0),
                        'speed': d.get('speed', 'N/A'),
                        'eta': d.get('eta', 'N/A'),
                        'total_mb': d.get('total_mb'),
                        'downloaded_mb': d.get('downloaded_mb'),
                        'message': f'Téléchargement... {d.get("percent", 0):.1f}%',
                    }
                elif d['status'] == 'finished':
                    active_downloads[session_id] = {
                        'status': 'finished',
                        'progress': 100,
                        'message': 'Traitement final...',
                    }

            result = dl.download(url, format_id=format_id, progress_callback=progress_cb)

            if result['status'] == 'success':
                filename = os.path.basename(result['filename'])
                filepath = result.get('filepath', os.path.join(DOWNLOAD_DIR, session_id, filename))
                file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                size_mb = round(file_size / (1024 * 1024), 1) if file_size else None

                active_downloads[session_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Téléchargement terminé !',
                    'filename': filename,
                    'size_mb': size_mb,
                    'download_url': f'/api/v1/file/{session_id}/{filename}',
                    'completed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
            else:
                active_downloads[session_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': result.get('message', 'Erreur inconnue'),
                }
        except Exception as e:
            active_downloads[session_id] = {
                'status': 'error',
                'progress': 0,
                'message': str(e),
            }

    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()

    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'progress_url': f'/api/v1/progress/{session_id}',
    })


@app.route('/api/v1/progress/<session_id>')
def api_v1_progress(session_id):
    """
    Vérifie la progression d'un téléchargement.

    Réponse (en cours):
        {
            "status": "downloading",
            "progress": 45.2,
            "speed": "2.5 MiB/s",
            "eta": "1:30",
            "total_mb": 25.3,
            "downloaded_mb": 11.4
        }

    Réponse (terminé):
        {
            "status": "completed",
            "progress": 100,
            "filename": "video.mp4",
            "size_mb": 24.8,
            "download_url": "/api/v1/file/abc123/video.mp4"
        }
    """
    if session_id not in active_downloads:
        return jsonify({'error': 'Session introuvable', 'code': 404}), 404

    data = active_downloads[session_id].copy()

    # Ajouter l'URL de téléchargement si terminé
    if data['status'] == 'completed' and 'download_url' not in data:
        filename = os.path.basename(data.get('filename', ''))
        data['download_url'] = f'/api/v1/file/{session_id}/{filename}'

    return jsonify(data)


@app.route('/api/v1/file/<session_id>/<filename>')
def api_v1_download_file(session_id, filename):
    """Télécharge le fichier résultant."""
    safe_name = secure_filename(filename)
    file_path = os.path.join(DOWNLOAD_DIR, session_id, safe_name)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Fichier introuvable', 'code': 404}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=safe_name,
        max_age=0,
    )


@app.route('/api/v1/cleanup/<session_id>', methods=['POST'])
def api_v1_cleanup(session_id):
    """Nettoie les fichiers d'une session."""
    session_dir = os.path.join(DOWNLOAD_DIR, session_id)
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
    active_downloads.pop(session_id, None)
    return jsonify({'status': 'nettoyé'})


@app.route('/api/v1/sites')
def api_v1_sites():
    """
    Liste tous les sites supportés.

    Réponse:
        {
            "total": 1000,
            "popular": [...],
            "all": [...]
        }
    """
    import yt_dlp
    extractors = yt_dlp.extractor.gen_extractors()
    all_sites = sorted(list(set(
        ex.IE_NAME for ex in extractors if ex.IE_NAME and ex.IE_NAME != 'generic'
    )))

    return jsonify({
        'total': len(all_sites),
        'popular': [{'name': s['name'], 'url': s['url'], 'emoji': s['emoji']} for s in POPULAR_SITES],
        'all': all_sites,
    })


# ============================================================
# Proxy Thumbnail (CORS bypass)
# ============================================================

@app.route('/api/thumbnail')
def api_thumbnail():
    """Proxy pour les thumbnails YouTube (évite les problèmes CORS)."""
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            return Response(data, mimetype=content_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================================
# Health Check
# ============================================================

@app.route('/health')
def health():
    """Endpoint de vérification de santé."""
    return jsonify({
        'status': 'ok',
        'version': '2.0.0',
        'sites_supported': ALL_SITES_COUNT,
        'active_sessions': len(active_downloads),
        'uptime': 'running',
    })


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint introuvable', 'code': 404}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Erreur serveur interne', 'code': 500}), 500
    return render_template('500.html'), 500


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'Fichier trop volumineux (max 3GB)', 'code': 413}), 413


# ============================================================
# Run
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    print(f"""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║   🚀  TubeStream Pro v2.0.0              ║
    ║                                          ║
    ║   📖  Site:      http://0.0.0.0:{port}           ║
    ║   🔗  API Docs:  http://0.0.0.0:{port}/api        ║
    ║   📡  API Base:  http://0.0.0.0:{port}/api/v1/    ║
    ║   🏥  Health:    http://0.0.0.0:{port}/health      ║
    ║                                          ║
    ║   🌐  1000+ sites supportés              ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
