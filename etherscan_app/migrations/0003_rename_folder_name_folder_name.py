# Generated by Django 3.2 on 2021-08-04 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etherscan_app', '0002_alter_addressuserrelationship_alias'),
    ]

    operations = [
        migrations.RenameField(
            model_name='folder',
            old_name='folder_name',
            new_name='name',
        ),
    ]
