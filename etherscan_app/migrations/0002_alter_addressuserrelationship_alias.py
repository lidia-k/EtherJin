# Generated by Django 3.2 on 2021-07-20 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("etherscan_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addressuserrelationship",
            name="alias",
            field=models.CharField(default=None, max_length=20, null=True, unique=True),
        ),
    ]
