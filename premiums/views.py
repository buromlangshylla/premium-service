import requests
from decouple import config
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import PremiumQuote, PremiumFactor, PremiumHistory
from .serializers import PremiumQuoteSerializer, PremiumFactorSerializer, PremiumHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend

POLICY_SERVICE_URL = config("POLICY_SERVICE_URL", default="http://localhost:8001")
CUSTOMER_SERVICE_URL = config("CUSTOMER_SERVICE_URL", default="http://localhost:8002")
COVERAGE_SERVICE_URL = config("COVERAGE_SERVICE_URL", default="http://localhost:8003")
GEO_SERVICE_URL = config("GEO_SERVICE_URL", default="http://localhost:8004")


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
        customer_id = request.data.get("customer_id")
        policy_id = request.data.get("policy_id")

        if not customer_id or not policy_id:
            return Response({"error": "customer_id and policy_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Policy Service → base premium
            policy_resp = requests.get(f"{POLICY_SERVICE_URL}/policies/{policy_id}/")
            policy_data = policy_resp.json()
            base_premium = float(policy_data.get("premium_amount", 1000))

            # 2. Coverage Service → add-ons
            coverages_resp = requests.get(f"{COVERAGE_SERVICE_URL}/customers/{customer_id}/coverages")
            coverages_data = coverages_resp.json()
            addon_premium = sum(float(cov.get("premium", 0)) for cov in coverages_data)

            # 3. Customer Service → risk profile
            customer_resp = requests.get(f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/")
            customer_data = customer_resp.json()
            risk_score = float(customer_data.get("risk_score", 0))
            age_factor = 0

            if customer_data.get("dob"):
                from datetime import date, datetime
                dob = datetime.strptime(customer_data["dob"], "%Y-%m-%d").date()
                age = (date.today() - dob).days // 365
                if age > 50:
                    age_factor = base_premium * 0.2  # 20% extra

            # 4. Geo Service → region risk
            geo_resp = requests.get(f"{GEO_SERVICE_URL}/customers/{customer_id}/location-risk")
            geo_data = geo_resp.json()
            region_factor = float(geo_data.get("risk_score", 0))

            risk_adjustment = risk_score + age_factor + region_factor
            discount = 0  # TODO: add logic for discounts
            final_premium = base_premium + addon_premium + risk_adjustment - discount

            quote = PremiumQuote.objects.create(
                customer_id=customer_id,
                policy_id=policy_id,
                base_premium=base_premium,
                addon_premium=addon_premium,
                risk_adjustment=risk_adjustment,
                discount=discount,
                final_premium=final_premium,
                currency="INR",
                status="draft",
                calculated_at=timezone.now(),
            )

            # 7. Save PremiumFactors (breakdown)
            PremiumFactor.objects.create(
                premium_quote=quote,
                factor_type="base",
                description="Base Premium",
                amount=base_premium
            )
            PremiumFactor.objects.create(
                premium_quote=quote,
                factor_type="addon",
                description="Add-on Premium",
                amount=addon_premium
            )
            PremiumFactor.objects.create(
                premium_quote=quote,
                factor_type="customer_risk",
                description=f"Risk Score Adjustment ({risk_score}) + Age Factor ({age_factor})",
                amount=risk_score + age_factor
            )
            PremiumFactor.objects.create(
                premium_quote=quote,
                factor_type="geo_risk",
                description="Geo Risk Factor",
                amount=region_factor
            )

            serializer = PremiumQuoteSerializer(quote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
