# dir to store downloaded data in
DATA_DIR = "/home/jonas/quant/data"

# path to a pickled OsloBors instance
PICKLE_PATH = DATA_DIR + "/oslobors.pickle"

# make this class public outside of this package
from markets._oslobors import OsloBors

def get_pickled_oslobors():
    """
    Get a pickled OsloBors instance""
    
    Return:
       An OsloBors instance
    """
    with open(PICKLE_PATH, 'rb') as f:
        import pickle
        return pickle.load(f)
