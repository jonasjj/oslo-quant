#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from historical_return_from_to_date import parse_date
from markets import trading_days
from markets import get_instrument

def simulate(strategy, from_date, to_date):

    # for all trading days between the two dates
    for today in trading_days(from_date, to_date):

        # run the strategy for this date
        orders = strategy.execute(today)

        # process the orders
        for order in orders:

            # make sure we have the full ticker object
            ticker = get_instrument(str(order.ticker))

            # the the market date for this ticker for this date
            ticker_day = ticker.get_day(today)

            order_filled = False

            # assume orders get filled at best price
            if order.action == 'buy':
                if order.price is None:
                    order.filled = True
                    order.filled_price = ticker_day['low']
                elif ticker_day['low'] <= order.price:
                    order.filled = True
                    order.filled_price = ticker_day['low']
            elif order.action == 'sell':
                if order.price is None:
                    order.filled = True
                    order.filled_price = ticker_day['high']
                elif ticker_day['high'] >= order.price:
                    order.filled = True
                    order.filled_price = ticker_day['high']
            else:
                raise Exception("Order.action is neither 'sell' nor 'buy'")

            if order.filled_price:
                print(order)                

if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run a simulation")
    parser.add_argument("strategy", help="The name of the strategy")
    parser.add_argument("money", help="Initial money")
    parser.add_argument("from_date", help="From date: YYYY-MM-DD")
    parser.add_argument("to_date", help="To date: YYYY-MM-DD")
    args = parser.parse_args()

    # load the strategy class
    import strategy    
    try:
        strategy_class = getattr(strategy, args.strategy)        
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

    # create the strategy instance
    strategy = strategy_class(args.money, [], from_date, to_date)
    
    # run the simulation
    simulate(strategy, from_date, to_date)
