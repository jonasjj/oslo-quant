from datetime import datetime
import argparse
from pprint import pprint

from markets import get_instrument

def parse_date(date_str):
    """
    Parse '2015-12-24' string and return datetime object
    
    Raises:
        ValueError on error

    Return:
        datetime.datetime object
    """
    return datetime.strptime(date_str, "%Y-%m-%d")

def find_expected_return_from_to_date(instrument, buy_date, sell_date):

    if buy_date > sell_date:
        raise ValueError("Sell date is before buy date")
    
    # get the first and last timestamp in the available data
    first_timestamp = instrument.get_first_timestamp()
    last_timestamp = instrument.get_last_timestamp()

    # estimate days
    days = (sell_date - buy_date).days

    # rewind to the first available buy date
    _buy_date = buy_date
    _sell_date = sell_date
    while _buy_date > first_timestamp:

        # decrement by 1 year
        _buy_date = datetime(_buy_date.year - 1, _buy_date.month, _buy_date.day)
        _sell_date = datetime(_sell_date.year - 1, _sell_date.month, _sell_date.day)

    # this is the first possible starting point
    _buy_date = datetime(_buy_date.year + 1, _buy_date.month, _buy_date.day)
    _sell_date = datetime(_sell_date.year + 1, _sell_date.month, _sell_date.day)

    if _buy_date < first_timestamp or _sell_date > last_timestamp:
        raise KeyError("Not enough data")
    
    years = []
    accumulated_gain = 0
    while _sell_date <= last_timestamp:

        buy = instrument.get_day_or_first_after(_buy_date)
        sell = instrument.get_day_or_first_after(_sell_date)
        gain = sell ['value'] - buy['value']
        years.append((buy['date'], sell['date'], buy['value'], sell['value'], gain))

        # increment by 1 year
        _buy_date = datetime(_buy_date.year + 1, _buy_date.month, _buy_date.day)
        _sell_date = datetime(_sell_date.year + 1, _sell_date.month, _sell_date.day)

    return years
    
    

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the expected return between dates")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX)")
    parser.add_argument("buy_date", help="Buy date")
    parser.add_argument("sell_date", help="Sell date")
    args = parser.parse_args()

    # get the instrument from the database
    instrument = get_instrument(args.instrument.upper())
    
    buy_date = parse_date(args.buy_date)
    sell_date = parse_date(args.sell_date)

    pprint(find_expected_return_from_to_date(instrument, buy_date, sell_date))
