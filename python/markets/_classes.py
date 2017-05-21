from datetime import datetime

"""
File containing classes for markets, indexes and tickers
"""
class Instrument(object):
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_first_timestamp(self):
        """
        Get the first data item for this instrument
        
        Return:
           datetime.datetime
        """
        return datetime.fromtimestamp(self.data[0]['date'])

    def get_last_timestamp(self):
        """
        Get the last data item for this instrument
        
        Return:
           datetime.datetime
        """
        return datetime.fromtimestamp(self.data[-1]['date'])

    def get_day(self, date):
        raise NotImplementedError

class Market(Instrument):
    def __init__(self, name, long_name):
        super().__init__(name, long_name)
        self.tickers = []

class Ticker(Instrument):
    def __init__(self, name, long_name, market, url):
        super().__init__(name, long_name)
        self.market = market
        self.sector_name = None
        self.data = None
        self.segments = []
        self.url = url

class Index(Instrument):
    def __init__(self, name, long_name, url):
        super().__init__(name, long_name)
        self.data = None
        self.tickers = []
        self.url = url
