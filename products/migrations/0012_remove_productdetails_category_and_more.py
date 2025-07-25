# Generated by Django 5.1.7 on 2025-03-18 05:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_remove_carmodel_productstore_ptr_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productdetails',
            name='category',
        ),
        migrations.RemoveField(
            model_name='productdetails',
            name='sub_category',
        ),
        migrations.AddField(
            model_name='productdetails',
            name='value',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ProductTitles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.produtccategory')),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productsubcategory')),
            ],
            options={
                'db_table': 'product_details_title',
            },
        ),
        migrations.AlterField(
            model_name='productdetails',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.producttitles'),
        ),
    ]
