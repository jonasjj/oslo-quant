import argparse

from historical_return_from_to_date import historical_return_from_to_date


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Find the best dates to buy an sell")
    parser.add_argument("instrument", help="Instrument name (ex.: OBX)")
    parser.add_argument("days_between", type=int, help="Days between buy and sell")
    args = parser.parse_args()

    
