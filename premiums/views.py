from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import PremiumQuote, PremiumFactor, PremiumHistory
from .serializers import PremiumQuoteSerializer, PremiumFactorSerializer, PremiumHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend


class PremiumQuoteFilterView(generics.ListAPIView):
    queryset = PremiumQuote.objects.all()
    serializer_class = PremiumQuoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer_id', 'policy_id', 'status']


class PremiumHistoryFilterView(generics.ListAPIView):
    queryset = PremiumHistory.objects.all()
    serializer_class = PremiumHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['policy_id']


class CalculatePremiumView(APIView):
    def post(self, request):
        data = request.data
        # Example calculation logic
        quote = PremiumQuote.objects.create(
            customer_id=data['customer_id'],
            policy_id=data['policy_id'],
            base_premium=data.get('base_premium', 1000),
            addon_premium=data.get('addon_premium', 200),
            risk_adjustment=data.get('risk_adjustment', 50),
            discount=data.get('discount', 100),
            final_premium=1150,
            currency='INR',
            status='draft',
            calculated_at=timezone.now()
        )
        PremiumFactor.objects.create(
            premium_quote=quote,
            factor_type='base',
            description='Base premium',
            amount=quote.base_premium
        )
        serializer = PremiumQuoteSerializer(quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrievePremiumQuoteView(APIView):
    def get(self, request, policy_id):
        quote = PremiumQuote.objects.filter(policy_id=policy_id).order_by('-calculated_at').first()
        if not quote:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PremiumQuoteSerializer(quote)
        return Response(serializer.data)


class RecalculatePremiumView(APIView):
    def post(self, request):
        data = request.data
        policy_id = data['policy_id']
        old_quote = PremiumQuote.objects.filter(policy_id=policy_id).order_by('-calculated_at').first()
        new_premium = data.get('new_premium', 1200)
        quote = PremiumQuote.objects.create(
            customer_id=old_quote.customer_id,
            policy_id=policy_id,
            base_premium=old_quote.base_premium,
            addon_premium=old_quote.addon_premium,
            risk_adjustment=old_quote.risk_adjustment,
            discount=old_quote.discount,
            final_premium=new_premium,
            currency=old_quote.currency,
            status='recalculated',
            calculated_at=timezone.now()
        )
        PremiumHistory.objects.create(
            policy_id=policy_id,
            old_premium=old_quote.final_premium,
            new_premium=new_premium,
            reason=data.get('reason', 'Recalculation'),
            changed_at=timezone.now()
        )
        serializer = PremiumQuoteSerializer(quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
