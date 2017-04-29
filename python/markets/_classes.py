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
    def __init__(self, name, long_name, market):
        super().__init__(name, long_name)
        self.market = market
        self.sector_name = None
        self.data = None
        self.segments = []
        self.netfonds_url = "http://hopey.netfonds.no/paperhistory.php?paper=" + \
                            name + "." + market.name + "&csv_format=sdv"

class Index(Instrument):
    def __init__(self, name, long_name):
        super().__init__(name, long_name)
        self.data = None
        self.tickers = []
        self.netfonds_url = "http://hopey.netfonds.no/paperhistory.php?paper=" + \
                            name + ".OSE&csv_format=sdv"
