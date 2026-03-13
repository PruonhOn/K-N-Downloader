# VortexDL — Video Downloader Web App

A full-featured Django video downloader with a sleek dark UI.

## Features
- Download videos from YouTube, TikTok, Instagram, Twitter, Vimeo, and 1000+ sites
- Quality selection from 144p to 8K
- MP4 video or MP3 audio extraction
- Video preview with thumbnail, duration, uploader info
- User registration & login with persistent profiles
- Download history per user
- Admin panel

## Quick Start

### 1. Install dependencies
```bash
pip install django yt-dlp pillow
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Create admin (optional)
```bash
python manage.py createsuperuser
```

### 4. Run the server
```bash
python manage.py runserver
```

Then open http://127.0.0.1:8000

## Project Structure
```
videodownloader/
├── core/
│   ├── models.py        # UserProfile, DownloadHistory
│   ├── views.py         # All views + download logic
│   ├── utils.py         # yt-dlp integration
│   ├── forms.py         # Auth + profile forms
│   ├── urls.py          # URL routing
│   └── admin.py         # Admin registration
├── templates/
│   └── core/
│       ├── base.html    # Nav, fonts, global CSS
│       ├── home.html    # Main downloader UI
│       ├── auth.html    # Login / Sign up
│       └── profile.html # Profile + history
├── videodownloader/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

## Notes
- For production: set DEBUG=False, change SECRET_KEY, configure ALLOWED_HOSTS
- Downloads are stored in the `downloads/` folder temporarily
- FFmpeg required for MP3 extraction and some video merging (install separately)

## Install FFmpeg (required for MP3 and best quality MP4)
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from https://ffmpeg.org/download.html
