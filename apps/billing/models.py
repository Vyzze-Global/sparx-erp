import random
import string
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.orders.models import Order, ReturnNote
from auth.models import CustomerProfile


def generate_short_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


class Invoice(models.Model):
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('pro-forma', 'Pro-Forma'),
        ('invoice', 'Invoice'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('payment_pending', 'Payment Pending')
    ]
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('card_payment', 'Card Payment'),
        ('online_payment', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('cash_on_delivery', 'Cash On Delivery'),
        ('bank_transfer', 'Bank Transfer')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    short_id = models.CharField(max_length=8, unique=True, default=generate_short_id, editable=False)
    invoice_number = models.IntegerField(null=True, unique=True)
    status = models.CharField(max_length=100, choices=INVOICE_STATUS, default='Draft')
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default='Cash')
    issued_at = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True,  default=0)
    paid = models.BooleanField(default=False)
    pay_url = models.URLField(blank=True, null=True)
    pay_url_expiry = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    remarks = models.CharField(max_length=150, blank=True, null=True)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-invoice_number']

    @staticmethod
    def _generate_invoice_number():
        """Generate the next invoice number."""
        last_invoice = Invoice.objects.order_by('-invoice_number').first()
        return (last_invoice.invoice_number + 1) if last_invoice and last_invoice.invoice_number else 1

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # get the highest existing invoice instance and increment it
            invoice = Invoice.objects.order_by('-invoice_number').first()
            if invoice is None:
                # if there are no existing Job instances, start from 1
                self.invoice_number = 1
            else:
                self.invoice_number = invoice.invoice_number + 1

        # get the sum of all order item amounts
        if self.order:
            self.total_amount = self.order.total

        # save the invoice instance
        super().save(*args, **kwargs)

    def get_balance_due(self):
        """
        Returns the balance due on the invoice.
        """
        return Decimal(self.order.total) - Decimal(self.get_total_payments())

    def get_total_refund(self):
        refunds = ReturnNote.objects.filter(order=self.order)
        return sum([refund.amount for refund in refunds])

    def get_total_payments(self):
        """
        Returns the total amount paid towards the invoice.
        """
        payments = InvoicePayment.objects.filter(invoice=self)
        return sum([payment.amount for payment in payments])

    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class InvoicePayment(models.Model):
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('card', 'Card'),
        ('online_payment', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('qr_payment', 'QR Payment'),
        ('wallet_payment', 'Wallet Payment'),
        ('loyalty_payment', 'Loyalty Payment'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    change_given = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    add_to_wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    tendered_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default='Cash')
    card_type = models.CharField(max_length=100, blank=True, null=True)
    card_last_digits = models.IntegerField(blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # # Check if amount is greater than balance due
        # if self.amount > self.invoice.get_balance_due():
        #     raise ValidationError("Payment amount cannot be greater than the balance due.")

        if not self.payment_date:
            self.payment_date = timezone.now()
        super(InvoicePayment, self).save(*args, **kwargs)

        # Update the invoice's paid status
        invoice = self.invoice
        if invoice.get_balance_due() <= 0:
            invoice.paid = True
            invoice.status = 'Paid'
            invoice.save()

    def __str__(self):
        return str(self.invoice)
