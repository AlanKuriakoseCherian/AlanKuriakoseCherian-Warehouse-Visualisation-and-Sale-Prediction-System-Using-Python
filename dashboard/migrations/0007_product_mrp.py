# Generated by Django 3.2.8 on 2022-07-17 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='mrp',
            field=models.FloatField(default=1000.0),
        ),
    ]