from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
import json
import os
import threading

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
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
    except:
        url = request.POST.get('url', '').strip()
    
    if not url:
        return JsonResponse({'success': False, 'error': 'Please provide a URL'})
    
    info = get_video_info(url)
    return JsonResponse(info)


def download(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
    except:
        data = request.POST
    
    url = data.get('url', '').strip()
    quality = data.get('quality', '1080')
    fmt = data.get('format', 'mp4')
    title = data.get('title', 'video')
    thumbnail = data.get('thumbnail', '')
    platform = data.get('platform', '')
    duration = data.get('duration', '')
    
    if not url:
        return JsonResponse({'success': False, 'error': 'URL required'})
    
    try:
        quality_height = int(quality) if quality.isdigit() else 1080
    except:
        quality_height = 1080
    
    result = download_video(url, quality_height, fmt, settings.DOWNLOAD_DIR)
    
    if result['success']:
        # Save to history
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
        
        filename = result['filename']
        if os.path.exists(filename):
            response = FileResponse(open(filename, 'rb'), as_attachment=True,
                                    filename=os.path.basename(filename))
            return response
        else:
            return JsonResponse({'success': False, 'error': 'File not found after download'})
    
    return JsonResponse({'success': False, 'error': result.get('error', 'Download failed')})


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
