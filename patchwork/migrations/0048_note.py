# Generated by Django 5.1.2 on 2024-11-04 07:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('patchwork', '0047_add_database_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'updated_at',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ('content', models.TextField(blank=True)),
                ('maintainer_only', models.BooleanField(default=True)),
                (
                    'patch',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='note',
                        related_query_name='note',
                        to='patchwork.patch',
                    ),
                ),
                (
                    'submitter',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]