from ._classes import Strategy, Order

import random

class RandomStrategy(Strategy):
    """
    This strategy is used for testing the simulator
    """

    def __init__(self, money, portfolio, from_date, to_date):
        super().__init__(money, portfolio, from_date, to_date)

    def execute(self, today):
        super().execute(today)

        random.seed(2)

        # select a random ticker
        instruments = self.get_instruments()
        instrument = random.choice(instruments)

        # random input
        action = random.choice(["buy", "sell"])
        quantity = random.randint(1,100)
        price = instrument.get_price(today)
        if random.random() < 0.2:
            price = None
        
        order = Order(instrument.ticker, action, quantity, price)
        
        return [order]
