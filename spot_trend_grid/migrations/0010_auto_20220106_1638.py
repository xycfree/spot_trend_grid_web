# Generated by Django 3.1.7 on 2022-01-06 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trend_grid', '0009_auto_20220106_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='last_price',
            field=models.CharField(blank=True, default='', help_text='最新买入价', max_length=256, null=True, verbose_name='最新买入价'),
        ),
    ]