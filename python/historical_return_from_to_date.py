from datetime import datetime
import argparse

from markets import get_pickled_oslobors

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
    import ipdb; ipdb.set_trace()
    

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the expected return between dates")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX)")
    parser.add_argument("buy_date", help="Buy date")
    parser.add_argument("sell_date", help="Sell date")
    args = parser.parse_args()

    # load the instrument from the database
    oslobors = get_pickled_oslobors()
    instrument = oslobors.instruments[args.instrument]
    
    buy_date = parse_date(args.buy_date)
    sell_date = parse_date(args.sell_date)

    print(find_expected_return_from_to_date(instrument, buy_date, sell_date))
