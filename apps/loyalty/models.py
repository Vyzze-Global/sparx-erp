import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from auth.models import CustomerProfile
from apps.orders.models import Order


class CustomerWallet(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def add_to_wallet(self, amount, remarks):
        WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='Credit', remarks=remarks)
        self.balance += amount
        self.save()

    def deduct_from_wallet(self, amount, remarks):
        if self.balance >= amount:
            WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='Debit', remarks=remarks)
            self.balance -= amount
            self.save()
        else:
            raise ValueError('Insufficient balance')

    def __str__(self):
        return f"{self.customer.userAccount.first_name} - {self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Credit', 'Credit to Wallet'),
        ('Debit', 'Debit from Wallet'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    wallet = models.ForeignKey(CustomerWallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.customer}"


# Loyalty Program and Tier Models
class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=255)
    accrual_rate_store = models.DecimalField(max_digits=5, decimal_places=4, default=0.005)
    accrual_rate_online = models.DecimalField(max_digits=5, decimal_places=4, default=0.01)
    redemption_rate = models.DecimalField(max_digits=5, decimal_places=4, default=1.00)
    register_bonus = models.DecimalField(max_digits=5, decimal_places=4, default=0.00)
    points_expiry_months = models.IntegerField(default=12)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LoyaltyTier(models.Model):
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.PROTECT, related_name='tiers')
    level = models.PositiveIntegerField(help_text="Indicates hierarchy of tiers")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    points_threshold = models.IntegerField()
    multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=0.001)
    badge_image = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        unique_together = ('program', 'level')

    def __str__(self):
        return f"{self.name} Tier"


class TierPerk(models.Model):
    PROMOTION_TYPES = [
        ('flat_discount', 'Flat Discount'),
        ('percentage_discount', 'Percentage Discount'),
        ('bonus_points', 'Bonus Points'),
    ]
    tier = models.ForeignKey(LoyaltyTier, on_delete=models.CASCADE, related_name='perks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    promotion_type = models.CharField(max_length=50, choices=PROMOTION_TYPES)
    flat_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bonus_points = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} perk for {self.tier.name}"


# Promotion and Condition Models
class Promotion(models.Model):
    PROMOTION_TYPES = [
        ('flat_discount', 'Flat Discount'),
        ('percentage_discount', 'Percentage Discount'),
        ('bonus_points', 'Bonus Points'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    promotion_type = models.CharField(max_length=50, choices=PROMOTION_TYPES)
    flat_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bonus_points = models.IntegerField(null=True, blank=True)
    max_usage_per_customer = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class PromotionCondition(models.Model):
    CONDITION_TYPES = [
        ('min_purchase', 'Minimum Purchase')
    ]
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.condition_type} of {self.value} for {self.promotion.name}"


# Loyalty Transactions and Customer Profile Models
class LoyaltyTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Earn', 'Earn Points'),
        ('Redeem', 'Redeem Points'),
        ('Expire', 'Expired Points'),
        ('Adjustment', 'Manual Adjustment'),
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=0.001)
    points = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='loyalty_transactions')
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    related_promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)
    related_tier_promotion = models.ForeignKey(TierPerk, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.customer} - {self.transaction_type} ({self.points} points)"


class CustomerLoyaltyProfile(models.Model):
    points_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tier_acquired_date = models.DateField(null=True, blank=True)
    total_points_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_points_redeemed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_points_expired = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='loyalty_profile')
    current_tier = models.ForeignKey(LoyaltyTier, on_delete=models.SET_NULL, null=True, blank=True)

    def get_points_value(self):
        return self.points_balance * self.current_tier.multiplier

    def redeem_points_by_value(self, value):
        if not self.current_tier:
            raise ValueError("Cannot redeem points without an assigned tier.")

        required_points = value / self.current_tier.multiplier
        if self.points_balance < required_points:
            raise ValueError("Insufficient points balance to redeem the specified value.")

        self.points_balance -= required_points
        self.total_points_redeemed += required_points
        self.save()
        return required_points

    # Calculate Points
    def calculate_points(self, amount, accrual_rate, multiplier=1.0):
        return amount * accrual_rate * multiplier

    # Earn Points on Orders
    def earn_points_from_order(self, order):
        loyalty_program = self.current_tier.program if self.current_tier else None

        if not loyalty_program or not loyalty_program.is_active:
            return  # No active loyalty program

        # Determine accrual rate based on order type (online/store)
        accrual_rate = (
            loyalty_program.accrual_rate_online if order.order_type == 'online'
            else loyalty_program.accrual_rate_store
        )

        # Calculate points with tier multiplier
        multiplier = self.current_tier.multiplier if self.current_tier else 1.0
        points = self.calculate_points(order.total, accrual_rate, multiplier)

        # Set expiry date for points
        expiry_date = timezone.now().date() + timedelta(days=loyalty_program.points_expiry_months * 30)

        # Add points and log transaction
        self.add_points(points, expiry_date=expiry_date, order=order)

    # # Redeem Points
    # def redeem_points_for_order(self, order):
    #     loyalty_program = self.current_tier.program if self.current_tier else None
    #     if not loyalty_program or not loyalty_program.is_active:
    #         raise ValueError("No active loyalty program for redemption.")

    #     # Calculate redeemable points based on order amount and redemption rate
    #     required_points = order.total_amount / loyalty_program.redemption_rate

    #     if required_points > self.points_balance:
    #         raise ValueError("Insufficient points for redemption.")

    #     # Deduct points and log transaction
    #     self.redeem_points(required_points)

    # Add Points Method
    def add_points(self, points, expiry_date=None, order=None):
        self.points_balance += points
        self.total_points_earned += points
        LoyaltyTransaction.objects.create(customer=self.customer, transaction_type='Earn', points=points, related_order=order,
                                          expiry_date=expiry_date)
        self.save()

    # Redeem Points Method
    def redeem_points(self, points):
        if points > self.points_balance:
            raise ValueError("Not enough points to redeem.")
        self.points_balance -= points
        self.total_points_redeemed += points
        LoyaltyTransaction.objects.create(customer=self.customer, transaction_type='Redeem', points=-points)
        self.save()

    def __str__(self):
        return f"{self.customer} - {self.points_balance} points"

# class LoyaltyTierHistory(models.Model):
#     profile = models.ForeignKey(CustomerLoyaltyProfile, on_delete=models.CASCADE, related_name='tier_history')
#     tier = models.ForeignKey(LoyaltyTier, on_delete=models.CASCADE)
#     acquired_date = models.DateField()
#     expiry_date = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.profile.customer} - {self.tier.name} Tier History"

# class Referral(models.Model):
#     referrer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='referrals_made')
#     referred_customer = models.OneToOneField('Customer', on_delete=models.CASCADE, related_name='referred_by')
#     referral_code = models.CharField(max_length=20, unique=True, db_index=True)
#     referrer_reward_points = models.IntegerField(default=0)
#     referred_reward_points = models.IntegerField(default=0)
#     is_successful = models.BooleanField(default=False)
#     referral_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Referral by {self.referrer} for {self.referred_customer}"
