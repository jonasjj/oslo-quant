import os

# dir to store downloaded data in
DATA_DIR = os.path.normpath(os.path.dirname(__file__) + "/../../data")

# path to a pickled instances
OSLOBORS_PICKLE_PATH = DATA_DIR + "/oslobors.p"
NASDAQOMX_PICKLE_PATH = DATA_DIR + "/nasdaqomx.p"

# Globals used for avoiding reloading these objects as much as possible.
# Don't access these directly, use getter functions.
_oslobors = None
_nasdaqomx = None
_instruments = None
    
def get_oslobors():
    """
    Get a pickled OsloBors instance""
    
    Return:
       An OsloBors instance
    """
    global _oslobors
    
    # if the object already has been loaded
    if _oslobors is not None:
        return _oslobors

    # load the object from a pickle file
    with open(OSLOBORS_PICKLE_PATH, 'rb') as f:
        import pickle
        _oslobors = pickle.load(f)
        return _oslobors

def get_nasdaqomx():
    """
    Get a pickled NasdaqOmx instance""
    
    Return:
       An NasdaqOmx instance
    """
    global _nasdaqomx

    # if the object already has been loaded
    if _nasdaqomx is not None:
        return _nasdaqomx

    # load the object from a pickle file
    with open(NASDAQOMX_PICKLE_PATH, 'rb') as f:
        import pickle
        _nasdaqomx = pickle.load(f)
        return _nasdaqomx

def get_instruments():
    """
    Get a pickled dict of all instruments in all markets

    Return:
       A dict of instruments indexed by name"""
    global _instruments

    # if the dict has already has been created
    if _instruments is not None:
        return _instruments

    # load all instruments
    oslobors = get_oslobors()
    nasdaqomx = get_nasdaqomx()

    # instruments to merge
    list_of_instruments = [oslobors.instruments,
                           nasdaqomx.instruments]

    # create a new dict containing all instruments for all markets
    _instruments = {}
    count = 0
    for l in list_of_instruments:
        count += len(l)
        _instruments.update(l)

    # check that no items were overwritten
    if len(_instruments) != count:
        raise Exception("There was a duplicate instrument name in two of the merged markets")
        
    return _instruments

def get_instrument(name):
    """
    Get an instrument by name.
    
    Return:
       An instrument with a unique name from one of the markets.

    Raises:
       KeyError: On item not found
    """
    instruments = get_instruments()
    return instruments[name]
