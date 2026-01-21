from rest_framework import serializers
from .models import Investment, Allocation


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = ('id', 'name', 'percentage', 'amount', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class InvestmentSerializer(serializers.ModelSerializer):
    allocations = AllocationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Investment
        fields = ('id', 'amount', 'entry_date', 'status', 'allocations')
        read_only_fields = ('id', 'entry_date')
    
    def create(self, validated_data):
        user = self.context['request'].user
        investment = Investment.objects.create(user=user, **validated_data)
        
        # Create default allocation for new investment
        Allocation.objects.create(
            investment=investment,
            name='Active Trading',
            percentage=75,
            amount=investment.amount * 0.75
        )
        Allocation.objects.create(
            investment=investment,
            name='Reserved',
            percentage=25,
            amount=investment.amount * 0.25
        )
        
        return investment
