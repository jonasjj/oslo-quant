from abc import ABCMeta, abstractmethod

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

class Strategy(metaclass=ABCMeta):
    """Base class for all strategies"""

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
        pass
