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

    if buy_date > sell_date:
        raise ValueError("Sell date is before buy date")
    
    # get the first and last timestamp in the available data
    first_timestamp = datetime.fromtimestamp(instrument.data[0]['date'])
    last_timestamp = datetime.fromtimestamp(instrument.data[-1]['date'])

    # days of available data
    #days_data = (last_timestamp - first_timestamp).days

    # estimate days
    days = (sell_date - buy_date).days

    # go to the first available start date
    start_date = datetime(first_timestamp.year, buy_date.month, buy_date.day)
    if start_date < first_timestamp:
        start_date = datetime(start_date.year + 1, start_date.month, start_date.day)

    # go to the first available sell date
    end_date = datetime(
        (sell_date.year - buy_date.year) + start_date.year,
        sell_date.month,
        sell_date.day)

    
    import ipdb; ipdb.set_trace()
    years = []
    while end_date <= last_timestamp:
        
        
        years.append((start_date.year,))

        # increment by 1 year
        start_date = datetime(start_date.year + 1, start_date.month, start_date.day)
        end_date = datetime(end_date.year + 1, end_date.month, end_date.day)
    

    

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
