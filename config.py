# ============================================================
# TubeStream Pro — Configuration de l'application
# ============================================================
import os

class Config:
    """Configuration globale."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tubestream-pro-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB max
    DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', 'downloads')
    PORT = int(os.environ.get('PORT', 5000))
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # SEO
    SITE_NAME = 'TubeStream Pro'
    SITE_URL = os.environ.get('SITE_URL', 'https://tubestream.app')
    SITE_DESCRIPTION = 'Téléchargez des vidéos de YouTube, TikTok, Instagram, Twitter et 1000+ sites. Gratuit, rapide, sans inscription.'
    SITE_KEYWORDS = 'télécharger vidéo youtube, télécharger tiktok, downloader instagram, twitter video download, vimeo download, dailymotion, convertisseur vidéo, mp4, mp3'
