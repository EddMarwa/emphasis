from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportingViewSet

router = DefaultRouter()
router.register(r'', ReportingViewSet, basename='reporting')

app_name = 'reports'

urlpatterns = [
    path('', include(router.urls)),
]
