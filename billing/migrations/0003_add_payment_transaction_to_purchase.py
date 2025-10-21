# Generated manually for ZenoPay integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_create_payment_transaction'),
    ]

    operations = [
        # Update Purchase to use tenant and add payment_transaction
        migrations.AddField(
            model_name='purchase',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='tenants.tenant'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='payment_transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase', to='billing.paymenttransaction'),
        ),
        
        # Update Purchase payment_method choices
        migrations.AlterField(
            model_name='purchase',
            name='payment_method',
            field=models.CharField(choices=[('zenopay_mobile_money', 'ZenoPay Mobile Money'), ('mpesa', 'M-Pesa'), ('tigopesa', 'Tigo Pesa'), ('airtelmoney', 'Airtel Money'), ('bank_transfer', 'Bank Transfer'), ('credit_card', 'Credit Card')], max_length=30),
        ),
    ]
