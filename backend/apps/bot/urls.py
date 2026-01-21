from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BotConfigViewSet, BotTradeViewSet, BotPerformanceViewSet

router = DefaultRouter()
router.register(r'config', BotConfigViewSet, basename='bot-config')
router.register(r'trades', BotTradeViewSet, basename='bot-trade')
router.register(r'performance', BotPerformanceViewSet, basename='bot-performance')

urlpatterns = [
    path('', include(router.urls)),
]
