"""
This file contains cost models for the stockbroker (bank)
"""

# The minimum loan-to-value-ratio
MIN_LOAN_TO_VALUE_RATIO = 0.5

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
    cost = ratio * order.quantity * order.filled_price
    if cost < minimum:
        cost = minimum

    return cost

def calculate_loan_ratio(account_value, portfolio_value):
    """ Calculate the loan-to-value ratio for an account

    Args:
       account_value(float):
       portfolio_value(float):
    
    Return(float):
       A value between 0 and 1.0
       1.0 means no loans, and 0.0 means that all assets are loaned
    """
    if account_value <= 0:
        raise Exception("The account value is negative or zero")
    elif account_value > portfolio_value:
        return 1.0
    else:
        return account_value / portfolio_value


