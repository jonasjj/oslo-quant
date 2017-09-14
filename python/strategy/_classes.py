from abc import ABCMeta, abstractmethod
from copy import deepcopy
import numpy as np
import datetime

from markets import get_instrument

class Order(object):
    """An order recommendation"""

    def __init__(self, instrument, action, price, quantity):
        """
        Args:
           instrument (markets._classes.Instrument): The instrument
           action (str): 'buy' or 'sell'
           price (float): Limit price
           quantity (int): The number of shared
        """
        self.instrument = instrument
        self.action = action
        self.price = price
        self.quantity = quantity

class Share(object):
    """A share holding position"""

    def __init__(self, instrument, quantity, cost=None):
        """
        Args:
           instrument (markets._classes.Instrument): The instrument
           quantity (int): The number of shares (negative for short)
           cost (float): Optional acquisition cost
        """
        self.instrument = instrument
        self.quantity = quantity
        self.cost = cost    
        
class Strategy(object, metaclass=ABCMeta):
    """Base class for all strategies"""

    @abstractmethod
    def __init__(self, portfolio, from_date, to_date):
        """
        Override this method and call super()

        Args:
           portfolio: List of Share objects represening
                      the intital share holding positions
           from_date(datetime.date): First daty of the simulation
           to_date(datetime.date): Last day of the simulation
        """
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

        # get the row
        timestamp = datetime.datetime(self.today.year,
                                      self.today.month,
                                      self.today.day).timestamp()        
        match_rows = np.where(ticker.data['date'] == timestamp)

        # Check that only one row matches this date
        if len(match_rows[0]) == 0:
            raise Exception("No rows match " + str(today) + " in " + str(ticker))
        elif len(match_rows[0]) > 1:
            raise Exception("More than one row matches " + \
                            str(self.today) + " in " + str(ticker))

        # the index of the single matching row for today's data for this ticker
        row_index = match_rows[0][0]

        # delete data which is into the future and the strategy now nothing of
        ticker.data = np.delete(ticker.data, np.s_[row_index + 1:])
        
        return ticker
        
