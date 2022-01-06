# Generated by Django 3.1.7 on 2021-09-09 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trend_grid', '0002_spotconfigmodel_free'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='double_throw_ratio',
            field=models.DecimalField(decimal_places=2, help_text='补仓比率(买入价调整比率。如：设置为5,即为5%当前买入价为100，那么下次买入价为95)', max_digits=4, verbose_name='补仓比率'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='profit_ratio',
            field=models.DecimalField(decimal_places=2, help_text='止盈比率(卖出价调整比率。如：设置为5,即为5%，当前买入价为100，那么下次卖出价为105)', max_digits=4, verbose_name='止盈比率'),
        ),
    ]
