import datetime
import numpy as np

"""
File containing classes for markets and instruments
"""


class Instrument(object):
    def __init__(self, ticker, long_name, data):
        """
        Args:
           ticker(str): Ticker name
           long_name(str): Full name
           data:(numpy.array): Numpy matrix with named columns
        """
        self.ticker = ticker
        self.long_name = long_name
        self.data = data

    def __str__(self):
        return self.ticker

    def __repr__(self):
        return self.ticker

    def get_first_date(self):
        """
        Get the first data item for this instrument

        Return:
           datetime.date
        """
        return datetime.date.fromtimestamp(self.data[0]['date'])

    def get_last_date(self):
        """
        Get the last data item for this instrument

        Return:
           datetime.date
        """
        return datetime.date.fromtimestamp(self.data[-1]['date'])

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

        # translate timestamp date to datetime.date
        d['date'] = datetime.date.fromtimestamp(d['date'])

        return d

    def get_day_index(self, date):
        """
        Get index of the row in data matching a specific date.

        Args:
           date (datetime.date)

        Return(int):
           Index of the Instrument.data row matching the date

        Raises:
           KeyError if there is no data for this date
        """
        # convert to timestamp
        timestamp = datetime.datetime(
            date.year, date.month, date.day).timestamp()

        # get matching rows
        matches = np.where(self.data['date'] == timestamp)[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError(str(self) + ": date not found: " + str(date))

        # if there was exactly one matching row
        elif match_count == 1:
            # get the index of the matching row
            row_index = matches[0]

            return row_index

        # if there were more than one matching row
        else:
            # There must be something wrong in the database, which one should we return?
            raise Exception("There was more than one matching row")

    def get_day_index_or_last_before(self, date):
        """
        Get index of the row in data matching a specific date,
        or get index of the previous preceding date if there were no trades this date.

        Args:
           date (datetime.date)

        Return(int):
           Index of the Instrument.data row matching the date

        Raises:
           KeyError if there is no data for this date or earlier dates
        """
        # convert to timestamp
        timestamp = datetime.datetime(
            date.year, date.month, date.day).timestamp()

        matches = np.where(self.data['date'] <= timestamp)[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError(str(self) + ": Date not found: " + str(date) +
                           ", first date is " + str(self.get_first_date()))

        else:
            # get the index of the last matching row
            row_index = matches[-1]
            return row_index

    def get_day(self, date):
        """
        Get the data for a specific date.

        Args:
           date (datetime.date)

        Return:
           Dict containing data for this date

        Raises:
           KeyError if there is no data for this date
        """
        row_index = self.get_day_index(date)
        return self._get_row(row_index)

    def get_day_or_first_after(self, date):
        """
        Get the data for the first date after

        Args:
           date (datetime.date)

        Return:
           Dict containing data for this or the next day with available data

        Raises:
           KeyError if there is no data for this or later dates
        """
        # convert to timestamp
        timestamp = datetime.datetime(
            date.year, date.month, date.day).timestamp()

        # get matching rows
        matches = np.where(self.data['date'] >= timestamp)[0]
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

        Args:
           date (datetime.date)

        Return:
           Dict containing data for this or the last day with available data

        Raises:
           KeyError if there is no data for this or previous dates
        """
        # convert to timestamp
        timestamp = datetime.datetime(
            date.year, date.month, date.day).timestamp()

        # get matching rows
        matches = np.where(self.data['date'] <= timestamp)[0]
        match_count = len(matches)

        # no matching rows
        if match_count == 0:
            raise KeyError("Date not found :" + str(date))
        else:
            # get the index of the last matching row
            row_index = matches[-1]

            return self._get_row(row_index)

    def get_price(self, date):
        """
        Get price at this date

        The 'open' price will be used,
        otherwise the 'value' price will be used.
        Typically, Nasdaq OMX data doesn't have 'open', but 'value'

        If there is no data for this date, the last known 'close' value
        will be used, or 'value' if it doesn't exist.

        Return:
           A price estimate for today
        """
        day_data = self.get_day_or_last_before(date)

        # if the data is for the requested date
        if day_data['date'] == date:

            # try to use the open price
            try:
                return day_data['open']
            except:
                return day_data['value']

        # if this data belongs to an earlier date
        else:

            # try to use the close price
            try:
                return day_data['close']
            except:
                return day_data['value']

    def existed_at_date(self, date):
        """
        Check if this instrument existed at the given date.
        If the given date is between the oldest and the newest date
        which we have data for this ticker, it is considered to exist.

        Args:
            date(datetime.date)

        Return True or False
        """
        first_date = self.get_first_date()
        last_date = self.get_last_date()

        if date < first_date or date > last_date:
            return False
        else:
            return True

class Market(object):
    def __init__(self, name, long_name):
        self.name = name
        self.long_name = long_name
        self.instruments = []
