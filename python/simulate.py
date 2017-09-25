#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from historical_return_from_to_date import parse_date
from markets import trading_days
from markets import get_instrument
from strategy import Share
from strategy import broker

def simulate(strategy, money, from_date, to_date):

    # share holding positions {ticker: Share,}
    portfolio = {}

    # for all trading days between the two dates
    for today in trading_days(from_date, to_date):

        # run the strategy for this date
        orders = strategy.execute(today)

        # process the orders
        for order in orders:
            
            # get the instrument object
            instrument = get_instrument(order.ticker)

            # get the market date for this instrument for this date
            try:
                ticker_day = instrument.get_day(today)
            except KeyError:
                ticker_day = None

            # If there was no trading for this ticker on this date
            # we're going to assume that this trade wasn't filled
            if ticker_day is None:
                pass
            
            # assume orders get filled at best price
            elif order.action == 'buy':
                if order.price is None:
                    order.fill(ticker_day['low'])
                elif ticker_day['low'] <= order.price:
                    order.fill(ticker_day['low'])
            elif order.action == 'sell':
                if order.price is None:
                    order.fill(ticker_day['high'])
                elif ticker_day['high'] >= order.price:
                    order.fill(ticker_day['high'])
            else:
                raise Exception("Order.action is neither 'sell' nor 'buy'")

            if order.filled:
                # update the Share object if it exists for this ticker
                try:
                    share = portfolio[order.ticker]
                    new_quantity = share.quantity + order.quantity
                    share.price = ((share.quantity * share.price) + \
                                   (order.quantity * order.price)) / new_quantity
                    share.quantity = new_quantity
                except KeyError:
                    # create a new share object
                    share = Share(order.ticker, order.quantity, order.filled_price)
                    portfolio[order.ticker] = share
                
                money -= order.total
            
            interest = broker.calculate_interest(money)
            money += interest

        # calculate the current market value
        portfolio_value = money
        for share in portfolio.values():
            share_value = share.get_value(today)
            portfolio_value += share_value

        # the total value of the account
        account_value = money + portfolio_value
        
        loan_ratio = broker.calculate_loan_ratio(account_value, portfolio_value)
        if loan_ratio < broker.MIN_LOAN_TO_VALUE_RATIO:
            raise Exception("Loan-to-value-ratio is too low: " + str(loan_ratio))

        # print a message summary of today
        print("%s: account_value: %.0f, money: %.0f, interest: %.0f" % \
              (str(today), account_value, money, interest))
        indent = len(str(today)) + 2
        for order in orders:
            print(' ' * indent + str(order))
            
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

    money = float(args.money)

    # create the strategy instance
    strategy = strategy_class(money, [], from_date, to_date)
    
    # run the simulation
    simulate(strategy, money, from_date, to_date)
