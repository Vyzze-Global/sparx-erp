import uuid

from django.apps import apps
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from auth.models import EmployeeProfile


class Terminal(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    pin_code = models.CharField(max_length=6)
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(auto_now=True)

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class TerminalSettings(models.Model):
    terminal = models.OneToOneField(Terminal, on_delete=models.CASCADE)
    printer_ip = models.CharField(max_length=50, null=True, blank=True)
    printer_name = models.CharField(max_length=50, null=True, blank=True)
    printer_vendor_id = models.CharField(max_length=50, null=True, blank=True)
    printer_product_id = models.CharField(max_length=50, null=True, blank=True)
    printer_port = models.IntegerField(default=9100)
    auto_print_receipts = models.BooleanField(default=True)
    custom_footer_message = models.TextField(null=True, blank=True)
    tablet_mode = models.BooleanField(default=True)
    # pos_printer = models.CharField(max_length=50)


class CashRegister(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    # cashier = models.ForeignKey(Employee, on_delete=models.PROTECT)
    register_id = models.CharField(max_length=20, unique=True)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name='cash_registers')
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_open = models.BooleanField(default=True)  # Tracks whether this register is still open
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    denomination_5000 = models.PositiveIntegerField(default=0)  # 5000 currency
    denomination_1000 = models.PositiveIntegerField(default=0)  # 1000 currency
    denomination_500 = models.PositiveIntegerField(default=0)  # 500 currency
    denomination_100 = models.PositiveIntegerField(default=0)  # 100 currency
    denomination_50 = models.PositiveIntegerField(default=0)  # 50 currency
    denomination_20 = models.PositiveIntegerField(default=0)  # 20 currency
    denomination_10 = models.PositiveIntegerField(default=0)  # 10 currency
    denomination_5 = models.PositiveIntegerField(default=0)  # 5 currency
    denomination_1 = models.PositiveIntegerField(default=0)  # 1 currency

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['terminal'], condition=models.Q(is_open=True),
                                    name='unique_open_register_per_terminal')
        ]

    def __str__(self):
        return f"Terminal name - {self.terminal.name} - Is-open# - {self.is_open}"

    def close_register(self):
        # Calculate the closing balance based on denominations
        closing_balance = (
                (self.denomination_5000 * 5000) +
                (self.denomination_1000 * 1000) +
                (self.denomination_500 * 500) +
                (self.denomination_100 * 100) +
                (self.denomination_50 * 50) +
                (self.denomination_20 * 20) +
                (self.denomination_10 * 10) +
                (self.denomination_5 * 5) +
                (self.denomination_1 * 1)
        )

        # Adjust for sales, cash in, and cash out
        closing_balance += self.total_sales + self.total_cash_in - self.total_cash_out

        # Calculate cash balance based on cash payments in InvoicePayment
        # cash_payments = InvoicePayment.objects.filter(
        #     invoice__order__cash_register=self,
        #     payment_method='cash'
        # ).aggregate(total_cash=Sum('amount'))['total_cash'] or 0

        InvoicePayment = apps.get_model('billing', 'InvoicePayment')
        cash_payments = InvoicePayment.objects.filter(
            invoice__order__cash_register=self,
            payment_method='cash'
        ).aggregate(total_cash=Sum('amount'))['total_cash'] or 0

        self.cash_balance = self.opening_balance + cash_payments - self.total_cash_out

        # self.cash_balance = cash_payments - self.total_cash_out

        self.is_open = False
        self.closing_balance = closing_balance
        self.closed_at = timezone.now()
        self.save()

    def generate_x_report(self):
        # Summarize sales, payments, discounts, etc., for the current shift
        timestamp = timezone.now().strftime("%Y-%m-%d %I:%M %p")
        terminal = self.terminal.name
        opening_balance = self.opening_balance or 0
        opened_at = self.opened_at.strftime("%Y-%m-%d %I:%M %p")

        Order = apps.get_model('orders', 'Order')

        # Sales
        total_sales = Order.objects.filter(cash_register=self).aggregate(total=Sum('total'))['total'] or 0

        # Delivery Fees
        total_delivery_fees = Order.objects.filter(cash_register=self).aggregate(Sum('delivery_fee'))[
                                  'delivery_fee__sum'] or 0

        # Discounts
        total_coupon_discounts = Order.objects.filter(cash_register=self).aggregate(Sum('coupon_discount'))[
                                     'coupon_discount__sum'] or 0
        total_order_items_discount = Order.objects.filter(cash_register=self).aggregate(Sum('order_items_discount'))[
                                         'order_items_discount__sum'] or 0
        total_order_discounts = Order.objects.filter(cash_register=self).aggregate(Sum('order_discount'))[
                                    'order_discount__sum'] or 0
        total_discounts = Order.objects.filter(cash_register=self).aggregate(Sum('total_discount'))[
                              'total_discount__sum'] or 0

        # Cash In/Out
        total_cash_in = CashInOutRecord.objects.filter(register=self, transaction_type="IN").aggregate(Sum('amount'))[
                            'amount__sum'] or 0
        total_cash_out = CashInOutRecord.objects.filter(register=self, transaction_type="OUT").aggregate(Sum('amount'))[
                             'amount__sum'] or 0

        InvoicePayment = apps.get_model('billing', 'InvoicePayment')

        # Payments Breakdown
        total_by_cash = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self, payment_method='cash').aggregate(
                total_by_cash=Sum('amount'))['total_by_cash'] or 0

        total_by_card = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self, payment_method='card').aggregate(
                total_by_card=Sum('amount'))['total_by_card'] or 0

        total_by_bank_transfer = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self, payment_method='bank_transfer').aggregate(
                total_by_bank_transfer=Sum('amount'))['total_by_bank_transfer'] or 0

        total_by_online_payments = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self,
                                          payment_method='online_payment').aggregate(
                total_by_online_payments=Sum('amount'))['total_by_online_payments'] or 0

        total_by_cheque = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self, payment_method='cheque').aggregate(
                total_by_cheque=Sum('amount'))['total_by_cheque'] or 0

        total_by_cod = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self,
                                          payment_method='cash_on_delivery').aggregate(
                total_by_cod=Sum('amount'))['total_by_cod'] or 0

        total_by_qr_payments = \
            InvoicePayment.objects.filter(invoice__order__cash_register=self, payment_method='qr_payment').aggregate(
                total_by_qr_payments=Sum('amount'))['total_by_qr_payments'] or 0

        # total_wallet_points = InvoicePayment.objects.filter(use_wallet_points=True).aggregate(Sum('paid_total'))['paid_total__sum']

        # # Calculate cash in hand
        # self.closing_balance = (
        #     self.opening_balance
        #     + self.total_cash_in
        #     - self.total_cash_out
        #     + self.total_cash
        # )

        context = {'timestamp': timestamp, 'terminal': terminal, 'opened_at': opened_at,
                   'opening_balance': opening_balance, 'total_sales': total_sales, 'total_discounts': total_discounts,
                   'total_delivery_fees': total_delivery_fees, 'total_coupon_discounts': total_coupon_discounts,
                   'total_order_items_discount': total_order_items_discount,
                   'total_order_discounts': total_order_discounts, 'total_cash_in': total_cash_in,
                   'total_cash_out': total_cash_out, 'total_by_cash': total_by_cash, 'total_by_card': total_by_card,
                   'total_by_bank_transfer': total_by_bank_transfer,
                   'total_by_online_payments': total_by_online_payments, 'total_by_cod': total_by_cod,
                   'total_by_cheque': total_by_cheque, 'total_by_qr_payments': total_by_qr_payments}

        return context


