# -*- coding: utf-8 -*-

import pickle
import os
import progressbar
import gzip
from urllib.request import urlopen

from markets._classes import Index
from markets import DATA_DIR, NASDAQOMX_PICKLE_PATH

class NasdaqOmx(object):
    def __init__(self):
        
        # construct paths
        self._indexes_dir = os.path.join(DATA_DIR, "indexes")

        base_url = "https://indexes.nasdaqomx.com/Index/ExportHistory/%s?startDate=2000-01-01T00:00:00.000&endDate=2050-01-01T00:00:00.000&timeOfDay=EOD"
        
        
        # dict containing all instruments indexed by name
        self.indexes = {"OMXO20GI": Index("OMXO20GI",
                                          "OMX Oslo 20 Gross Index",
                                          base_url % "OMXO20GI"),
                        "OMXS30": Index("OMXS30",
                                        "OMX Stockholm 20 Index",
                                        base_url % "OMXS30"),
                        "OMXH25" : Index("OMXH25",
                                         "OMX Helsinki 25",
                                          base_url % "OMXH25"),
                        "OMXC20CAP" : Index("OMXC20CAP",
                                            "OMX Copenhagen 20 CAP",
                                            base_url % "OMXC20CAP"),
                        }

        self.instruments = self.indexes
    
    def __str__(self):
        return "Nasdaq OMX"

    def _download_gz(self, url, dest_file):
        """
        Download file from url to path dest_file.
        The file will be in gzip format
        """
        data = urlopen(url).read()
        
        with gzip.GzipFile(dest_file, "wb") as f:
            f.write(data)

    def download(self):
        """
        Download the daily history for all tickers and indexes from nasdaqomx.com
        DATA_DIR is used for target dir.
        Overwrites existing files.
        """

        # create dir
        if not os.path.isdir(self._indexes_dir):
            os.makedirs(self._indexes_dir)

        # list of tuples with (url, dest_file) to download
        download_list = []
                    
        # add indexes to download list
        for index in self.indexes.values():
            index_file = os.path.join(self._indexes_dir, index.name)
            
            download_list.append((index.url, index_file))

        # create progressbar
        bar = progressbar.ProgressBar(maxval=len(download_list))
        bar.start()

        # download all files in the list
        for i, (url, dest_file) in enumerate(download_list):
            self._download_gz(url, dest_file + ".xlsx.gz")
            bar.update(i)

        bar.finish()
        print("Downloaded " + str(i) + " files to " + DATA_DIR)

    def _load_file(self, file_path):
        """
        Load the file.
        
        Return:
           A numpy named array
        """
        pass
        
    def load(self):
        """
        Load files from DATA_DIR
        """
        pass
        
    def pickle(self):
        """
        Pickle this object to NORDNETOMX_PICKLE_PATH
        """
        with open(NORDNETOMX_PICKLE_PATH, "wb" ) as f:
            pickle.dump(self,  f)
