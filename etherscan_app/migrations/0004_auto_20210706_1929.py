# Generated by Django 3.2 on 2021-07-06 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etherscan_app', '0003_auto_20210706_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='hash',
            field=models.CharField(max_length=200, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='value_in_ether',
            field=models.DecimalField(decimal_places=100, max_digits=100),
        ),
    ]
