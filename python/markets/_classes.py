from datetime import datetime
import numpy as np

"""
File containing classes for markets, indexes and tickers
"""
class Instrument(object):
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_first_timestamp(self):
        """
        Get the first data item for this instrument
        
        Return:
           datetime.datetime
        """
        return datetime.fromtimestamp(self.data[0]['date'])

    def get_last_timestamp(self):
        """
        Get the last data item for this instrument
        
        Return:
           datetime.datetime
        """
        return datetime.fromtimestamp(self.data[-1]['date'])

    def _get_row(self, index):
        """
        Get the data row with index

        Return
           Dict containing data for this row index

        Raises:
           IndexError if the row index doesn't exist
        """
        # get the row values
        row_values = self.data[index]
        
        # create the return dict
        column_names = self.data.dtype.names
        d = dict(zip(column_names, row_values))
        
        # translate timestamp date to datetime
        d['date'] = datetime.fromtimestamp(d['date'])

        return d

    def get_day(self, date):
        """
        Get the data for a specific date.
        
        Return:
           Dict containing data for this date

        Raises:
           KeyError if there is no data for this date
        """
        # get matching rows
        matches = np.where(self.data['date'] == date.timestamp())[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError("Date not found :" + str(date))

        # if there was exactly one matching row
        elif match_count == 1:
            # get the index of the matching row
            row_index = matches[0]

            return self._get_row(row_index)
            
        # if there were more than one matching row
        else:
            # There must be something wrong in the database, which one should we return?
            raise Exception("There was more than one matching row")
        
    def get_day_or_first_after(self, date):
        """
        Get the data for the first date after
        
        Return:
           Dict containing data for this or the next day with available data

        Raises:
           KeyError if there is no data for this or later dates
        """
        # get matching rows
        matches = np.where(self.data['date'] >= date.timestamp())[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError("Date not found :" + str(date))
        else:
            # get the index of the first matching row
            row_index = matches[0]

            return self._get_row(row_index)

    def get_day_or_last_before(self, date):
        """
        Get the data for the first date before
        
        Return:
           Dict containing data for this or the last day with available data

        Raises:
           KeyError if there is no data for this or previous dates
        """
        # get matching rows
        matches = np.where(self.data['date'] <= date.timestamp())[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError("Date not found :" + str(date))
        else:
            # get the index of the last matching row
            row_index = matches[-1]

            return self._get_row(row_index)

class Market(Instrument):
    def __init__(self, name, long_name):
        super().__init__(name, long_name)
        self.tickers = []

class Ticker(Instrument):
    def __init__(self, name, long_name, market, url):
        super().__init__(name, long_name)
        self.market = market
        self.sector_name = None
        self.data = None
        self.segments = []
        self.url = url

class Index(Instrument):
    def __init__(self, name, long_name, url):
        super().__init__(name, long_name)
        self.data = None
        self.tickers = []
        self.url = url
