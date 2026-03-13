from django.contrib import admin
from .models import UserProfile, DownloadHistory

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_downloads', 'created_at')

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'format', 'quality', 'platform', 'downloaded_at')
    list_filter = ('format', 'platform', 'downloaded_at')
    search_fields = ('title', 'url')
