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

        # let's focus on stocks noted on Oslo Børs
        instruments = self.get_instruments(oslobors=True, nasdaqomx=False)

    def execute(self, today):
        super().execute(today)

        return []