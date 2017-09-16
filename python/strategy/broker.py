"""
This file contains cost models for the stockbroker (bank)
"""

# The maximum owned assets divided by the portifolio value
MAX_LOAN_RATIO = 0.5

def calculate_interest(balance):
    """
    Calculate the interest for an account balance for 1 day
    
    Args:
       balance(float): The money in the account

    Return:
       The owed or allowed interest
    """
    # Nordnet Mini / Normal / Bonus
    annual_loan_interest_rate_percentage = -0.0605
    annual_deposit_interest_rate_percentage = 0.0

    if balance < 0:
        interest_percentage = annual_loan_interest_rate_percentage
    else:
        interest_percentage = annual_deposit_interest_rate_percentage

    return ((interest_percentage / 100.0) / 365.0) * balance

def calculate_brokerage(order):
    """
    Calculate the brokerage for an order

    Args:
       order(Strategy.Order):
    
    Return:
       Brokerage fees for filling the order
    """
    # Nordnet Mini
    minimum = 49
    percentage = 0.15
    
    # Nordnet Normal
    #minimum = 99
    #percentage = 0.049

    ratio = percentage / 100.0
    cost = ratio * order.quantity * order.price
    if cost < minimum:
        cost = minimum

    return cost
