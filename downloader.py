"""
TubeStream Pro — Downloader Universel (1000+ sites)
Supporte : YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo,
Dailymotion, Reddit, Twitch, SoundCloud, et 1000+ sites via yt-dlp.
"""
import yt_dlp
import os


class Downloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

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

    def get_info(self, url):
        """
        Fetch metadata and ALL available formats with exact file sizes.
        Works with 1000+ sites supported by yt-dlp.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 15,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)

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
                seen_video_res = {}  # Deduplicate by resolution

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

                    # Combined formats (video + audio in one file)
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

                    # Video-only formats
                    elif vcodec != 'none' and acodec == 'none':
                        if not height:
                            continue
                        res_key = f"{height}p"

                        # Keep best quality per resolution (prefer larger file or higher bitrate)
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

                    # Audio-only formats
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

                # Build deduplicated video formats list (sorted by resolution desc)
                video_formats = sorted(
                    [v for v in seen_video_res.values() if v.get('height')],
                    key=lambda x: x['height'],
                    reverse=True
                )

                # Remove internal _raw_size
                for v in video_formats:
                    v.pop('_raw_size', None)

                # Sort audio by bitrate desc
                audio_formats.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)

                # Deduplicate combined formats by resolution (keep best)
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

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                if 'This video is unavailable' in error_msg:
                    return {'error': 'This video is unavailable or has been removed'}
                elif 'Private video' in error_msg:
                    return {'error': 'This is a private video'}
                elif 'Sign in' in error_msg or 'login' in error_msg.lower():
                    return {'error': 'This content requires authentication'}
                elif 'blocked' in error_msg.lower() or 'restricted' in error_msg.lower():
                    return {'error': 'This content is restricted in your region'}
                return {'error': error_msg}

            except Exception as e:
                return {'error': f"Unexpected error: {str(e)}"}

    def download(self, url, format_id=None, options=None, progress_callback=None):
        """Download with specific format ID."""
        opts = {
            'outtmpl': f'{self.download_path}/%(title)s_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
        }

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

                # For merged formats, find the actual output file
                filename = ydl.prepare_filename(result)

                # Check if file exists (might have been merged)
                if os.path.exists(filename):
                    filepath = filename
                else:
                    # Try common extensions
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
