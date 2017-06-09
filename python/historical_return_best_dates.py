import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

from markets import get_instrument
from historical_return_from_to_date import historical_return_from_to_date

def _historical_return_dates(instrument,
                             days_between):
    """"
    Find the historically best dates to buy and sell
    
    Args:
        instrument (markets.Instrument): Instrument to use in check
        days_between (int): Approximate number of days between buy and sell

    Return:
        unsorted list of tuples where:
            [(buy_date, avg_gain_ratio, pos_gain_ratio),..]
    """
    year = 2017
    date = datetime(year, 1, 1)

    results = []
    
    # loop through all the days in one year
    while date.year == year:

        buy_date = date
        sell_date = buy_date + timedelta(days=days_between)

        d = historical_return_from_to_date(instrument, buy_date, sell_date)

        results.append((buy_date, d['avg_gain_ratio'], d['pos_gain_ratio']))
        
        date += timedelta(days=1)

    return results

def historical_return_best_dates_by_avg_gain_ratio(instrument,
                                                   days_between):
    
    results = _historical_return_dates(instrument, days_between)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def historical_return_best_dates_by_pos_gain_ratio(instrument,
                                                   days_between):
    
    results = _historical_return_dates(instrument, days_between)
    results.sort(key=lambda x: x[2], reverse=True)
    return results

def _print(results):
    tab_list = []

    decimals = 4
    
    for r in results:
        tab_list.append((r[0].strftime("%Y-%m-%d"),
                         str(round(r[1], decimals)),
                         str(round(r[2], decimals))))

    print(tabulate(tab_list, headers=("Date", "avg_gain_ratio", "pos_gain_ratio")))
    
if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the best dates to buy an sell")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX)")
    parser.add_argument("days_between", type=int, help="Days between buy and sell")
    parser.add_argument("--avg_gain",
                        action='store_true',
                        help="Sorted by average gain ratio per year")
    parser.add_argument("--pos_gain",
                        action='store_true',
                        help="Sorted by number of years with positive gain")
    topn_default = 5
    parser.add_argument("--topn",
                        metavar="N",
                        type=int,
                        default=topn_default,
                        help="Show the top N entires only. Default: " + str(topn_default))
    args = parser.parse_args()
    
    # get the instrument from the database
    instrument = get_instrument(args.instrument.upper())
    
    if args.avg_gain:
        print("\nBest dates sorted by average gain")
        res = historical_return_best_dates_by_avg_gain_ratio(instrument,
                                                             args.days_between)
        _print(res[:args.topn -1])
            
    if args.pos_gain:
        print("\nBest dates sorted by change of positive gain gain")
        res = historical_return_best_dates_by_pos_gain_ratio(instrument,
                                                             args.days_between)
        _print(res[:args.topn -1])
