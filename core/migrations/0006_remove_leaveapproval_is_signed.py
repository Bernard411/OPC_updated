# Generated by Django 4.2.14 on 2024-12-02 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_leaveapproval_is_signed_leaveapproval_signature'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaveapproval',
            name='is_signed',
        ),
    ]
