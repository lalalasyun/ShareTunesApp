# Generated by Django 5.2 on 2025-04-16 14:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255)),
                ('album', models.CharField(blank=True, max_length=255, null=True)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('preview_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '楽曲',
                'verbose_name_plural': '楽曲',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserTrackHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_history', to='tracks.track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '楽曲再生履歴',
                'verbose_name_plural': '楽曲再生履歴',
                'ordering': ['-played_at'],
            },
        ),
    ]
