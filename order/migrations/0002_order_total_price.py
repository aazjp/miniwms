# Generated by Django 5.1.5 on 2025-02-25 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