class CashRegisterShift(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    cash_register = models.ForeignKey(CashRegister, on_delete=models.PROTECT)
    cashier = models.ForeignKey(EmployeeProfile, models.PROTECT)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cash_register', 'cashier'],
                condition=models.Q(is_active=True),
                name='unique_active_cash_register_cashier_shift'
            )
        ]

    def __str__(self):
        return f"{self.cash_register.terminal.name}: {self.is_active}"

    def end_shift(self):
        self.is_active = False
        self.check_out = timezone.now()  # Set the current date and time
        self.save()


class CashInOutRecord(models.Model):
    register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='cash_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=3, choices=[('IN', 'Cash In'), ('OUT', 'Cash Out')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.reference}"


class ShiftReport(models.Model):
    shift = models.ForeignKey(CashRegisterShift, on_delete=models.PROTECT)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cash in drawer at close

    # Sales breakdown
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_discounts = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_returns = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total amount refunded
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total tax collected
    total_vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total tax collected
    total_delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total delivery fees
    total_coupons = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total coupon discounts applied

    # Payment method breakdown
    total_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_online_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_qr_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_bank_transfer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_wallet_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # From customer wallet

    # Cash adjustments (cash in/out)
    total_cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    report_generated_at = models.DateTimeField(auto_now_add=True)
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()

    def generate_report(self):
        Order = apps.get_model('orders', 'Order')
        ReturnNote = apps.get_model('orders', 'ReturnNote')

        # Sum up various fields from related Orders, Returns, etc.
        self.total_sales = Order.objects.filter(order_status='completed').aggregate(Sum('total'))['total__sum']
        self.total_discounts = Order.objects.aggregate(Sum('total_discount'))['total_discount__sum']
        self.total_returns = ReturnNote.objects.aggregate(Sum('amount'))['amount__sum']
        self.total_tax = Order.objects.aggregate(Sum('sales_tax'))['sales_tax__sum']
        self.total_delivery_fees = Order.objects.aggregate(Sum('delivery_fee'))['delivery_fee__sum']
        self.total_coupons = Order.objects.aggregate(Sum('coupon_discount'))['coupon_discount__sum']
        # Additional calculations for payment methods
        self.total_cash = Order.objects.filter(payment_status='cash').aggregate(Sum('paid_total'))['paid_total__sum']
        self.total_card = Order.objects.filter(payment_status='card_payment').aggregate(Sum('paid_total'))[
            'paid_total__sum']
        self.total_online_payment = Order.objects.filter(payment_status='online_payment').aggregate(Sum('paid_total'))[
            'paid_total__sum']
        self.total_cheque = Order.objects.filter(payment_status='cheque').aggregate(Sum('paid_total'))[
            'paid_total__sum']
        self.total_wallet_points = Order.objects.filter(use_wallet_points=True).aggregate(Sum('paid_total'))[
            'paid_total__sum']

        # Calculate cash in hand
        self.closing_balance = (
                self.opening_balance
                + self.total_cash_in
                - self.total_cash_out
                + self.total_cash
        )

    def __str__(self):
        return f"Z Report - {self.terminal} - {self.shift_start} to {self.shift_end}"

