# Generated by Django 5.2.1 on 2025-07-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
