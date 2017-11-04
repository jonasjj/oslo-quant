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

        # how mange trading days into the past we should compare against
        self.compare_days = 20 * 3

        # how often to rebalance the portfolio
        self.rebalancing_days = 20

        # the number of stocks to hold at any given time
        self.number_of_stocks = 3

        # this means the portfolio will be due to rebalancing today
        self.rebalance_date = self.trading_days_ago(self.rebalancing_days)

    def execute(self, today, portfolio):
        super().execute(today, portfolio)

        # if the portfolio is due to rebalancing
        if self.rebalance_date <= self.trading_days_ago(self.rebalancing_days):

            # the date to compare against
            compare_date = self.trading_days_ago(self.compare_days)

            # get the top performers
            top_performers = self.get_top_performers(compare_date,
                                                     self.number_of_stocks)

            # convert list of instruments to list of tickers
            top_tickers = [str(x) for x in top_performers]

            orders = []

            # sell all shared in the portfolio which don't qualify
            for ticker, share in self.portfolio.items():
                if ticker not in top_tickers:
                    o = Order(ticker, "sell", share.quantity)
                    orders.append(o)
            
            # buy all stocks which we don't already own
            for ticker in top_tickers:
                if ticker not in self.portfolio:
                    o = Order(ticker, "buy", 100)
                    orders.append(o)

            self.rebalance_date = today
            return orders

        else:
            return []

    def get_top_performers(self, buy_date, count):
        """
        Get the N top performing stocks within a date interval

        args:
            buy_date(datetime.date): Buy date. Sell date is today
            count(int): Number of top performers to return

        return:
            The N top performing stocks
        """
        sell_date = self.today

        # get a list of all the stocks that exist today
        instruments = self.get_instruments()

        # only include stocks listed on "Oslo Børs"
        instruments = [x for x in instruments if x.exchange == 'Oslo Børs']

        # only include equity, not derivatives
        instruments = [x for x in instruments if x.paper_type == 'Aksjer']

        # keep only instruments that exist today and at the compare date
        instruments = [
            x for x in instruments if x.existed_at_date(buy_date)]

        # list of tuples (gain_ratio, instrument)
        l = []

        # construct the list
        for i in instruments:
            buy = i.get_price(buy_date)
            sell = i.get_price(sell_date)
            gain_ratio = sell / buy
            l.append((gain_ratio, i))

        # sort the list based on gain_ratio
        l.sort(key=lambda x: x[0], reverse=True)

        # keep only the instrument objects
        top_performers = [x[1] for x in l[:count]]

        return top_performers
