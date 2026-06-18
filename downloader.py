"""
TubeStream Pro — Downloader Universel (1000+ sites)
====================================================
Supporte : YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo,
Dailymotion, Reddit, Twitch, SoundCloud, et 1000+ sites via yt-dlp.

Anti-authentication strategies (free, no user action required) :
  1. Multi-client YouTube extraction (android → ios → web)
     Android/iOS clients often bypass sign-in & age-verification walls
     that YouTube shows to datacenter IPs (Railway/Render).
  2. Realistic browser User-Agent + Accept-Language headers.
  3. Geo-bypass via X-Forwarded-For country guessing.
  4. Optional cookies file (admin-set via COOKIES_FILE env) for the
     hardest cases (private/age-restricted content).
"""

import os
import yt_dlp


# ============================================================
# Anti-bot / anti-auth configuration
# ============================================================

REALISTIC_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/131.0.0.0 Safari/537.36'
)

DEFAULT_HTTP_HEADERS = {
    'User-Agent': REALISTIC_USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

# Optional cookies file path (set by admin via Railway env var).
# Read DYNAMICALLY at each call so admin uploads take effect without restart.
COOKIES_FILE_ENV = 'COOKIES_FILE'


def _get_cookies_file():
    """Return current cookies file path (read dynamically)."""
    return os.environ.get(COOKIES_FILE_ENV, '')


def _youtube_extractor_args(client):
    """Build YouTube extractor args for a specific player client."""
    return {
        'youtube': {
            # client can be 'android', 'ios', 'web', 'tv_embedded', 'default'
            'player_client': [client, 'web'],
            # Skip webpage/configs fetch for speed; let yt-dlp use the
            # player response directly from the client API.
            'player_skip': ['configs'],
            # Sometimes YouTube returns "Sign in to confirm you're not a bot"
            # because of missing PO token. Skip that check.
            'skip': ['hls', 'dash'],
        }
    }


# Order matters: try clients most likely to bypass auth first
YOUTUBE_CLIENT_STRATEGIES = ['android', 'ios', 'tv_embedded', 'web']


class Downloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    @staticmethod
    def _bytes_to_mb(size_bytes):
        """Convert bytes to MB with 1 decimal precision."""
        if not size_bytes:
            return None
        return round(size_bytes / (1024 * 1024), 1)

    @staticmethod
    def _format_duration(seconds):
        """Format seconds to HH:MM:SS or M:SS."""
        if not seconds:
            return None
        try:
            seconds = int(seconds)
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if h > 0:
                return f"{h}:{m:02d}:{s:02d}"
            return f"{m}:{s:02d}"
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _is_youtube(url):
        """Detect YouTube URLs (incl. youtu.be, music.youtube.com, embed links)."""
        if not url:
            return False
        u = url.lower()
        return any(h in u for h in (
            'youtube.com', 'youtu.be', 'youtube-nocookie.com'
        ))

    @staticmethod
    def _is_auth_error(error_msg):
        """Detect whether an yt-dlp error is an authentication wall."""
        m = (error_msg or '').lower()
        markers = [
            'sign in',
            'login required',
            'authentication required',
            'confirm you',
            "you're not a bot",
            'not a bot',
            'age-restricted',
            'age restricted',
            'private video',
            'members-only',
            'members only',
            'requires authentication',
        ]
        return any(marker in m for marker in markers)

    @staticmethod
    def _humanize_error(error_msg):
        """Convert raw yt-dlp error into a friendly French message."""
        if not error_msg:
            return 'Erreur inconnue'
        m = error_msg.lower()
        if 'unavailable' in m or 'removed' in m:
            return 'Cette vidéo est indisponible ou a été supprimée'
        if 'private' in m:
            return 'Cette vidéo est privée'
        if 'age' in m and 'restrict' in m:
            return 'Vidéo soumise à limite d\'âge — réessayez, plusieurs stratégies sont tentées'
        if 'sign in' in m or 'login' in m or 'authentication' in m:
            return 'Authentification requise par la plateforme — essayez un autre lien ou configurez un fichier cookies'
        if 'not a bot' in m or 'confirm you' in m:
            return 'Détection anti-bot de YouTube — réessayez dans quelques minutes'
        if 'blocked' in m or 'restricted' in m or 'region' in m:
            return 'Contenu bloqué dans cette région'
        if 'unsupported url' in m:
            return 'URL non supportée par yt-dlp'
        if 'timeout' in m or 'timed out' in m:
            return 'Délai dépassé — réessayez'
        if 'network' in m or 'connection' in m:
            return 'Erreur réseau — réessayez'
        return error_msg

    def _base_opts(self):
        """Base yt-dlp options applied to every extraction/download."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 15,
            'retries': 5,
            'fragment_retries': 5,
            # Bypass geo-restriction by faking client country
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # Realistic browser headers
            'http_headers': DEFAULT_HTTP_HEADERS,
            # Don't try to use a player JS that requires sign-in
            'extractor_args': {},
        }
        # Optional cookies file (admin-set)
        cookies_file = _get_cookies_file()
        if cookies_file and os.path.exists(cookies_file):
            opts['cookiefile'] = cookies_file
        return opts

    def _opts_for(self, url, client=None):
        """Build opts adapted to the URL (with YouTube client strategy)."""
        opts = self._base_opts()
        if self._is_youtube(url):
            client = client or YOUTUBE_CLIENT_STRATEGIES[0]
            opts['extractor_args'] = _youtube_extractor_args(client)
        return opts

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def get_info(self, url):
        """
        Fetch metadata and ALL available formats with exact file sizes.
        Works with 1000+ sites supported by yt-dlp.

        For YouTube URLs, tries multiple player clients (android → ios →
        tv_embedded → web) to bypass authentication walls shown to
        datacenter IPs.
        """
        last_error = None
        tried_clients = []

        # For YouTube, try each client strategy in order
        if self._is_youtube(url):
            for client in YOUTUBE_CLIENT_STRATEGIES:
                tried_clients.append(client)
                opts = self._opts_for(url, client=client)
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                    if info:
                        result = self._build_info_response(url, info)
                        result['meta'] = {
                            'client_used': client,
                            'clients_tried': tried_clients,
                        }
                        return result
                except yt_dlp.utils.DownloadError as e:
                    last_error = str(e)
                    # If it's NOT an auth error, no point trying other clients
                    if not self._is_auth_error(last_error):
                        break
                    # Otherwise, try next client
                    continue
                except Exception as e:
                    last_error = str(e)
                    break

            # All strategies failed
            return {
                'error': self._humanize_error(last_error),
                'error_raw': last_error,
                'clients_tried': tried_clients,
                'hint': (
                    'YouTube exige une authentification pour ce contenu depuis '
                    'cette IP (datacenter Railway). Solutions : (1) réessayez '
                    'plus tard, (2) configurez un fichier cookies via la '
                    'variable COOKIES_FILE.'
                ),
            }

        # Non-YouTube: single attempt with realistic headers
        opts = self._opts_for(url)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info:
                return {'error': 'Impossible d\'extraire les métadonnées de cette URL'}
            return self._build_info_response(url, info)

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            return {
                'error': self._humanize_error(error_msg),
                'error_raw': error_msg,
                'hint': (
                    'Certains contenus (Instagram privé, TikTok avec connexion '
                    'requise, etc.) peuvent nécessiter un fichier cookies '
                    '(variable COOKIES_FILE).'
                ),
            }
        except Exception as e:
            return {'error': f'Erreur inattendue : {str(e)}'}

    def _build_info_response(self, url, info):
        """Convert yt-dlp info dict to the API response format."""
        if not info:
            return {'error': 'Unable to extract video info'}

        # Playlist detection
        if info.get('_type') == 'playlist':
            entries = [e for e in info.get('entries', []) if e]
            return {
                'id': info.get('id'),
                'title': info.get('title', 'Untitled Playlist'),
                'type': 'playlist',
                'video_count': len(entries),
                'uploader': info.get('uploader') or info.get('uploader_id'),
                'entries': entries[:50],
                'total_entries': len(entries),
                'formats': {'combined': [], 'video': [], 'audio': []},
                'format_count': 0,
                'audio_count': 0,
            }

        # Extract and organize formats
        combined_formats = []
        video_formats = []
        audio_formats = []
        seen_video_res = {}

        for f in info.get('formats', []):
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            filesize = f.get('filesize') or f.get('filesize_approx')
            height = f.get('height')
            width = f.get('width')
            ext = f.get('ext', 'mp4')
            format_id = f.get('format_id', '')
            fps = f.get('fps')
            abr = f.get('abr')
            vbr = f.get('vbr')
            tbr = f.get('tbr')
            size_mb = self._bytes_to_mb(filesize)
            format_note = f.get('format_note', '')

            if vcodec != 'none' and acodec != 'none':
                res_label = f"{height}p" if height else "Auto"
                combined_formats.append({
                    'format_id': format_id,
                    'resolution': res_label,
                    'height': height,
                    'width': width,
                    'ext': ext,
                    'size_mb': size_mb,
                    'fps': fps,
                    'quality': f"{res_label}{' (' + str(fps) + 'fps)' if fps else ''}",
                    'type': 'combined',
                    'format_note': format_note,
                    'acodec': acodec,
                    'vcodec': vcodec,
                    'abr': abr,
                    'vbr': vbr,
                    'tbr': tbr,
                })

            elif vcodec != 'none' and acodec == 'none':
                if not height:
                    continue
                res_key = f"{height}p"
                if res_key not in seen_video_res or (
                    filesize and (
                        not seen_video_res[res_key].get('size_mb') or
                        filesize > (seen_video_res[res_key].get('_raw_size') or 0)
                    )
                ):
                    seen_video_res[res_key] = {
                        'format_id': format_id,
                        'resolution': res_key,
                        'height': height,
                        'width': width,
                        'ext': ext,
                        'size_mb': size_mb,
                        'fps': fps,
                        'quality': f"{res_key}{' (' + str(fps) + 'fps)' if fps else ''}",
                        'type': 'video',
                        'format_note': format_note,
                        'vcodec': vcodec,
                        'abr': abr,
                        'vbr': vbr,
                        'tbr': tbr,
                        '_raw_size': filesize,
                    }

            elif acodec != 'none' and vcodec == 'none':
                audio_formats.append({
                    'format_id': format_id,
                    'ext': ext,
                    'size_mb': size_mb,
                    'abr': abr,
                    'quality': f"{abr}kbps {ext.upper()}" if abr else f"{ext.upper()}",
                    'type': 'audio',
                    'acodec': acodec,
                    'format_note': format_note,
                    'tbr': tbr,
                })

        video_formats = sorted(
            [v for v in seen_video_res.values() if v.get('height')],
            key=lambda x: x['height'],
            reverse=True
        )
        for v in video_formats:
            v.pop('_raw_size', None)

        audio_formats.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)

        seen_combined = {}
        for cf in combined_formats:
            res = cf.get('resolution')
            if res and res not in seen_combined:
                seen_combined[res] = cf
        combined_unique = sorted(
            list(seen_combined.values()),
            key=lambda x: x.get('height', 0),
            reverse=True
        )

        return {
            'id': info.get('id'),
            'title': info.get('title', 'Untitled'),
            'type': 'video',
            'duration': info.get('duration'),
            'duration_formatted': self._format_duration(info.get('duration')),
            'thumbnail': info.get('thumbnail'),
            'description': info.get('description', '')[:500] if info.get('description') else '',
            'uploader': info.get('uploader') or info.get('channel') or info.get('uploader_id'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'upload_date': info.get('upload_date'),
            'webpage_url': info.get('webpage_url', url),
            'extractor': info.get('extractor', 'unknown'),
            'extractor_key': info.get('extractor_key', ''),
            'formats': {
                'combined': combined_unique,
                'video': video_formats,
                'audio': audio_formats,
            },
            'format_count': len(video_formats) + len(combined_unique),
            'audio_count': len(audio_formats),
        }

    def download(self, url, format_id=None, options=None, progress_callback=None):
        """Download with specific format ID. Tries multiple YouTube clients."""
        last_error = None
        tried_clients = []

        # For YouTube, try each client strategy in order
        if self._is_youtube(url):
            for client in YOUTUBE_CLIENT_STRATEGIES:
                tried_clients.append(client)
                result = self._download_once(
                    url, format_id, options, progress_callback, client=client
                )
                if result['status'] == 'success':
                    result['meta'] = {
                        'client_used': client,
                        'clients_tried': tried_clients,
                    }
                    return result
                last_error = result.get('message', '')
                # If not an auth error, no point trying other clients
                if not self._is_auth_error(last_error):
                    break
                # Otherwise, try next client
                continue

            return {
                'status': 'error',
                'message': self._humanize_error(last_error),
                'message_raw': last_error,
                'clients_tried': tried_clients,
            }

        # Non-YouTube: single attempt
        return self._download_once(url, format_id, options, progress_callback)

    def _download_once(self, url, format_id, options, progress_callback, client=None):
        """Perform a single download attempt with given opts."""
        opts = self._opts_for(url, client=client)
        opts['outtmpl'] = f'{self.download_path}/%(title)s_%(id)s.%(ext)s'
        opts['socket_timeout'] = 30

        if format_id:
            opts['format'] = format_id
        else:
            opts['format'] = 'bestvideo+bestaudio/best'

        if options:
            opts.update(options)

        if progress_callback:
            def hook(d):
                if d['status'] == 'downloading':
                    p = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        percent = float(p)
                    except ValueError:
                        percent = 0.0
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    size_mb = self._bytes_to_mb(total_bytes) if total_bytes else None
                    downloaded_mb = self._bytes_to_mb(downloaded) if downloaded else None

                    progress_callback({
                        'status': 'downloading',
                        'percent': percent,
                        'speed': speed,
                        'eta': eta,
                        'filename': d.get('filename'),
                        'total_mb': size_mb,
                        'downloaded_mb': downloaded_mb,
                    })
                elif d['status'] == 'finished':
                    progress_callback({
                        'status': 'finished',
                        'filename': d.get('filename'),
                        'total_bytes': d.get('total_bytes'),
                    })

            opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    result = ydl.extract_info(url, download=True)
                except yt_dlp.utils.DownloadError as e:
                    return {'status': 'error', 'message': str(e)}

                if result is None:
                    return {'status': 'error', 'message': 'No content found'}

                filename = ydl.prepare_filename(result)

                if os.path.exists(filename):
                    filepath = filename
                else:
                    for ext in ['.mp4', '.mkv', '.webm', '.m4a', '.mp3', '.flac', '.ogg']:
                        base = os.path.splitext(filename)[0] + ext
                        if os.path.exists(base):
                            filepath = base
                            filename = base
                            break
                    else:
                        filepath = filename

                return {
                    'status': 'success',
                    'filename': filename,
                    'filepath': os.path.abspath(filepath),
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
