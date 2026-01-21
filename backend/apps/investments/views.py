from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
import csv
from io import StringIO
from .models import Investment, Allocation
from .serializers import InvestmentSerializer, AllocationSerializer


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def investment_list_view(request):
    """List user investments or create new investment"""
    user = request.user
    
    if request.method == 'GET':
        investments = Investment.objects.filter(user=user)
        serializer = InvestmentSerializer(investments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = InvestmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def investment_detail_view(request, investment_id):
    """Get or update investment"""
    user = request.user
    try:
        investment = Investment.objects.get(id=investment_id, user=user)
    except Investment.DoesNotExist:
        return Response({'detail': 'Investment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = InvestmentSerializer(investment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = InvestmentSerializer(investment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def allocation_list_view(request, investment_id):
    """List allocations for an investment"""
    user = request.user
    try:
        investment = Investment.objects.get(id=investment_id, user=user)
    except Investment.DoesNotExist:
        return Response({'detail': 'Investment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    allocations = Allocation.objects.filter(investment=investment)
    serializer = AllocationSerializer(allocations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
