import uuid

from django.core.validators import RegexValidator
from django.db import models

phone_regex = RegexValidator(
    regex=r"^\d{10}", message="Invalid Phone Number"
)

# Create your models here.
class DeliveryCity(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    self_delivery = models.BooleanField(default=False)
    delivery_fee = models.FloatField(blank=True, default=0.00)

    def __str__(self):
        return f"{self.name} - {self.postal_code}"


class DeliveryPartner(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=10, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    hotline = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    tracking_link = models.CharField(max_length=200, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.hotline}"


class SelfDeliveryPartner(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    alt_contact = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    nic = models.CharField(max_length=14, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.contact}"


class Settings(models.Model):
    company_name = models.CharField(max_length=100, blank=True, null=True, default="Company Name")
    invoice_address = models.TextField(blank=True, null=True)
    invoice_hotline = models.CharField(max_length=15, null=True, blank=True, validators=[phone_regex])
    invoice_footer_note = models.TextField(blank=True, null=True)
    master_pin = models.CharField(max_length=6, null=True)
    logo = models.ImageField(upload_to='settings/logo', blank=True, null=True)
    retina_logo = models.ImageField(upload_to='settings/logo', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/logo', blank=True, null=True)
    invoice_logo = models.ImageField(upload_to='settings/logo', blank=True, null=True)

    def __str__(self):
        return "System Settings"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('delivery', 'Delivery'),
        ('promotions', 'Promotion'),
        ('system', 'System'),
    ]

    NOTIFY_USER_GROUP = [
        ('admin', 'Admin'),
        ('customer', 'Customer')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    # recipient_employee = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL)
    notification_type = models.CharField(max_length=20, null=True, blank=True, choices=NOTIFICATION_TYPES,
                                         default='system')
    notification_user_group = models.CharField(max_length=20, blank=True, null=True, choices=NOTIFY_USER_GROUP,
                                               default='admin')
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    action_name = models.CharField(max_length=20, blank=True, null=True)
    action_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.created_at}"


class DeliverySchedule(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class FileAttachment(models.Model):
    original = models.ImageField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original}"


class FAQ(models.Model):
    faq_title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    faq_description = models.TextField()
    faq_type = models.CharField(max_length=55, default='global', blank=True, null=True)

    def __str__(self):
        return self.faq_title


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    type = models.CharField(max_length=55, default='global', blank=True, null=True)
    issued_by = models.CharField(max_length=25, default='Super Admin', blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class RefundPolicy(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    target = models.CharField(max_length=25, blank=True, null=True)
    status = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title
