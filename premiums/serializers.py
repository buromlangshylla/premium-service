from rest_framework import serializers
from .models import PremiumQuote, PremiumFactor, PremiumHistory


class PremiumQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumQuote
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PremiumFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumFactor
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PremiumHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumHistory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

