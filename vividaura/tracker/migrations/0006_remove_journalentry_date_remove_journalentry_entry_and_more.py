# Generated by Django 5.2 on 2025-05-03 03:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_journalentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journalentry',
            name='date',
        ),
        migrations.RemoveField(
            model_name='journalentry',
            name='entry',
        ),
        migrations.RemoveField(
            model_name='moodentry',
            name='journal_entry',
        ),
        migrations.AddField(
            model_name='journalentry',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='Write about your day'),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
