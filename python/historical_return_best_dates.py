import argparse
import datetime
from tabulate import tabulate

from markets import get_instrument
from historical_return_from_to_date import historical_return_from_to_date

def historical_return_dates(instrument,
                            days_between,
                            first_date=datetime.date(2017,1,2),
                            last_date=datetime.date(2017,12,31),
                            average_days=1):
    """"
    Find the historically best dates to buy and sell
    
    Args:
        instrument (markets.Instrument): Instrument to use in check
        days_between (int): Approximate number of days between buy and sell
        first_date (datetime.date): First date to check
        last_date (datetime.date): Last date to check
        average_days (int): Moving average over N days

    Return:
        dict with three list:
           - sorted by date
           - sorted by average gain ratio
           - sorted by change of positive gain ratio:

            {'days':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'avg_gain_ratio': 
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..],
             'pos_gain':
                [(buy_date, sell_date, avg_gain_ratio, pos_gain_ratio),..]}
    """
    tmp_results = []

    # find out how many days before and after each date we need
    # to implement calculate the moving average
    before_days = int((average_days - 1) / 2)
    after_days = int(average_days - before_days - 1)
    
    date = first_date - datetime.timedelta(days=before_days)

    # loop through all the days in the time range
    while date <= last_date + datetime.timedelta(days=after_days):

        buy_date = date
        sell_date = buy_date + datetime.timedelta(days=days_between)

        d = historical_return_from_to_date(instrument, buy_date, sell_date)

        tmp_results.append((buy_date,
                            sell_date,
                            d['avg_gain_ratio'],
                            d['pos_gain_ratio']))
        
        date += datetime.timedelta(days=1)

    # store year count of the source data
    year_count = d['year_count']

    # calculate the moving average for all days
    results = []
    for i in range(len(tmp_results) - before_days - after_days):

        # find the index of this day within tmp_results
        index = i + before_days

        # find the buy/sell dates for this date
        buy_date, sell_date, _, _ = tmp_results[index]

        # calculate the moving average values for this day
        acc_avg_gain_ratio = 0
        acc_pos_gain_ratio = 0
        for j in range(index - before_days, index + after_days + 1):
           _, _, avg_gain_ratio, pos_gain_ratio = tmp_results[j]
           acc_avg_gain_ratio += avg_gain_ratio
           acc_pos_gain_ratio += pos_gain_ratio

        day_count = before_days + after_days + 1

        t = (buy_date,
             sell_date,
             acc_avg_gain_ratio / day_count,
             acc_pos_gain_ratio / day_count)
             
        results.append(t)
        
    # sort by column a, then by column b
    avg_gain_list = sorted(results, key=lambda x: (x[2], x[3]), reverse=True)
    pos_gain_list = sorted(results, key=lambda x: (x[3], x[2]), reverse=True)
    
    d = {'days': results,
         'year_count': year_count,
         'avg_gain_ratio': avg_gain_list,
         'pos_gain_ratio': pos_gain_list}
    
    return d

def _print(results):
    """Print a tabulated list"""

    tab_list = []

    decimals = 4

    for r in results:
        tab_list.append((str(r[0]),
                         str(r[1]),
                         str(round(r[2], decimals)),
                         str(round(r[3], decimals))))

    print(tabulate(tab_list, headers=("Buy date",
                                      "Sell date",
                                      "Avg. gain ratio",
                                      "Pos. gain ratio")))

if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the best dates to buy an sell")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX)")
    parser.add_argument("days_between", type=int, help="Days between buy and sell")
    parser.add_argument("--avg_gain",
                        action='store_true',
                        help="Sorted by average gain ratio")
    parser.add_argument("--pos_gain",
                        action='store_true',
                        help="Sorted by number of years with positive gain")
    parser.add_argument("--worst",
                        action="store_true",
                        help="Find the worst dates instead of the best dates")
    parser.add_argument("--topn",
                        metavar="N",
                        type=int,
                        default=-1,
                        help="Show the top N entires only")
    parser.add_argument("--avg",
                        metavar="N",
                        type=int,
                        default=1,
                        help="Moving average with N values")
    parser.add_argument("--plot",
                        action="store_true",
                        help="Plot the results")
    args = parser.parse_args()
    
    # get the instrument from the database
    instrument = get_instrument(args.instrument.upper())

    # run the algorithm
    res = historical_return_dates(instrument, args.days_between, average_days=args.avg)
    
    # get the result lists
    avg_gain_list = res['avg_gain_ratio']
    pos_gain_list = res['pos_gain_ratio']
    
    # Determine whether to present the best or the worst days
    if args.worst:

        best_or_worst_string = "Worst"

        # show the worst days at the top of the list [0]
        avg_gain_list.reverse()
        pos_gain_list.reverse()

    else:
        best_or_worst_string = "Best"
        
    if args.avg_gain:
        print("\n%s dates sorted by average gain" % best_or_worst_string)            
        _print(avg_gain_list[:args.topn -1])
            
    if args.pos_gain:
        print("\n%s dates sorted by change of positive gain gain" % best_or_worst_string)
        _print(pos_gain_list[:args.topn -1])

    if args.plot:
        import numpy as np
        from plotting import linked_plot

        # create empty numpy matrix with room for all values
        matrix = np.zeros(shape=len(res['days']),
                          dtype=[('date', 'f8'),
                                 ('avg_gain', 'f8'),
                                 ('pos_gain', 'f8')])
                        
        # construct numpy matrix
        for i,day in enumerate(res['days']):
            date, _, avg_gain, pos_gain = day

            # convert to Unix timestamp
            dt = datetime.datetime(date.year, date.month, date.day)
            timestamp = dt.timestamp()
            
            matrix[i] = timestamp, avg_gain, pos_gain

        plot_inputs = []

        # string for plot titles
        if args.avg == 1:
            average_days_string = ""
        else:
            average_days_string = " (moving average days: %d)" % args.avg

        # add average gain ratio to ploit
        if args.avg_gain:
            plot_inputs.append((matrix, 'avg_gain',
                                "Average gain ratio for " +
                                instrument.name + average_days_string +
                                ", years averaged: " + str(res['year_count'])))

        # add positive gain ratio to plot
        if args.pos_gain:
            plot_inputs.append((matrix, 'pos_gain',
                                "Positive gain ratio for " +
                                ", years averaged: " + str(res['year_count'])))

        # create the plot
        linked_plot(plot_inputs)
