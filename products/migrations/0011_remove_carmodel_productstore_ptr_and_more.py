# Generated by Django 5.1.7 on 2025-03-18 04:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_productdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carmodel',
            name='productstore_ptr',
        ),
        migrations.RemoveField(
            model_name='mobilemodel',
            name='productstore_ptr',
        ),
        migrations.AlterModelTable(
            name='productdetails',
            table='product_details',
        ),
        migrations.DeleteModel(
            name='bikeModel',
        ),
        migrations.DeleteModel(
            name='carModel',
        ),
        migrations.DeleteModel(
            name='mobileModel',
        ),
    ]