# class ZReport(models.Model):
#     terminal = models.ForeignKey(Terminal, on_delete=models.PROTECT)
#     cashier = models.ForeignKey(Employee, on_delete=models.PROTECT)
#     opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cash in drawer at start
#     closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cash in drawer at close

#     # Sales breakdown
#     total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total sales for the day
#     total_discounts = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total discount applied
#     total_returns = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total amount refunded
#     total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total tax collected
#     total_vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total tax collected
#     total_delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total delivery fees
#     total_coupons = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total coupon discounts applied

#     # Payment method breakdown
#     total_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_online_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_qr_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_bank_transfer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_wallet_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # From customer wallet

#     # Cash adjustments (cash in/out)
#     total_cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # Cash Denomination Fields
#     denomination_5000 = models.PositiveIntegerField(default=0)  # 5000 currency
#     denomination_1000 = models.PositiveIntegerField(default=0)  # 1000 currency
#     denomination_500 = models.PositiveIntegerField(default=0)  # 500 currency
#     denomination_100 = models.PositiveIntegerField(default=0)  # 100 currency
#     denomination_50 = models.PositiveIntegerField(default=0)   # 50 currency
#     denomination_20 = models.PositiveIntegerField(default=0)   # 20 currency
#     denomination_10 = models.PositiveIntegerField(default=0)   # 10 currency
#     denomination_5 = models.PositiveIntegerField(default=0)    # 5 currency
#     denomination_1 = models.PositiveIntegerField(default=0)    # 1 currency

