# Generated by Django 4.2.3 on 2024-02-27 12:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0002_rename_switch_share_general_sharesettings_can_share_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sharesettings',
            old_name='can_share_basic_info',
            new_name='can_share_dashboard',
        ),
    ]
