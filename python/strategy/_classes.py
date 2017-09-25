from abc import ABCMeta, abstractmethod
from copy import deepcopy
import numpy as np
import datetime

import markets
from . import broker

class Order(object):
    """An order recommendation"""

    def __init__(self, ticker, action, quantity, price=None):
        """
        Args:
           ticker(str): The ticker
           action(str): 'buy' or 'sell'
           quantity(int): The number of shared
           price(float): Limit price or None for market value
        """
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.price = price
        self.filled = False
        self.filled_price = None
        self.cost = None
        
    def __str__(self):
        s = "%s %s %s" % (self.action, self.quantity, self.ticker)
        
        # check if self.price is defined
        if self.price is None:
            s += ", market price"
        else:
            s += ", limit: " + str(self.price)

        if self.filled:
            s += ", filled: " + str(self.filled_price)
            s += ", cost: " + str(self.cost)
            s += ", brokerage: " + str(self.brokerage)
            s += ", total: " + str(self.total)
        else:
            s += ", open"
            
        return s
        
    def fill(self, filled_price):
        """
        Fill this order.
        Typically this function will be called by the simulator.

        Args:
           filled_price(float): The matched price for this order
        """
        self.filled_price = filled_price
        self.filled = True
        self.brokerage = broker.calculate_brokerage(self)
        self.cost = self.quantity * self.filled_price
        self.total = self.cost + self.brokerage

class Share(object):
    """A share holding position"""

    def __init__(self, ticker, quantity, price):
        """
        Args:
           ticker(str): The ticker
           quantity(int): The number of shares (negative for short)
           price(float): The purchase price per share
        """
        self.ticker = ticker
        self.quantity = quantity
        self.price = price

    def get_value(self, date):
        """
        Get the closing value of an instrument at a given date
        The closing value will be used if it exists,
        otherwise the 'value' field will be used.
        Nasdaq OMX data typical doesn't have closing values.

        Args:
           date(datetime.date): Date to get value for

        Return:
           The monetary value of the asset
        """
        instrument = markets.get_instrument(self.ticker)
        
        # if this date doesn't have any data, assume its worth the last known value
        day_data = instrument.get_day_or_last_before(date)

        # preferably use the 'close' field, then the 'value' field
        try:
            current_price = day_data['close']
        except KeyError:
            current_price = day_data['value']

        return self.quantity * current_price
        
class Strategy(object, metaclass=ABCMeta):
    """Base class for all strategies"""

    @abstractmethod
    def __init__(self, money, portfolio, from_date, to_date):
        """
        Override this method and call super()

        Args:
           money(float): Initial liquid assets
           portfolio: Dict of Share objects represening
                      the intital share holding positions
           from_date(datetime.date): First daty of the simulation
           to_date(datetime.date): Last day of the simulation
        """
        self.money = money
        self.portfolio = portfolio
        self.from_date = from_date
        self.to_date = to_date

    @abstractmethod
    def execute(self, today):
        """
        Override this method and call super()

        This method shall assume that we have data only upto the
        trading day before <today>. This method is typically run on
        before the trading opens. A list of order recommendations for
        today shall be returned.
        
        Args:
           today(datetime.date): Present day

        Return:
           A list of Order objects
        """
        self.today = today

    def get_instrument(self, ticker):
        """
        Get an altered version of the instrument which only contains
        date up till today.

        Args:
           ticker(str): Ticker name
        
        Return:
           A deepcopied version of the Instrument object

        Raises:
           ValueError: If the ticker doesn't exist for this date.
                       For instance when trying to get 'NAS.OSE'
                       and today's date is before 2003-12-18.
        """
        # get a copy of the Instrument object which we can modify
        instrument = deepcopy(markets.get_instrument(ticker))

        # Check that this ticker existed at today's date
        first_date = instrument.get_first_date()
        last_date = instrument.get_last_date()
        if self.today < first_date or self.today > last_date:
            raise ValueError("'" + ticker + "' didn't exist at " + str(self.today) + \
                             ", first date: " + str(first_date) + \
                             ", last date: " + str(last_date))

        # We already know that this date exists for this ticker.
        # If there is no date, it means there were no trades this date,
        # Therefore we will look for this date, or the last preceding date.
        row_index = instrument.get_day_index_or_last_before(self.today)

        # delete data which is into the future and the strategy now nothing of
        instrument.data = np.delete(instrument.data, np.s_[row_index + 1:])

        return instrument

    def get_tickers(self):
        """
        Get a list of tickers that exist at today's date

        Return:
           Alphabetically sorted list of tickers
        """
        # All tickers that ever existed
        all_tickers = markets.get_tickers()
        
        todays_tickers = []
        for t in all_tickers:

            # If a ValueError is raised, it mean this ticker doesn't exist today
            try:
                self.get_instrument(t)
                todays_tickers.append(t)
            except ValueError:
                pass

        return todays_tickers
