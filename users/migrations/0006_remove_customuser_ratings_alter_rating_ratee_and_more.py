# Generated by Django 4.2.20 on 2025-05-26 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customuser_ratings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='ratings',
        ),
        migrations.AlterField(
            model_name='rating',
            name='ratee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rate_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='rating',
            name='rater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rate_sent', to=settings.AUTH_USER_MODEL),
        ),
    ]
