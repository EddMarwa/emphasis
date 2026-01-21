from django.urls import path
from . import views

app_name = 'investments'

urlpatterns = [
    path('investments/', views.investment_list_view, name='investment-list'),
    path('investments/<int:investment_id>/', views.investment_detail_view, name='investment-detail'),
    path('investments/<int:investment_id>/allocations/', views.allocation_list_view, name='allocation-list'),
]
