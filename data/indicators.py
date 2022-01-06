#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/12/17 10:28  @Author: wangbing3  @Descript:

import talib.abstract as ta
# import talib as ta
import numpy as np
import pandas as pd
from pandas import DataFrame
from data import binan
from loguru import logger


def populate_indicators(dataframe: DataFrame, metadata: dict = None) -> DataFrame:
    macd = ta.MACD(dataframe)
    dataframe['macd'] = macd['macd']
    dataframe['macdsignal'] = macd['macdsignal']

    ### Add timeperiod from hyperopt (replace xx with value):
    ### "xx" must be replaced even before the first hyperopt is run,
    ### else "xx" would be a syntax error because it must be a Integer value.
    dataframe['cci-buy'] = ta.CCI(dataframe, timeperiod=7)
    dataframe['cci-sell'] = ta.CCI(dataframe, timeperiod=7)

    return dataframe


def populate_buy_trend(dataframe: DataFrame, metadata: dict = None) -> DataFrame:
    dataframe.loc[
        (
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['cci-buy'] <= -100.0)  # Replace with value from hyperopt.
        ),
        'buy'] = 1

    return dataframe


def populate_sell_trend(dataframe: DataFrame, metadata: dict = None) -> DataFrame:
    dataframe.loc[
        (
                (dataframe['macd'] < dataframe['macdsignal']) &
                (dataframe['cci-sell'] >= 260.0)  # Replace with value from hyperopt.
        ),
        'sell'] = 1

    return dataframe


def fetch_ohlcv_to_dataframe(symbol, interval="15m", point=6):
    """ 获取K线图
    :param point: 小数位长度
    :param interval: 时间间隔，5m, 15m, 1h, 4h
    :param symbol: 交易对 BTC/USDT
    :return:
    """
    data = binan.get_klines(symbol, interval, limit=100)
    """
            [
          [
            1499040000000,      // 开盘时间
            "0.01634790",       // 开盘价
            "0.80000000",       // 最高价
            "0.01575800",       // 最低价
            "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
            "148976.11427815",  // 成交量
            1499644799999,      // 收盘时间
            "2434.19055334",    // 成交额
            308,                // 成交笔数
            "1756.87402397",    // 主动买入成交量
            "28.46694368",      // 主动买入成交额
            "17928899.62484339" // 请忽略该参数
          ]
        ]
    """
    df = pd.DataFrame(data)
    df = df.iloc[:, 0:6]  # 截取6列
    df.columns = ["open_time", "open", "high", "low", "close", "volume"]  # 增加列标头
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms") + pd.Timedelta(hours=8)  # UTC +8

    # logger.info(df)
    logger.info(df["open"].dtypes)  # 查看列类型
    logger.info(type(df["open"][0]))  # 查看列值类型
    df["open"] = pd.to_numeric(df["open"], errors="raise", downcast=None)  # open列字符串转换为int64或float64
    df["open"] = df["open"].round(decimals=point)  # open列保留小数位
    logger.info(df)
    return df


if __name__ == '__main__':
    df = fetch_ohlcv_to_dataframe("ONEUSDT")
    df = populate_indicators(df)
    df = populate_buy_trend(df)
    df = populate_sell_trend(df)
    logger.info(df[df["buy"] > 0])
