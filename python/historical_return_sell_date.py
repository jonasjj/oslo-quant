#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import numpy as np

from markets import get_instrument
from historical_return_from_to_date import parse_date
from historical_return_from_to_date import historical_return_from_to_date
from historical_return_best_dates import print_tablist
from plotting import linked_plot

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
           - sorted by average gain ratio
           - sorted by change of positive gain ratio:

            {'days':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'avg_gain_ratio': 
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'pos_gain':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..]}

        'sell_date' will of course be the sell_date given as an argument
    """
    # start with a buy date which is sell_date minus 1 year + 1 day
    buy_date = datetime.date(sell_date.year - 1, sell_date.month, sell_date.day) + \
               datetime.timedelta(days=1)

    results = []
        
    # for all the days in the year leading up to sell_date
    while buy_date <= sell_date:

        d = historical_return_from_to_date(instrument, buy_date, sell_date)

        results.append((buy_date,
                        sell_date,
                        d['avg_gain_ratio'],
                        d['pos_gain_ratio']))
        
        # increment by one day
        buy_date += datetime.timedelta(days=1)

    # store year count of the source data
    year_count = d['year_count']

    # sort by column a, then by column b
    avg_gain_list = sorted(results, key=lambda x: (x[2], x[3]), reverse=True)
    pos_gain_list = sorted(results, key=lambda x: (x[3], x[2]), reverse=True)

    d = {'days': results,
         'year_count': year_count,
         'avg_gain_ratio': avg_gain_list,
         'pos_gain_ratio': pos_gain_list}
    
    return d
    
if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot historical return when selling at a particular date")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX.OSE")
    parser.add_argument("sell_date", help="Sell date: YYYY-MM-DD")
    args = parser.parse_args()

    # get the instrument from the database
    instrument = get_instrument(args.instrument.upper())

    sell_date = parse_date(args.sell_date)

    res = historical_return_sell_date(instrument, sell_date)

    # print a table with the results
    print_tablist(res['days'])
    
    # create empty numpy matrix with room for all values
    matrix = np.zeros(shape=len(res['days']),
                      dtype=[('date', 'f8'),
                             ('avg_gain', 'f8'),
                             ('pos_gain', 'f8')])

    # construct numpy matrix
    for i,day in enumerate(res['days']):
        date, _, avg_gain, pos_gain = day
        
        # convert to Unix timestamp
        dt = datetime.datetime(date.year, date.month, date.day)
        timestamp = dt.timestamp()
        
        matrix[i] = timestamp, avg_gain, pos_gain
    
    # create the plot
    linked_plot([(matrix,
                  'avg_gain',
                  "Average gain ratio for " + instrument.name + \
                  ", years averaged: " + str(res['year_count'])),
                 (matrix,
                  'pos_gain',
                  "Positive gain ratio for " + instrument.name + \
                  ", years averaged: " + str(res['year_count']))])
