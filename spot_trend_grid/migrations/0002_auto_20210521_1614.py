# Generated by Django 3.1.7 on 2021-05-21 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trend_grid', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsNoticeModel',
            fields=[
                ('id', models.AutoField(help_text='自增id', primary_key=True, serialize=False)),
                ('coin_id', models.IntegerField(help_text='交易对ID,对应SpotConfigModel.id', verbose_name='交易对ID')),
                ('coin_type', models.CharField(help_text='交易对,如BTC填入BTCUSDT)', max_length=16, verbose_name='交易对')),
                ('status', models.IntegerField(help_text='已达最大购买次数通知标记', verbose_name='钉钉通知标记')),
                ('if_use', models.BooleanField(default=True, verbose_name='是否启用')),
            ],
            options={
                'verbose_name': '钉钉通知标记',
                'verbose_name_plural': '最大购买次数通知标记',
            },
        ),
        migrations.AlterModelOptions(
            name='spotconfigmodel',
            options={'verbose_name': '现货趋势策略', 'verbose_name_plural': '现货趋势策略'},
        ),
    ]
