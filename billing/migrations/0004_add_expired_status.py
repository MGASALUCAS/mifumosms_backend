# billing/migrations/0004_add_expired_status.py
# Generated manually for adding expired status

from django.db import migrations, models  # ← add models here


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0003_add_payment_transaction_to_purchase"),
    ]

    operations = [
        # Add expired status to PaymentTransaction
        migrations.AlterField(
            model_name="paymenttransaction",
            name="status",
            field=models.CharField(
                max_length=20,
                default="pending",
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                    ("expired", "Expired"),
                    ("refunded", "Refunded"),
                ],
            ),
        ),

        # Add expired status to Purchase
        migrations.AlterField(
            model_name="purchase",
            name="status",
            field=models.CharField(
                max_length=20,
                default="pending",
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                    ("expired", "Expired"),
                    ("refunded", "Refunded"),
                ],
            ),
        ),
    ]
