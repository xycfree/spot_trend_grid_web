# Generated by Django 3.1.7 on 2022-01-06 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trend_grid', '0007_auto_20220106_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='double_throw_ratio',
            field=models.CharField(blank=True, default='', help_text='补仓比率列表(买入价调整比率。如：设置为5,即为5%当前买入价为100，那么下次买入价为95),为空则计算atr波动率', max_length=256, null=True, verbose_name='补仓比率'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='free',
            field=models.DecimalField(blank=True, decimal_places=8, default=0, help_text='可用货币数量', max_digits=10, null=True, verbose_name='可用数量'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='last_price',
            field=models.DecimalField(blank=True, decimal_places=8, default=0, help_text='最新买入价', max_digits=16, null=True, verbose_name='最新买入价'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='max_count',
            field=models.IntegerField(default=5, help_text='连续买入而不卖出的最大次数', verbose_name='连续买入而不卖出的最大次数'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='min_num',
            field=models.IntegerField(default=5, help_text='交易金额最小位数长度,如0.00001,则填入5', verbose_name='交易金额最小位数长度'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='profit_ratio',
            field=models.CharField(blank=True, default='', help_text='止盈比率列表(卖出价调整比率。如：设置为5,即为5%，当前买入价为100，那么下次卖出价为105),为空则计算atr波动率', max_length=256, null=True, verbose_name='止盈比率'),
        ),
        migrations.AlterField(
            model_name='spotconfigmodel',
            name='quantity',
            field=models.CharField(blank=True, default='', help_text='交易数量列表', max_length=256, null=True, verbose_name='交易数量列表'),
        ),
    ]