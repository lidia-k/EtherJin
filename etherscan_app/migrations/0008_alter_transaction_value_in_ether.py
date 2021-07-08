# Generated by Django 3.2 on 2021-07-08 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etherscan_app', '0007_address_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='value_in_ether',
            field=models.DecimalField(decimal_places=100, max_digits=110),
        ),
    ]
