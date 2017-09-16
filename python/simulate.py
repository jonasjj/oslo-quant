#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from historical_return_from_to_date import parse_date
from markets import trading_days
from markets import get_instrument
from strategy import Share

# The maximum owned assets divided by the portifolio value
MAX_LOAN_RATIO = 0.5

def calculate_interest(balance):
    """
    Calculate the interest for an account balance for 1 day
    
    Args:
       balance(float): The money in the account

    Return:
       The owed or allowed interest
    """
    # Nordnet Mini / Normal / Bonus
    annual_loan_interest_rate_percentage = -0.0605
    annual_deposit_interest_rate_percentage = 0.0

    if balance < 0:
        interest_percentage = annual_loan_interest_rate_percentage
    else:
        interest_percentage = annual_deposit_interest_rate_percentage

    return ((interest_percentage / 100.0) / 365.0) * balance

def calculate_brokerage(order):
    """
    Calculate the brokerage for an order

    Args:
       order(Strategy.Order):
    
    Return:
       Brokerage fees for filling the order
    """
    # Nordnet Mini
    minimum = 49
    percentage = 0.15
    
    # Nordnet Normal
    #minimum = 99
    #percentage = 0.049

    ratio = percentage / 100.0
    cost = ratio * order.quantity * order.price
    if cost < minimum:
        cost = minimum

    return cost

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

            # the the market date for this instrument for this date
            ticker_day = instrument.get_day(today)

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

            cost = order.quantity * order.price
            brokerage = calculate_brokerage(order)
            interest = calculate_interest(money)

            money -= cost
            money -= brokerage
            money += interest

            # print a message
            s = str(order)
            if(order.filled):
                s += ", brokerage: %.0f, cost: %.0f, interest: %.0f, money: %.0f" % \
                     (brokerage, cost, interest, money)
            print(s)

        # calculate the current market value
        portfolio_value = money
        for share in portfolio:
            share_value = share.get_value(today)
            portfolio_value += share_value

        account_value = money + portfolio_value
            
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
