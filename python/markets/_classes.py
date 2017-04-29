"""
File containing classes for markets, indexes and tickers
"""
class Market(object):
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        self.tickers = []

class Ticker(object):
    def __init__(self, name, long_name, market):
        self.name = name
        self.long_name = long_name
        self.market = market

