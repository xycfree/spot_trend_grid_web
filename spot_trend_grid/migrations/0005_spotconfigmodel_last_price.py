# Generated by Django 3.1.7 on 2022-01-05 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trend_grid', '0004_auto_20211227_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='spotconfigmodel',
            name='last_price',
            field=models.DecimalField(decimal_places=8, help_text='最新买入价', max_digits=16, null=True, verbose_name=True),
        ),
    ]