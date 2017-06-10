import argparse

def plot():
    from markets import get_instrument
    from plotting import linked_plot
    
    linked_plot([(get_instrument("OBX").data, 'close', 'OBX'),
                 (get_instrument("OMXO20GI").data, 'value', 'omxo20gi'),])

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Plot instruments")

    parser.add_argument('-i', metavar=("TICKER", "COLUMN"), nargs=2, action='append',
                        help="Plot column ('open', 'value', etc.) from instrument")
    args = parser.parse_args()
    print(args)
    