#     # Timestamps
#     report_generated_at = models.DateTimeField(auto_now_add=True)
#     shift_start = models.DateTimeField()
#     shift_end = models.DateTimeField()

#     def generate_report(self):
#         Order = apps.get_model('orders', 'Order')
#         ReturnNote = apps.get_model('orders', 'ReturnNote')

#         # Sum up various fields from related Orders, Returns, etc.
#         self.total_sales = Order.objects.filter(order_status='completed').aggregate(Sum('total'))['total__sum']
#         self.total_discounts = Order.objects.aggregate(Sum('discount'))['discount__sum']
#         self.total_returns = ReturnNote.objects.aggregate(Sum('amount'))['amount__sum']
#         self.total_tax = Order.objects.aggregate(Sum('sales_tax'))['sales_tax__sum']
#         self.total_delivery_fees = Order.objects.aggregate(Sum('delivery_fee'))['delivery_fee__sum']
#         self.total_coupons = Order.objects.aggregate(Sum('coupon_discount'))['coupon_discount__sum']
#         # Additional calculations for payment methods
#         self.total_cash = Order.objects.filter(payment_status='cash').aggregate(Sum('paid_total'))['paid_total__sum']
#         self.total_card = Order.objects.filter(payment_status='card_payment').aggregate(Sum('paid_total'))['paid_total__sum']
#         self.total_online_payment = Order.objects.filter(payment_status='online_payment').aggregate(Sum('paid_total'))['paid_total__sum']
#         self.total_cheque = Order.objects.filter(payment_status='cheque').aggregate(Sum('paid_total'))['paid_total__sum']
#         self.total_wallet_points = Order.objects.filter(use_wallet_points=True).aggregate(Sum('paid_total'))['paid_total__sum']

#         # Calculate cash in hand
#         self.closing_balance = (
#             self.opening_balance
#             + self.total_cash_in
#             - self.total_cash_out
#             + self.total_cash
#         )

#     def __str__(self):
#         return f"Z Report - {self.terminal} - {self.shift_start} to {self.shift_end}"

# phone_regex = RegexValidator(
#     regex=r'^\+?1?\d{9,15}$',
#     message="Phone number must be entered in the format: '+94719999999'. Up to 15 digits allowed."
# )
# class SalesPerson(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     profile_image = models.ImageField(upload_to='salespersons/', blank=True, null=True)
#     nic = models.CharField(max_length=20, blank=True, null=True)
#     joined_date = models.DateField(blank=True, null=True)
#     birthday = models.DateField(blank=True, null=True)
#     employee_code = models.CharField(max_length=20, unique=True)
#     commission_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission percentage")
#     total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     emp_code = models.CharField(max_length=100, blank=True, null=True)
#     tel_home = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
#     tel_office = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
#     notes = models.CharField(max_length=200, blank=True, null=True)
#     remarks = models.CharField(max_length=200, blank=True, null=True)
#     created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
#                                    related_name='employee_updated_by')
#     updated_at = models.DateTimeField(auto_now=True, null=True)

#     def add_sales(self, order_total):
#         self.total_sales += order_total
#         self.save()

#     def calculate_commission(self, order_total):
#         return order_total * (self.commission_rate / 100)

# class CustomerWallet(models.Model):
#     customer = models.OneToOneField('Customer', on_delete=models.CASCADE, related_name='wallet')
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def add_to_wallet(self, amount):
#         self.balance += amount
#         self.save()

