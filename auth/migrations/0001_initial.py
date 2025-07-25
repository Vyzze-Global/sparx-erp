# Generated by Django 5.0.6 on 2025-06-18 03:35

import auth.models
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True)),
                ('phone_number', models.CharField(blank=True, db_index=True, max_length=15, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+94719999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('user_type', models.CharField(choices=[('admin', 'Admin'), ('employee', 'Employee'), ('customer', 'Customer')], default='customer', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_users', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_users', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('whatsapp', models.CharField(blank=True, max_length=15, null=True, unique=True, validators=[auth.models.validate_whatsapp_number])),
                ('email_token', models.CharField(blank=True, max_length=100, null=True)),
                ('forget_password_token', models.CharField(blank=True, max_length=100, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='customer_profiles/')),
                ('bio', models.TextField(blank=True, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('birth_day', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=20, null=True)),
                ('loyalty_points', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_profiles_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_profiles_updated', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(limit_choices_to={'user_type': 'customer'}, on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('mobile', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+94719999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('whatsapp', models.CharField(blank=True, max_length=15, null=True, unique=True, validators=[auth.models.validate_whatsapp_number])),
                ('email_token', models.CharField(blank=True, max_length=100, null=True)),
                ('forget_password_token', models.CharField(blank=True, max_length=100, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='employee_profiles/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('emp_code', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('commission_rate', models.DecimalField(blank=True, decimal_places=2, help_text='Commission percentage', max_digits=5, null=True)),
                ('sales_target', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('monthly_sales_total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('notes', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_profiles_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_profiles_updated', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(limit_choices_to={'user_type': 'employee'}, on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='useraccount',
            constraint=models.UniqueConstraint(condition=models.Q(('phone_number__isnull', False)), fields=('phone_number',), name='unique_phone_number'),
        ),
        migrations.AddConstraint(
            model_name='customerprofile',
            constraint=models.UniqueConstraint(condition=models.Q(('whatsapp__isnull', False)), fields=('whatsapp',), name='unique_customer_whatsapp'),
        ),
        migrations.AddIndex(
            model_name='employeeprofile',
            index=models.Index(fields=['status', 'mobile', 'whatsapp'], name='accounts_em_status_0159a9_idx'),
        ),
        migrations.AddConstraint(
            model_name='employeeprofile',
            constraint=models.UniqueConstraint(condition=models.Q(('whatsapp__isnull', False)), fields=('whatsapp',), name='unique_employee_whatsapp'),
        ),
        migrations.AddConstraint(
            model_name='employeeprofile',
            constraint=models.UniqueConstraint(condition=models.Q(('emp_code__isnull', False)), fields=('emp_code',), name='unique_emp_code'),
        ),
    ]
