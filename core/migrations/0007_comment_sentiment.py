# Generated by Django 4.1.1 on 2024-04-29 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_savepost'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sentiment',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]