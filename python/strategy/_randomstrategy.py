from ._classes import Strategy, Order

class RandomStrategy(Strategy):

    def __init__(self, money, portfolio, from_date, to_date):
        super().__init__(money, portfolio, from_date, to_date)

    def execute(self, today):
        super().execute(today)

        ticker = 'OBX.OSE'

        self.get_tickers()
        
        order = Order(ticker, "buy", 100, 630.0)
        
        return [order]