#     def deduct_from_wallet(self, amount):
#         if self.balance >= amount:
#             self.balance -= amount
#             self.save()
#         else:
#             raise ValueError('Insufficient balance')

# class Warranty(models.Model):
#     product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='warranties')
#     warranty_period = models.PositiveIntegerField(help_text="Warranty period in months")
#     policy = models.TextField()

#     def is_valid(self, purchase_date):
#         warranty_end_date = purchase_date + relativedelta(months=self.warranty_period)
#         return timezone.now().date() <= warranty_end_date

# class WarrantyClaim(models.Model):
#     customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     purchase_date = models.DateField()
#     claim_date = models.DateTimeField(auto_now_add=True)
#     warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True)
#     issue_description = models.TextField()
#     is_resolved = models.BooleanField(default=False)

#     def resolve_claim(self):
#         self.is_resolved = True
#         self.save()


# # Loyalty App Models
# class LoyaltyProgram(models.Model):
#     name = models.CharField(max_length=255, default="Chandula Loyalty Program")
#     accrual_rate_store = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Points per rupee spent in store")
#     accrual_rate_online = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Points per rupee spent online")
#     redemption_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.01, help_text="Currency per point when redeeming")
#     points_expiry_months = models.IntegerField(default=12, help_text="Months before points expire")
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name

# class LoyaltyTier(models.Model):
#     program = models.OneToOneField(LoyaltyProgram, on_delete=models.PROTECT)
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     points_threshold = models.IntegerField(help_text="Points required to reach this tier")
#     multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Points multiplier for this tier")
#     badge_image = models.ImageField(upload_to='badges/', blank=True, null=True, help_text="Badge image awarded at this tier")
#     perks = models.JSONField(default=dict, help_text="Define perks for this tier, e.g., {'free_delivery': True}")

#     def __str__(self):
#         return f"{self.name} Tier"


# class Promotion(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     promotion_type = models.CharField(max_length=50, choices=[('Discount', 'Discount'), ('BonusPoints', 'Bonus Points')])
#     discount_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
#     bonus_points = models.IntegerField(null=True, blank=True)
#     # applicable_categories = models.ManyToManyField(Category, blank=True)
#     # applicable_products = models.ManyToManyField(Product, blank=True)
#     conditions = models.JSONField(default=dict, help_text="Define conditions like {'min_purchase': 100}")
#     max_usage_per_customer = models.IntegerField(default=1)

#     def __str__(self):
#         return self.name

#     def is_active(self):
#         return self.start_date <= timezone.now() <= self.end_date


# class LoyaltyTransaction(models.Model):
#     TRANSACTION_TYPES = [
#         ('Earn', 'Earn Points'),
#         ('Redeem', 'Redeem Points'),
#         ('Expire', 'Expired Points'),
#         ('Adjustment', 'Manual Adjustment'),
#     ]

#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_transactions')
#     transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
#     points = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_date = models.DateTimeField(auto_now_add=True, db_index=True)  # Indexed for better querying
#     related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
#     related_promotion = models.ForeignKey('Promotion', on_delete=models.SET_NULL, null=True, blank=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['customer', 'transaction_date']),
#         ]

#     def __str__(self):
#         return f"{self.customer} - {self.transaction_type} ({self.points} points)"

# class CustomerLoyaltyProfile(models.Model):
#     customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='loyalty_profile')
#     points_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     current_tier = models.ForeignKey(LoyaltyTier, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)  # Indexed
#     tier_acquired_date = models.DateField(null=True, blank=True)
#     total_points_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total_points_redeemed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total_points_expired = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     def add_points(self, points):
#         self.points_balance += points
#         self.total_points_earned += points
#         self.save()

#     def redeem_points(self, points):
#         if points > self.points_balance:
#             raise ValueError("Not enough points to redeem.")
#         self.points_balance -= points
#         self.total_points_redeemed += points
#         self.save()

#     def __str__(self):
#         return f"{self.customer} - {self.points_balance} points"


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
