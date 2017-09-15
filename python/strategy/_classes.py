from abc import ABCMeta, abstractmethod
from copy import deepcopy
import numpy as np
import datetime

from markets import get_instrument

class Order(object):
    """An order recommendation"""

    def __init__(self, ticker, action, quantity, price=None):
        """
        Args:
           ticker (markets._classes.Ticker): The ticker
           action (str): 'buy' or 'sell'
           quantity (int): The number of shared
           price (float): Limit price or None for market value
        """
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.price = price
        self.filled = False
        self.filled_price = -999999.0
        
    def __str__(self):
        s = "%s %s %s" % (self.action, self.quantity, self.ticker)
        
        # check if self.price is defined
        if self.price is None:
            s += " at market price"
        else:
            s += " limit: " + str(self.price)

        if self.filled:
            s += " filled: " + str(self.filled_price)
            
        return s
        
class Share(object):
    """A share holding position"""

    def __init__(self, ticker, quantity, cost=None):
        """
        Args:
           ticker (markets._classes.Ticker): The ticker
           quantity (int): The number of shares (negative for short)
           cost (float): Optional acquisition cost
        """
        self.ticker = ticker
        self.quantity = quantity
        self.cost = cost    
        
class Strategy(object, metaclass=ABCMeta):
    """Base class for all strategies"""

    @abstractmethod
    def __init__(self, money, portfolio, from_date, to_date):
        """
        Override this method and call super()

        Args:
           money(float): Initial liquid assets
           portfolio: List of Share objects represening
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
           today (datetime.date): Present day

        Return:
           A list of Order objects
        """
        self.today = today

    def get_instrument(self, name):

        # get a copy of the ticker object which we can modify
        ticker = deepcopy(get_instrument(name))

        row_index = ticker.get_day_index(self.today)

        # delete data which is into the future and the strategy now nothing of
        ticker.data = np.delete(ticker.data, np.s_[row_index + 1:])
        
        return ticker
        
