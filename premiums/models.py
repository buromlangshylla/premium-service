from django.db import models
import uuid


class Base(models.Model):
    created_by = models.CharField(max_length=250, editable=False, null=True, blank=True)
    modified_by = models.CharField(max_length=250, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PremiumQuote(Base):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('recalculated', 'Recalculated'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()
    policy_id = models.UUIDField()
    base_premium = models.DecimalField(max_digits=12, decimal_places=2)
    addon_premium = models.DecimalField(max_digits=12, decimal_places=2)
    risk_adjustment = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2)
    final_premium = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    calculated_at = models.DateTimeField()

    def __str__(self):
        return f"PremiumQuote {self.id} ({self.status})"


class PremiumFactor(Base):
    FACTOR_TYPE_CHOICES = [
        ('base', 'Base'),
        ('addon', 'Addon'),
        ('customer_risk', 'Customer Risk'),
        ('geo_risk', 'Geo Risk'),
        ('discount', 'Discount'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    premium_quote = models.ForeignKey(PremiumQuote, on_delete=models.CASCADE, related_name='factors')
    factor_type = models.CharField(max_length=20, choices=FACTOR_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"PremiumFactor {self.factor_type} ({self.amount})"


class PremiumHistory(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_id = models.UUIDField()
    old_premium = models.DecimalField(max_digits=12, decimal_places=2)
    new_premium = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255)
    changed_at = models.DateTimeField()

    def __str__(self):
        return f"PremiumHistory {self.policy_id} ({self.changed_at})"
