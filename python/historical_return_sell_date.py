#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from markets import get_instrument
from historical_return_from_to_date import parse_date

def historical_return_sell_date(instrument, sell_date):
    """
    Find the historical average gain and chance of positive gain when buying
    an instrument up to a year in advance, but selling on a given date.

    Args:
        instrument (markets.Instrument): Instrument to check
        sell_date (datetime.date): The sell date to estimate for

    Return:
        dict with three list:
           - sorted by date, ending at sell_date
           - sorted by date starting at 1st of January    
           - sorted by average gain ratio
           - sorted by change of positive gain ratio:

            {'days_up_to':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'days_by_calendar_year':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'avg_gain_ratio': 
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'pos_gain':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..]}

        'sell_date' will of course be the sell_date given as an argument
    """
    pass

if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot historical return when selling at a particular date")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX.OSE")
    parser.add_argument("sell_date", help="Sell date: YYYY-MM-DD")
    args = parser.parse_args()

    # get the instrument from the database
    instrument = get_instrument(args.instrument.upper())

    sell_date = parse_date(args.sell_date)
