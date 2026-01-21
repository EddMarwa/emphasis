from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('user/', views.get_current_user_view, name='current-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

