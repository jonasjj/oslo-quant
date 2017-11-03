import datetime

from ._classes import Strategy, Order


class MomentumStrategy(Strategy):
    """
    This momentum strategy picks the N top performing stocks over a
    fixed period leading up to preset day. The N top performers are
    held for a fixed period, then the portfolio is rebalanced.

    The rationale is that stocks that are have been bullish recently
    are likely to continue the bullish trend for some time.

    This strategy is based on this article:
    http://business.nasdaq.com/marketinsite/2017/Momentum-Demystified.html
    """

    def __init__(self, money, portfolio, from_date, to_date):
        super().__init__(money, portfolio, from_date, to_date)

        # how long into the past we should compare against
        self.compare_delta = datetime.timedelta(days=30 * 3)

        # the number of stocks to hold at any given time
        self.number_of_stocks = 3

    def execute(self, today):
        super().execute(today)

        # the date to compare against
        compare_date = today - self.compare_delta

        # let's focus on stocks noted on Oslo Børs (that exist at from_date)
        instruments = self.get_instruments(oslobors=True, nasdaqomx=False)

        # keep only instruments that exist today, and existed at the compare date
        instruments = [x for x in instruments if x.existed_at_date(compare_date)]

        return []
