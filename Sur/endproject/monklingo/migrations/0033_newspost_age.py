# Generated by Django 5.1.3 on 2025-03-31 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monklingo', '0032_customuser_assigned_temple'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspost',
            name='age',
            field=models.TextField(null=True),
        ),
    ]
