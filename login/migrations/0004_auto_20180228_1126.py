# Generated by Django 2.0.1 on 2018-02-28 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_user_u_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='u_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
