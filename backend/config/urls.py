from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone


def status_view(_request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "quantum-capital-backend",
            "time": timezone.now().isoformat(),
        }
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status', status_view),
    path('api/auth/', include('apps.users.urls')),
]

