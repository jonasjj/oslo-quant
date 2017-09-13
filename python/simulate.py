#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from historical_return_from_to_date import parse_date

def simulate(strategy, from_date, to_date):
    pass

if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run a simulation")
    parser.add_argument("strategy", help="The name of the strategy")
    parser.add_argument("from_date", help="From date: YYYY-MM-DD")
    parser.add_argument("to_date", help="To date: YYYY-MM-DD")
    args = parser.parse_args()

    # load the strategy
    import strategy    
    try:
        strategy = getattr(strategy, args.strategy)
    except AttributeError:
        print('Could not import ' + args.strategy + ' from strategy')
        print("Available strategies are:")

        # print all items from the strategy module that end with "Strategy"
        for attr in dir(strategy):
            if attr.endswith("Strategy"):
                print("   " + attr)
                sys.exit(1)
    
    # parse the from/to dates
    from_date = parse_date(args.from_date)
    to_date = parse_date(args.to_date)

    # run the simulation
    simulate(strategy, from_date, to_date)
