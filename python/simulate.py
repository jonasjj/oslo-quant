#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import numpy as np
import datetime

from historical_return_from_to_date import parse_date
from markets import trading_days
from markets import get_instrument
from strategy import Share
from strategy import broker
from plotting import LinkedPlot


def simulate(strategy, money, from_date, to_date, reference):

    # the number of shares we could have bought from the reference instrument
    reference_shares = money / reference.get_price(from_date)

    # share holding positions {ticker: Share,}
    portfolio = {}

    # log what the strategy is doing by appending tuples:
    strategy_log = []

    # info about what the strategy is doing on the format tuple(date, str)
    action_markers = []

    # for all trading days between the two dates
    for today in trading_days(from_date, to_date):

        # label text to show for this day in the plot
        action_label = None

        # run the strategy for this date
        orders = strategy.execute(today, portfolio, money)

        # process the orders
        for order in orders:

            # get the instrument object
            instrument = get_instrument(order.ticker)

            # get the market date for this instrument for this date
            try:
                ticker_day = instrument.get_day(today)
            except KeyError:
                ticker_day = None

            # assume orders get filled at average price
            average_price = instrument.get_price(today)

            # If there was no trading for this ticker on this date
            # we're going to assume that this trade wasn't filled
            if ticker_day is None:
                pass

            # try to fill orders
            elif order.action == 'buy':
                if order.price is None:
                    order.fill(average_price)
                elif average_price <= order.price:
                    order.fill(average_price)
                money -= order.total
            elif order.action == 'sell':
                if order.price is None:
                    order.fill(average_price)
                elif average_price >= order.price:
                    order.fill(average_price)
                money += order.total
            else:
                raise Exception("Order.action is neither 'sell' nor 'buy'")

            if order.filled:

                # update the action label for the plot
                if action_label is None:
                    action_label = ""
                else:
                    action_label += "\n"
                action_label += order.action + " " + \
                    order.ticker + " " + str(order.filled_price)

                # update the Share object if it exists for this ticker
                try:
                    share = portfolio[order.ticker]

                    # the new number of shares of this stock we own now
                    if order.action == 'sell':
                        new_quantity = share.quantity - order.quantity
                    else:
                        new_quantity = share.quantity + order.quantity

                        share.price = ((share.quantity * share.price) +
                                       (order.quantity * order.filled_price)) / new_quantity

                    share.quantity = new_quantity

                    if new_quantity == 0:
                        portfolio.pop(order.ticker)

                except KeyError:
                    # create a new share object
                    share = Share(order.ticker, order.quantity,
                                  order.filled_price)
                    portfolio[order.ticker] = share

        interest = broker.calculate_interest(money)
        money += interest

        # calculate the current market value
        portfolio_value = 0
        for share in portfolio.values():
            share_value = share.get_value(today)
            portfolio_value += share_value

        # the total value of the account
        account_value = money + portfolio_value

        loan_ratio = broker.calculate_loan_ratio(
            account_value, portfolio_value)
        if loan_ratio < broker.MIN_LOAN_TO_VALUE_RATIO:
            print("Loan-to-value-ratio is too low: " + str(loan_ratio))
            break

        # calculate the value of the reference shares
        reference_value = reference_shares * reference.get_price(today)

        # add an entry to the log for today
        strategy_log.append((today,
                             account_value,
                             money,
                             portfolio_value,
                             loan_ratio,
                             reference_value))

        if action_label is not None:
            action_markers.append((today, action_label))

        # print a message summary of today
        print("%s: reference_value: %.0f, account_value: %.0f, money: %.0f, interest: %.0f" %
              (str(today), reference_value, account_value, money, interest))
        indent = len(str(today)) + 2
        for order in orders:
            print(' ' * indent + str(order))

    matrix = np.array(strategy_log, dtype=[('date', 'O'),
                                           ('account_value', 'f8'),
                                           ('money', 'f8'),
                                           ('portfolio_value', 'f8'),
                                           ('loan_ratio', 'f8'),
                                           ('reference_value', 'f8')])

    # create a plot showing the behavior of the strategy
    plot = LinkedPlot(window_title=str(strategy))
    plot.add_plot("Account value", title_above=False)
    plot.add_subplot(matrix, "account_value", "Account value")
    plot.add_subplot(matrix, "reference_value", str(reference))

    for date, text in action_markers:
        plot.add_marker(date,
                        "Account value",
                        "account_value",
                        "Account value",
                        text=text)

    plot.show()


if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run a simulation")
    parser.add_argument("strategy", help="The name of the strategy")
    parser.add_argument("money", help="Initial money")
    parser.add_argument("from_date", help="From date: YYYY-MM-DD")
    parser.add_argument("to_date", help="To date: YYYY-MM-DD")
    parser.add_argument("reference", help="Reference instrument (ex: OBX.OSE)")
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

    # get the reference instument
    reference = get_instrument(args.reference.upper())

    # run the simulation
    simulate(strategy, money, from_date, to_date, reference)
