#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import numpy as np
from tabulate import tabulate

from markets import get_instrument
from historical_return_from_to_date import parse_date
from historical_return_from_to_date import historical_return_from_to_date
from plotting import LinkedPlot


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
                        d['pos_gain_ratio'],
                        d['variance'],
                        d['std_deviation']))

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


def print_tablist(results):
    """Print a tabulated list"""

    tab_list = []

    decimals = 4

    for r in results:
        tab_list.append((str(r[0]),
                         str(r[1]),
                         str(round(r[2], decimals)),
                         str(round(r[3], decimals)),
                         str(round(r[4], decimals)),
                         str(round(r[5], decimals))))

    print(tabulate(tab_list, headers=("Buy date",
                                      "Sell date",
                                      "Avg.gain",
                                      "Pos.gain",
                                      "Variance",
                                      "Std.dev")))


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Plot historical return when selling at a particular date")
    parser.add_argument("ticker", help="Ticker name (ex.: OBX.OSE)")
    parser.add_argument("sell_date", help="Sell date: YYYY-MM-DD")
    parser.add_argument("--variance",
                        action='store_true',
                        help="Plot variance as well")
    parser.add_argument("--std_deviation",
                        action='store_true',
                        help="Plot standard deviation as well")
    args = parser.parse_args()

    # get the instrument from the database
    instrument = get_instrument(args.ticker.upper())

    sell_date = parse_date(args.sell_date)

    res = historical_return_sell_date(instrument, sell_date)

    # print a table with the results
    print_tablist(res['days'])

    # create empty numpy matrix with room for all values
    matrix = np.zeros(shape=len(res['days']),
                      dtype=[('date', 'f8'),
                             ('avg_gain', 'f8'),
                             ('pos_gain', 'f8'),
                             ('variance', 'f8'),
                             ('std_deviation', 'f8')])

    # construct numpy matrix
    for i, day in enumerate(res['days']):
        date, _, avg_gain, pos_gain, variance, std_deviation = day

        # convert to Unix timestamp
        dt = datetime.datetime(date.year, date.month, date.day)
        timestamp = dt.timestamp()

        matrix[i] = timestamp, avg_gain, pos_gain, variance, std_deviation

    # create the linked plots
    plot_title = "historical_return_sell_date.py, " + \
        instrument.ticker + ", years averaged: " + \
        str(res['year_count']) + ", sell date: " + str(sell_date)

    linked_plot = LinkedPlot(plot_title)
    linked_plot.add_plot()
    linked_plot.add_subplot(matrix, "avg_gain")
    linked_plot.add_plot()
    linked_plot.add_subplot(matrix, "pos_gain")

    if args.variance:
        linked_plot.add_plot()
        linked_plot.add_subplot(matrix, "variance")

    if args.std_deviation:
        linked_plot.add_plot()
        linked_plot.add_subplot(matrix, "std_deviation")

    linked_plot.show()
