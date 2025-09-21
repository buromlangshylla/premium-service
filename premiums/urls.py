from django.urls import path
from .views import (
    CalculatePremiumView,
    RetrievePremiumQuoteView,
    RecalculatePremiumView,
    PremiumQuoteFilterView,
    PremiumHistoryFilterView,
)

urlpatterns = [
    path('premium/calculate', CalculatePremiumView.as_view(), name='premium-calculate'),
    path('premium/<uuid:policy_id>', RetrievePremiumQuoteView.as_view(), name='premium-detail'),
    path('premium/recalculate', RecalculatePremiumView.as_view(), name='premium-recalculate'),
    path('premium/quotes', PremiumQuoteFilterView.as_view(), name='premium-quote-filter'),
    path('premium/history', PremiumHistoryFilterView.as_view(), name='premium-history-filter'),
]

