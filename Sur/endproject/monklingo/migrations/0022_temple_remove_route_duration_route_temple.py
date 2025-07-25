# Generated by Django 5.1.3 on 2025-02-20 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monklingo', '0021_checkpoint_name_alter_checkpoint_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temple',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Unknown Temple', max_length=255, unique=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='route',
            name='duration',
        ),
        migrations.AddField(
            model_name='route',
            name='temple',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='monklingo.temple'),
        ),
    ]
