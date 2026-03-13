from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    total_downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class DownloadHistory(models.Model):
    FORMAT_CHOICES = [('mp4', 'MP4'), ('mp3', 'MP3')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads', null=True, blank=True)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500)
    thumbnail = models.URLField(max_length=2000, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    quality = models.CharField(max_length=50)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='mp4')
    file_size = models.CharField(max_length=50, blank=True)
    duration = models.CharField(max_length=50, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"{self.title} - {self.format} {self.quality}"
