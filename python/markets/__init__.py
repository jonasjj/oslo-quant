import os
import numpy as np
import datetime

# dir to store downloaded data in
DATA_DIR = os.path.normpath(os.path.dirname(__file__) + "/../../data")

# path to a pickled instances
OSLOBORS_PICKLE_PATH = DATA_DIR + "/oslobors.p"
NASDAQOMX_PICKLE_PATH = DATA_DIR + "/nasdaqomx.p"

# Globals used for avoiding reloading these objects as much as possible.
# Don't access these directly, use getter functions.
_oslobors = None
_nasdaqomx = None
_instruments = None
    
def get_oslobors():
    """
    Get the pickled Oslo Exchange data
    
    Return:
       A Market instance

    Raises:
       FileNotFoundError if the pickle isn't found
    """
    global _oslobors
    
    # if the object already has been loaded
    if _oslobors is not None:
        return _oslobors

    # load the object from a pickle file
    with open(OSLOBORS_PICKLE_PATH, 'rb') as f:
        import pickle
        _oslobors = pickle.load(f)
        return _oslobors

def get_nasdaqomx():
    """
    Get the pickled NasdaqOMX data
    
    Return:
       A Market instance

    Raises:
       FileNotFoundError if the pickle isn't found
    """
    global _nasdaqomx

    # if the object already has been loaded
    if _nasdaqomx is not None:
        return _nasdaqomx

    # load the object from a pickle file
    with open(NASDAQOMX_PICKLE_PATH, 'rb') as f:
        import pickle
        _nasdaqomx = pickle.load(f)
        return _nasdaqomx

def get_instruments(oslobors=True, nasdaqomx=True):
    """
    Get a pickled dict of all instruments in all markets.
    If a market's pickle file isn't found, it will be omitted.

    Args:
        oslobors(bool): Include stocks listed on Oslo Børs
        nasdaqomx(bool): Include stocks listed on Nasdaq OMX

    Return:
       A dict of instruments indexed by name"""
    global _instruments

    # if the dict has already has been created
    if _instruments is not None:
        return _instruments.copy()

    # markets to merge
    list_of_markets = []

    # load all instruments if the pickle files exist
    if oslobors:
        oslobors_stocks = get_oslobors()
        list_of_markets.append(oslobors_stocks)
    
    if nasdaqomx:
        nasdaqomx_stocks = get_nasdaqomx()
        list_of_markets.append(nasdaqomx_stocks)

    # create a new dict containing all instruments for all markets
    _instruments = {}
    for market in list_of_markets:
        for instrument in market.instruments:

            # check that no items are overwritten
            if instrument.ticker in market.instruments:
                raise Exception("There are duplicate instrument names in two of the merged markets")       
            else:
                _instruments[instrument.ticker] = instrument
            
    return _instruments.copy()

def get_instrument(ticker):
    """
    Get an instrument by ticker name.
    
    Args:
       ticker(str): Ticker name

    Return:
       An instrument with a unique name from one of the markets.

    Raises:
       KeyError: On item not found
    """
    instruments = get_instruments()
    return instruments[ticker]

def get_tickers(oslobors=True, nasdaqomx=True):
    """
    Get a list of all the tickers in all markets sorted alphabetically
    
    Return:
       A list of str
    """
    instruments = get_instruments()
    tickers = list(instruments)
    tickers.sort()
    return tickers

def is_trading_day(date, ticker='OBX.OSE'):
    """
    Check if this is a trading day
    
    Args:
       date(datetime.date): The date to check for
       ticker(str): Name of ticker to check for

    Return:
       True if the date is a trading day, else False

    Raises:
       KeyError: On item not found
    """
    instrument = get_instrument(ticker)
    
    # If get_day_index() succeeds, this must be a trading day
    try:
        instrument.get_day_index(date)
        return True
    except KeyError:
        return False

def trading_days(from_date, to_date, ticker='OBX.OSE'):
    """
    Find the closed interval of trading days between two dates

    Args:
       from_date(datetime.date):
       to_date(datetime.date):
       ticker(str): Name of ticker to check for

    Yields:
       datetime.date objects
    """
    trading_days = []
    date = from_date

    while date <= to_date:
        if is_trading_day(date, ticker):
            yield date
        date += datetime.timedelta(days=1)
