# Generated by Django 5.1.7 on 2025-03-17 05:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_productstore_display_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='mobileModel',
            fields=[
                ('productstore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.productstore')),
                ('brand', models.CharField(max_length=100)),
                ('storage', models.CharField(max_length=100)),
                ('network', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Mobile',
            },
            bases=('products.productstore',),
        ),
    ]
