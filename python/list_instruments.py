import sys
from pprint import pprint

from markets import get_instruments

def list_instruments(query_strings=[]):
    """
    Print a formatted list of all available instruments or instruments
    that contain a word from a list of words in the ticker name or long name.
    If no query strings are given, all instruments will be printed.

    Args:
       query_strings: Iterable of words to look for.
                      The matching will use the OR function.
    """
    instruments = get_instruments()

    # list of tuples: [(name, long_name),]
    matches = []
    
    for name in sorted(instruments):
        long_name = instruments[name].long_name
        
        # if one or more query strings were given
        if len(query_strings) > 0:            
        
            for s in query_strings:
                
                su = s.upper() 
                if su in name.upper() or su in long_name.upper():
                    matches.append((name, long_name))
                    break
                
        # if no query strings were specifies
        else:            
            # match all instruments
            matches.append((name, long_name))

    # find the width of the first column
    width = 0
    for m in matches:
        width = max(width, len(m[0]))
        
    # print the matches in equal width columns
    f = "%-" + str(width) + "s - %s"
    for t in matches:
        print(f % t)
            
list_instruments(sys.argv[1:])
