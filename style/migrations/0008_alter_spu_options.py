# Generated by Django 4.2.17 on 2025-03-06 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('style', '0007_alter_spu_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spu',
            options={'permissions': [('can_view_spu', 'Can view spu'), ('can_add_spu', 'Can add spu'), ('can_update_spu', 'Can update spu'), ('can_delete_spu', 'Can delete spu')]},
        ),
    ]
