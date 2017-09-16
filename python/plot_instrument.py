#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from markets import get_instrument
from plotting import linked_plot

def plot(ticker_columns):
    """
    Args:
       ticker_columns (list): Tickers and ticker  columns to plot.
          This argument must be an iterable on the format:
             [[instrument_ticker_a, column_name_a],
              [instrument_ticker_b, column_name_b],
              ...]          
    """

    # create linked_plot() arguments
    l = []
    for instrument_name, column_name in ticker_columns:
        instrument = get_instrument(instrument_name.upper())
        plot_title = instrument_name.upper() + "_" + column_name
        l.append((instrument.data, column_name, plot_title))

    # create the plot
    linked_plot(l)

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot instruments")

    parser.add_argument('-i', metavar=("TICKER", "COLUMN"), nargs=2, action='append',
                    help=("Plot column ('open', 'value', etc.) from ticker."
                          " Several ticker/column sets may be specified."
                          " Example: \"-i STL.OSE open -i NAS.OSE open\""))
    args = parser.parse_args()

    if args.i is None:
        print("No tickers and columns specified. Try --help")
    else:
        plot(args.i)
    
    
