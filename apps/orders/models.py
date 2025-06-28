import decimal
import uuid
import random
import string
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from auth.models import CustomerProfile, EmployeeProfile
from apps.pos.models import CashRegister
from apps.products.models import Product, Batch, ProductVariation
from apps.systemconfig.models import DeliveryPartner, SelfDeliveryPartner

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+94719999999'. Up to 15 digits allowed."
)

def generate_short_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class Coupon(models.Model):
    COUPON_TYPE = [
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    type = models.CharField(max_length=50, choices=COUPON_TYPE)  # 'fixed', 'percentage', etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    minimum_cart_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    max_uses = models.PositiveIntegerField(blank=True, null=True)  # Optional maximum number of uses
    used_count = models.PositiveIntegerField(default=0)  # Track the number of times the discount has been used
    active_from = models.DateTimeField()
    expire_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    target = models.PositiveIntegerField(blank=True, null=True)
    is_approve = models.BooleanField(default=True)

    @property
    def is_expired(self) -> bool:
        now = timezone.now()
        return self.is_valid and self.expire_at >= now

    def is_cart_amount_ok(self, cart_amount: decimal) -> bool:
        return cart_amount >= self.minimum_cart_amount

    def __str__(self):
        return self.code


class Order(models.Model):
    ORDER_STATUS = [
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('quote', 'Quote'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('partially_refunded', 'Partially Refunded'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled')
        # Todo -> Failed status ???
    ]

    ORDER_TYPE = [
        ('store', 'Store'),
        ('online', 'Online')
    ]

    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('card_payment', 'Card Payment'),
        ('online_payment', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    COLLECTION_METHOD = [
        ('in_store', 'In Store'),
        ('store_pickup', 'Store Pickup'),
        ('delivery', 'Delivery')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    order_number = models.IntegerField(null=True, unique=True)
    customer_contact = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    delivery_time = models.CharField(max_length=50, blank=True, null=True)
    use_wallet_points = models.BooleanField(default=False, blank=True, null=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, blank=True, null=True, default='Request')
    payment_status = models.CharField(max_length=100, choices=PAYMENT_METHOD, blank=True, null=True) # Todo -> change field name
    order_type = models.CharField(max_length=100, choices=ORDER_TYPE, default='None')
    collection_method = models.CharField(max_length=100, choices=COLLECTION_METHOD, blank=True, null=True, default='None')
    note = models.CharField(max_length=150, blank=True, null=True)
    remarks = models.CharField(max_length=150, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    return_voucher_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    percentage_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    percentage_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    flat_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    return_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    paid_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    # discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # payment_gateway = models.CharField(max_length=100, default='en', blank=True, null=True)
    # sales_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # order_items_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    # order_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # cancelled_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # cancelled_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # cancelled_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    customer = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.PROTECT)
    sales_advisor = models.ForeignKey(EmployeeProfile, blank=True, null=True, on_delete=models.PROTECT)
    coupon = models.ForeignKey(Coupon, blank=True, null=True, on_delete=models.PROTECT)
    cash_register = models.ForeignKey(CashRegister, blank=True, null=True, on_delete=models.SET_NULL)
    return_voucher = models.ForeignKey('ReturnVoucher', on_delete=models.SET_NULL, null=True, blank=True)

    def get_customer_name(self):
        if self.customer:
            return self.customer.get_name()
        return "Guest"

    def get_terminal_name(self):
        if self.cash_register:
            return self.cash_register.get_terminal_name()
        return None

    def get_customer_email(self):
        if self.customer:
            return self.customer.get_email()
        return None

    def get_created_at(self):
        if self.created_at:
            return self.created_at.strftime('%d-%m-%y %I:%M %p')
        return "_"

    def get_total(self):
        items = self.orderitem_set.all()
        subtotal = sum(item.price * item.quantity for item in items)
        discount_total = sum(item.discount for item in items)
        cost = sum(item.cost * item.quantity for item in items)

        returns = self.returnnote_set.all()
        return_total = sum(item.amount for item in returns)
        order_total = subtotal - discount_total
        grand_total = (subtotal + (self.delivery_fee or 0)) - (discount_total + return_total)
        net_total = subtotal - (discount_total + return_total)
        profit = order_total - cost

        context = {'subtotal': subtotal, 'discount_total': discount_total, 'cost': cost, 'return_total': return_total,
                   'order_total': order_total, 'grand_total': grand_total, 'profit': profit, 'net_total': net_total}

        return context

    def __str__(self):
        return f"Customer-{self.customer} - O#-{self.order_number}"


class OrderItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    batch_number = models.CharField(max_length=50, blank=True, null=True)  # Added batch number
    item_name = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    percentage_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    percentage_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    flat_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    # discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    # total_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    line_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    quantity = models.IntegerField(blank=True, default=1)
    return_quantity = models.IntegerField(default=0)
    item_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    item_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    order = models.ForeignKey(Order, blank=False, null=False, on_delete=models.CASCADE, related_name="order_items")
    variation = models.ForeignKey(ProductVariation, blank=True, null=True, on_delete=models.SET_NULL)
    batch = models.ForeignKey(Batch, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Order-{self.order}"

    # def save(self, *args, **kwargs):
    #     """
    #     Override the save method to automatically calculate the item_total
    #     based on quantity and item_value.
    #     """
    #     # Calculate item_total based on quantity and item_value
    #     if self.item_value is not None:
    #         self.item_total = self.quantity * self.item_value
    #     else:
    #         self.item_total = 0  # Default to 0 if item_value is not set
    #
    #     # Call the parent class's save method to persist the changes
    #     super().save(*args, **kwargs)

    def return_item(self, count, refund_amount):
        if count < 0:
            raise ValidationError("Return count cannot be negative.")
        if count > self.quantity:
            raise ValidationError("Return count exceeds available quantity.")

        # Update quantities for the order item
        self.quantity -= count
        self.return_quantity += count

        # Recalculate item_total based on the updated quantity
        self.item_total = self.quantity * refund_amount if refund_amount else self.item_total

        # Save changes to the OrderItem first
        self.save()

        # Update the related Order instance
        order = self.order  # Get the related order

        return_amount = refund_amount * count

        # Update the order fields based on returned items
        # order.order_items_discount -= (self.total_discount * count)
        order.return_amount += return_amount
        order.total -= return_amount

        # Save the changes to the order
        order.save()


class OrderAddress(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    order = models.ForeignKey(Order, blank=False, null=True, on_delete=models.CASCADE, related_name='order_addresses')
    title = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    delivery_contact = models.CharField(max_length=15, blank=True, null=True, validators=[phone_regex])
    delivery_note = models.CharField(max_length=200, blank=True, null=True)
    delivery_time = models.CharField(max_length=100, null=True, blank=True)
    delivery_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Id-{self.id} Order-{self.order.order_number}"


class OrderNote(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    order = models.ForeignKey(Order, blank=False, null=False, on_delete=models.CASCADE)
    note = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.note


class OrderReturn(models.Model):
    RETURN_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    REFUND_METHOD = [
        ('add_to_wallet', 'Add to Wallet'),
        ('return_voucher', 'Return Voucher'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    return_number = models.IntegerField(null=True, unique=True)
    return_status = models.CharField(max_length=50, choices=RETURN_STATUS, default='pending')
    refund_method = models.CharField(max_length=50, choices=REFUND_METHOD, default='return_voucher')
    reason = models.TextField(blank=True, null=True)  # Reason for return
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-return_number']

    def save(self, *args, **kwargs):
        # Assign return number if not already assigned
        if not self.return_number:
            last_return_order = OrderReturn.objects.order_by('-return_number').first()
            self.return_number = (last_return_order.return_number + 1) if last_return_order else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order Return #{self.return_number} - Order #{self.order.order_number}"


class OrderReturnItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('restocked', 'Restocked'),
        ('returned_to_supplier', 'Returned to Supplier'),
        ('damaged_discarded', 'Damaged and Discarded'),
        ('refunded', 'Refunded'),
        ('replacement_issued', 'Replacement Issued'),
        ('not_approved', 'Not Approved'),
        ('partial_refund', 'Partial Refund'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    return_quantity = models.IntegerField(default=1)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending')

    order_return = models.ForeignKey(OrderReturn, on_delete=models.CASCADE, related_name="return_order_items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"Return Item for {self.order_return}"


class ReturnVoucher(models.Model):
    VOUCHER_STATUS = [
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
    ]
    short_id = models.CharField(max_length=8, unique=True, default=generate_short_id, editable=False)
    code = models.CharField(max_length=20, unique=True)
    mobile = models.CharField(max_length=15, null=False, blank=False, validators=[phone_regex])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=VOUCHER_STATUS, default='active')
    issued_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    order_return = models.ForeignKey(OrderReturn, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"Voucher-{self.code}"

    @property
    def is_expired(self) -> bool:
        now = timezone.now()
        return self.is_valid and self.expiry_date <= now

    @property
    def is_redeemed(self) -> bool:
        return self.status == 'redeemed'

    def is_valid(self):
        """Check if the voucher is valid."""
        return self.status == 'active' and (self.expiry_date is None or self.expiry_date > timezone.now())

    def save(self, *args, **kwargs):
        # Generate a unique code if it doesn't exist
        if not self.code:
            self.code = uuid.uuid4().hex[:8].upper()  # Generate an 8-character unique code

       # Set expiry_date as 14 days from issued_at if not already set
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=14)

        super().save(*args, **kwargs)

    def redeem(self):
        """Mark the voucher as redeemed."""
        if self.status == 'active':
            self.status = 'redeemed'
            self.save()
        else:
            raise ValueError("Voucher cannot be redeemed as it is not active.")


class ReturnNote(models.Model):
    PAYMENT_METHOD = [
        ('CASH', 'CASH'),
        ('IPG_REFUND', 'IPG_REFUND'),
        ('ONLINE_PAYMENT', 'ONLINE_PAYMENT'),
        ('BANK_TRANSFER', 'BANK_TRANSFER'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    return_number = models.IntegerField(null=True, unique=True)
    order = models.ForeignKey(Order, blank=False, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    reason = models.CharField(max_length=150, blank=True, null=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, blank=True, null=True)
    transaction_reference = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.return_number:
            # get the highest existing Order instance and increment it
            return_note = ReturnNote.objects.order_by('-return_number').first()
            if return_note is None:
                # if there are no existing Order instances, start from 1
                self.return_number = 1
            else:
                self.return_number = return_note.return_number + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"RN-{self.return_number}"


class OrderDispatch(models.Model):
    TYPE = [
        ('SELF_DELIVERY', 'SELF_DELIVERY'),
        ('DELIVERY_PARTNER', 'DELIVERY_PARTNER')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    order = models.OneToOneField(Order, blank=True, null=True, on_delete=models.CASCADE)
    deliver_partner = models.ForeignKey(DeliveryPartner, blank=True, null=True, on_delete=models.PROTECT)
    self_deliver_partner = models.ForeignKey(SelfDeliveryPartner, blank=True, null=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=50, choices=TYPE)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=15, null=False, blank=False, validators=[phone_regex])
    tracking_number = models.CharField(max_length=200, blank=True, null=True)
    tracking_link = models.CharField(max_length=200, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.order} - {self.name}"


class Review(models.Model):
    # variation_option = models.ForeignKey('VariationOption', null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    rating = models.IntegerField()
    photos = models.JSONField(default=list, blank=True, null=True)
    positive_feedbacks_count = models.IntegerField(default=0)
    negative_feedbacks_count = models.IntegerField(default=0)
    abusive_reports_count = models.IntegerField(default=0)
    my_feedback = models.BooleanField(null=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f'Review by {self.customer} on {self.product}'
