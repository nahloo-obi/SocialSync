# Generated by Django 5.0.4 on 2025-02-10 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_profiles_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=20)),
                ('phone_number', models.CharField(max_length=11)),
                ('text', models.TextField()),
            ],
        ),
    ]
