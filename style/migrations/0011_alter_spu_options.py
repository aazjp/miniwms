# Generated by Django 5.1.5 on 2025-03-08 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('style', '0010_alter_spu_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spu',
            options={'permissions': [('download_barcode', 'Can download barcode'), ('search_spu', 'Can search spu')]},
        ),
    ]
