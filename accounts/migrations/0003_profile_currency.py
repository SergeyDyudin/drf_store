# Generated by Django 4.0 on 2022-01-24 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20220113_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='currency',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Virtual currency'),
        ),
    ]
