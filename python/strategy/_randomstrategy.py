from ._classes import Strategy

class RandomStrategy(Strategy):

    def __init__(self, portfolio, from_date, to_date):
        super().__init__(portfolio, from_date, to_date)

    def execute(self, today):
        super().execute(today)

        ticker = self.get_instrument('OBX.OSE')

        import ipdb; ipdb.set_trace()
        
