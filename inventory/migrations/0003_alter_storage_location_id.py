# Generated by Django 4.2.17 on 2025-02-24 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_storage_location_remove_inventory_record_color_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage_location',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
