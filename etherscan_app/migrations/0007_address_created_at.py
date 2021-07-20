# Generated by Django 3.2 on 2021-07-08 00:45

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('etherscan_app', '0006_remove_address_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 7, 8, 0, 45, 30, 123891, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
