# Generated manually for ZenoPay integration

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('billing', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Update SMSBalance to use tenant instead of user
        migrations.RemoveField(
            model_name='smsbalance',
            name='user',
        ),
        migrations.AddField(
            model_name='smsbalance',
            name='tenant',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sms_balance', to='tenants.tenant'),
        ),
        
        # Update UsageRecord to use tenant
        migrations.AddField(
            model_name='usagerecord',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_records', to='tenants.tenant'),
        ),
        
        # Update Subscription to use tenant
        migrations.RemoveField(
            model_name='subscription',
            name='user',
        ),
        migrations.AddField(
            model_name='subscription',
            name='tenant',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='tenants.tenant'),
        ),
        
        # Create PaymentTransaction model
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('zenopay_order_id', models.CharField(help_text='ZenoPay order ID', max_length=100, unique=True)),
                ('zenopay_reference', models.CharField(blank=True, help_text='ZenoPay reference number', max_length=100)),
                ('zenopay_transid', models.CharField(blank=True, help_text='ZenoPay transaction ID', max_length=100)),
                ('zenopay_channel', models.CharField(blank=True, help_text='Payment channel (e.g., MPESA-TZ)', max_length=50)),
                ('zenopay_msisdn', models.CharField(blank=True, help_text='Customer phone number', max_length=20)),
                ('order_id', models.CharField(help_text='Internal order ID', max_length=100, unique=True)),
                ('invoice_number', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='TZS', max_length=3)),
                ('buyer_email', models.EmailField(max_length=254)),
                ('buyer_name', models.CharField(max_length=100)),
                ('buyer_phone', models.CharField(max_length=20)),
                ('payment_method', models.CharField(choices=[('zenopay_mobile_money', 'ZenoPay Mobile Money'), ('mpesa', 'M-Pesa'), ('tigopesa', 'Tigo Pesa'), ('airtelmoney', 'Airtel Money'), ('bank_transfer', 'Bank Transfer'), ('credit_card', 'Credit Card')], max_length=30)),
                ('payment_reference', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('webhook_url', models.URLField(blank=True)),
                ('webhook_received', models.BooleanField(default=False)),
                ('webhook_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('failed_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_transactions', to='tenants.tenant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_transactions', to='accounts.user')),
            ],
            options={
                'db_table': 'payment_transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
