#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import argparse
from pprint import pprint
from collections import OrderedDict
import statistics

from markets import get_instrument

def parse_date(date_str):
    """
    Parse '2015-12-24' string and return datetime object
    
    Raises:
        ValueError on error

    Return:
        datetime.date object
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        raise ValueError("Couldn't parse date " + str(date_str) + " on the format YYYY-MM-DD")

def historical_return_from_to_date(instrument, buy_date, sell_date):

    if buy_date > sell_date:
        raise ValueError("Sell date is before buy date")
    
    # get the first and last timestamp in the available data
    first_date = instrument.get_first_date()
    last_date = instrument.get_last_date()

    # estimate days
    days = (sell_date - buy_date).days

    # rewind to the first available buy date
    _buy_date = buy_date
    _sell_date = sell_date
    while _buy_date > first_date:

        # decrement by 1 year
        _buy_date = _buy_date.replace(year=_buy_date.year - 1)
        _sell_date =  _sell_date.replace(year=_sell_date.year - 1)

    # this is the first possible starting point
    _buy_date = _buy_date.replace(year=_buy_date.year + 1)
    _sell_date = _sell_date.replace(year=_sell_date.year + 1)

    if _buy_date < first_date or _sell_date > last_date:
        raise KeyError("Not enough data")
    
    trades = []
    accumulated_gain = 0
    accumulated_gain_ratio = 0
    year_count = 0
    pos_gain_trades = 0
    neg_gain_trades = 0

    gain_ratios = []

    # use the close price if it exists
    if 'close' in instrument.data.dtype.names:
        value_key = 'close'
    else:
        value_key = 'value'
        
    
    while _sell_date <= last_date:

        buy = instrument.get_day_or_first_after(_buy_date)
        sell = instrument.get_day_or_first_after(_sell_date)

        # sanity checking of the input data
        if buy[value_key] == 0 or sell[value_key] == 0:
            _buy_date = _buy_date.replace(year=_buy_date.year + 1)
            _sell_date = _sell_date.replace(year=_sell_date.year + 1)
            continue
            raise Exception("Value is 0. The input data is erroneous")

        year_count += 1

        gain = sell[value_key] - buy[value_key]
        gain_ratio = (sell[value_key] / buy[value_key]) - 1
        gain_ratios.append(gain_ratio)
        accumulated_gain += gain
        accumulated_gain_ratio += gain_ratio

        if gain > 0:
            pos_gain_trades += 1        
        
        trade=OrderedDict()
        trade['buy_date'] = buy['date']
        trade['sell_date'] = sell['date']
        trade['buy'] = buy[value_key]
        trade['sell'] = sell[value_key]
        trade['gain_ratio'] = gain_ratio
        trades.append(trade)

        # increment by 1 year
        _buy_date = _buy_date.replace(year=_buy_date.year + 1)
        _sell_date = _sell_date.replace(year=_sell_date.year + 1)

    if year_count == 0:
        raise ValueError("There are no historical trades for these dates")
        
    avg_gain = accumulated_gain / year_count
    avg_gain_ratio = accumulated_gain_ratio / year_count

    try:
        pos_gain_ratio = pos_gain_trades / year_count
    except ZeroDivisionError:
        pos_gain_ratio = 0
        
    variance = statistics.variance(gain_ratios)
    std_deviation = statistics.stdev(gain_ratios)
        
    data = OrderedDict()
    data['trades'] = trades
    data['year_count'] = year_count
    data['avg_gain_ratio'] = avg_gain_ratio
    data['pos_gain_ratio'] = pos_gain_ratio
    data['variance'] = variance
    data['std_deviation'] = std_deviation
    return data
                      
if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the historical return between dates")
    parser.add_argument("ticker", help="Ticker name (ex.: OBX.OSE)")
    parser.add_argument("buy_date", help="Buy date: YYYY-MM-DD")
    parser.add_argument("sell_date", help="Sell date: YYYY-MM-DD")
    args = parser.parse_args()

    # get the instrument from the database
    instrument = get_instrument(args.ticker.upper())
    
    buy_date = parse_date(args.buy_date)
    sell_date = parse_date(args.sell_date)

    pprint(historical_return_from_to_date(instrument, buy_date, sell_date))
