"""
File containing classes for markets, indexes and tickers
"""
class Instrument(object):
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        
    def __str__(self):
        return self.long_name

    def __repr__(self):
        return self.name

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
