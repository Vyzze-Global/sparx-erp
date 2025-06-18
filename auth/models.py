import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
from django.conf import settings

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+94719999999'. Up to 15 digits allowed."
)

def validate_whatsapp_number(value):
    regex = r'^\d{10,15}$'
    if not re.match(regex, value):
        raise ValidationError(
            'Invalid WhatsApp number: %(value)s',
            params={'value': value},
        )

class UserAccountManager(BaseUserManager):
    def create_user(self, email, phone_number, first_name, last_name, password=None, **kwargs):
        if not email:
            raise ValueError("Email is required")
        if not phone_number and kwargs.get('user_type') == 'customer':
            raise ValueError("Phone number is required for customers")
        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_customer(self, email, phone_number, first_name, last_name, password=None, **kwargs):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_type='customer',
            **kwargs
        )
        CustomerProfile.objects.create(
            user=user,
            mobile=phone_number,
            is_verified=kwargs.get('is_verified', False)
        )
        return user

    def create_employee(self, email, phone_number, first_name, last_name, emp_code=None, password=None, **kwargs):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_type='employee',
            is_verified=kwargs.get('is_verified', False),
            **kwargs
        )
        EmployeeProfile.objects.create(
            user=user,
            mobile=phone_number,
            emp_code=emp_code,
            is_verified=kwargs.get('is_verified', False)
        )
        return user

    def create_superuser(self, email, phone_number, first_name, last_name, password=None, **kwargs):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_type='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            **kwargs
        )
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    USER_TYPE = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True, validators=[phone_regex], db_index=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_users')
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['phone_number'], condition=models.Q(phone_number__isnull=False), name='unique_phone_number'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} - {self.email}"


class EmployeeProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='employee_profile', limit_choices_to={'user_type': 'employee'})
    is_verified = models.BooleanField(default=False)
    mobile = models.CharField(max_length=15, blank=True, null=True, validators=[phone_regex])
    whatsapp = models.CharField(max_length=15, blank=True, null=True, unique=True, validators=[validate_whatsapp_number])
    email_token = models.CharField(max_length=100, blank=True, null=True)
    forget_password_token = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    emp_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Commission percentage")
    sales_target = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    monthly_sales_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name='employee_profiles_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name='employee_profiles_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['whatsapp'], condition=models.Q(whatsapp__isnull=False), name='unique_employee_whatsapp'),
            models.UniqueConstraint(fields=['emp_code'], condition=models.Q(emp_code__isnull=False), name='unique_emp_code'),
        ]
        indexes = [
            models.Index(fields=['status', 'mobile', 'whatsapp']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''} - Employee"


class CustomerProfile(models.Model):
    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='customer_profile', limit_choices_to={'user_type': 'customer'})
    is_verified = models.BooleanField(default=False)
    whatsapp = models.CharField(max_length=15, blank=True, null=True, unique=True, validators=[validate_whatsapp_number])
    email_token = models.CharField(max_length=100, blank=True, null=True)
    forget_password_token = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='customer_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    birth_day = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER, blank=True, null=True)
    loyalty_points = models.IntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_profiles_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_profiles_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['whatsapp'], condition=models.Q(whatsapp__isnull=False), name='unique_customer_whatsapp'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''} - Customer"