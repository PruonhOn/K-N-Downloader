from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fetch/', views.fetch_info, name='fetch_info'),
    path('download/', views.download, name='download'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('history/delete/<int:pk>/', views.delete_history, name='delete_history'),
]
