from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.conf import settings
import json
import os

from .models import UserProfile, DownloadHistory
from .forms import SignUpForm, LoginForm, ProfileForm
from .utils import get_video_info, download_video


def home(request):
    recent_downloads = []
    if request.user.is_authenticated:
        recent_downloads = DownloadHistory.objects.filter(user=request.user)[:5]
    return render(request, 'core/home.html', {'recent_downloads': recent_downloads})


def fetch_info(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
    except Exception:
        url = request.POST.get('url', '').strip()

    if not url:
        return JsonResponse({'success': False, 'error': 'Please provide a URL'}, status=400)

    try:
        info = get_video_info(url)
        return JsonResponse(info)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def download(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    url = data.get('url', '').strip()
    quality = str(data.get('quality', '1080')).strip()
    fmt = data.get('format', 'mp4').strip()
    title = data.get('title', 'video').strip()
    thumbnail = data.get('thumbnail', '').strip()
    platform = data.get('platform', '').strip()
    duration = data.get('duration', '').strip()

    if not url:
        return JsonResponse({'success': False, 'error': 'URL required'}, status=400)

    try:
        quality_height = int(quality) if quality.isdigit() else 1080
    except Exception:
        quality_height = 1080

    try:
        result = download_video(url, quality_height, fmt, settings.DOWNLOAD_DIR)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

    if result.get('success'):
        if request.user.is_authenticated:
            DownloadHistory.objects.create(
                user=request.user,
                url=url,
                title=title,
                thumbnail=thumbnail,
                platform=platform,
                quality=f"{quality}p" if quality.isdigit() else quality,
                format=fmt,
                duration=duration,
                status='completed'
            )
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.total_downloads += 1
            profile.save()

        filename = result.get('filename')
        if filename and os.path.exists(filename):
            return FileResponse(
                open(filename, 'rb'),
                as_attachment=True,
                filename=os.path.basename(filename)
            )

        return JsonResponse({
            'success': False,
            'error': 'File not found after download'
        }, status=404)

    return JsonResponse({
        'success': False,
        'error': result.get('error', 'Download failed')
    }, status=400)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'core/auth.html', {'form': form, 'mode': 'signup'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
    else:
        form = LoginForm()

    return render(request, 'core/auth.html', {'form': form, 'mode': 'login'})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    downloads = DownloadHistory.objects.filter(user=request.user)[:20]

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'core/profile.html', {
        'profile': profile,
        'downloads': downloads,
        'form': form,
    })


@login_required
def delete_history(request, pk):
    item = get_object_or_404(DownloadHistory, pk=pk, user=request.user)
    item.delete()
    return JsonResponse({'success': True})