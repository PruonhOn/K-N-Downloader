import yt_dlp
import re


def get_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'YouTube'
    elif 'tiktok.com' in url:
        return 'TikTok'
    elif 'instagram.com' in url:
        return 'Instagram'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'Twitter/X'
    elif 'facebook.com' in url:
        return 'Facebook'
    elif 'vimeo.com' in url:
        return 'Vimeo'
    elif 'dailymotion.com' in url:
        return 'Dailymotion'
    return 'Unknown'


def format_duration(seconds):
    if not seconds:
        return 'Unknown'
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_filesize(bytes_val):
    if not bytes_val:
        return 'Unknown'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get available formats
            formats = info.get('formats', [])
            
            quality_options = []
            seen_heights = set()
            
            for f in formats:
                height = f.get('height')
                ext = f.get('ext', '')
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                
                if height and vcodec != 'none' and height not in seen_heights:
                    seen_heights.add(height)
                    label = f"{height}p"
                    if height >= 2160:
                        label = f"4K ({height}p)"
                    elif height >= 1440:
                        label = f"2K ({height}p)"
                    
                    quality_options.append({
                        'height': height,
                        'label': label,
                        'format_id': f.get('format_id', ''),
                        'filesize': format_filesize(f.get('filesize') or f.get('filesize_approx')),
                        'ext': ext,
                    })
            
            # Sort by quality descending
            quality_options.sort(key=lambda x: x['height'], reverse=True)
            
            # Deduplicate and add standard qualities if missing
            if not quality_options:
                quality_options = [
                    {'height': 1080, 'label': '1080p (Full HD)', 'format_id': 'best[height<=1080]', 'filesize': 'N/A', 'ext': 'mp4'},
                    {'height': 720, 'label': '720p (HD)', 'format_id': 'best[height<=720]', 'filesize': 'N/A', 'ext': 'mp4'},
                    {'height': 480, 'label': '480p', 'format_id': 'best[height<=480]', 'filesize': 'N/A', 'ext': 'mp4'},
                    {'height': 360, 'label': '360p', 'format_id': 'best[height<=360]', 'filesize': 'N/A', 'ext': 'mp4'},
                ]
            
            return {
                'success': True,
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration')),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': (info.get('description', '') or '')[:300],
                'platform': get_platform(url),
                'qualities': quality_options,
                'webpage_url': info.get('webpage_url', url),
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def download_video(url, quality_height, format_type, download_dir):
    import os
    
    os.makedirs(download_dir, exist_ok=True)
    output_path = os.path.join(str(download_dir), '%(title)s.%(ext)s')
    
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
    else:
        if quality_height:
            fmt = f'bestvideo[height<={quality_height}]+bestaudio/best[height<={quality_height}]/best'
        else:
            fmt = 'best'
        ydl_opts = {
            'format': fmt,
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': True,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            return {'success': True, 'filename': filename, 'title': info.get('title', 'video')}
    except Exception as e:
        return {'success': False, 'error': str(e)}
