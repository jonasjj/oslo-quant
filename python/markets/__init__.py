# dir to store downloaded data in
DATA_DIR = "/home/jonas/quant/data"

# path to a pickled instances
OSLOBORS_PICKLE_PATH = DATA_DIR + "/oslobors.p"
NASDAQOMX_PICKLE_PATH = DATA_DIR + "/nasdaqomx.p"

# make this class public outside of this package
from markets._oslobors import OsloBors
from markets._nasdaqomx import NasdaqOmx

def get_oslobors():
    """
    Get a pickled OsloBors instance""
    
    Return:
       An OsloBors instance
    """
    with open(OSLOBORS_PICKLE_PATH, 'rb') as f:
        import pickle
        return pickle.load(f)

def get_nasdaqomx():
    """
    Get a pickled NasdaqOmx instance""
    
    Return:
       An NasdaqOmx instance
    """
    with open(NASDAQOMX_PICKLE_PATH, 'rb') as f:
        import pickle
        return pickle.load(f)

