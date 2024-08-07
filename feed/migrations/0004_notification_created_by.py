# Generated by Django 5.0.6 on 2024-06-22 12:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
