# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
import json
import re
import datetime
import numpy as np

class NasdaqOmxSpider(scrapy.Spider):
    name = 'nasdaqomx'
    allowed_domains = ['nasdaqomx.com']

    # Index groups that are relevant to Norwegian traders
    categories = [
        #{'name': 'AlphaDEX', 'id': 5064},
        #{'name': 'NASDAQ Commodity', 'id': 12},
        #{'name': 'Custom Indexes', 'id': 54},
        #{'name': 'NASDAQ Dividend and Income Index Family', 'id': 51},
        #{'name': 'Dorsey Wright Indexes', 'id': 5075},
        {'name': 'Iceland', 'id': 13},
        {'name': 'Stockholm', 'id': 3},
        {'name': 'Oslo', 'id': 17},
        #{'name': 'Russia', 'id': 18},
        #{'name': 'Baltic', 'id': 6},
        {'name': 'Helsinki', 'id': 5},
        {'name': 'Nordic', 'id': 14},
        {'name': 'Copenhagen', 'id': 4},
        {'name': 'Europe', 'id': 16},
        {'name': 'Nordic Market', 'id': 7},
        #{'name': 'ISE Indexes', 'id': 5104},
        #{'name': 'NASDAQ Global Index Family', 'id': 15},
        #{'name': 'NASDAQ Global Index Developed Markets', 'id': 46},
        #{'name': 'NASDAQ Global Index Emerging Markets', 'id': 47},
        #{'name': 'NASDAQ Global Index Americas Region', 'id': 48},
        #{'name': 'NASDAQ Global Index Europe Region', 'id': 49},
        #{'name': 'NASDAQ Global Index AMEA Region', 'id': 50},
        #{'name': 'US Style', 'id': 5068},
        #{'name': 'Green', 'id': 20},
        #{'name': 'NASDAQ BulletShares Ladder Indexes', 'id': 56},
        #{'name': 'Nasdaq KBW', 'id': 5073},
        #{'name': 'Sharia', 'id': 19},
        #{'name': 'NASDAQ', 'id': 33},
        #{'name': 'PHLX', 'id': 34},
        #{'name': 'PHLX Other', 'id': 35},
        #{'name': 'Other', 'id': 42},
        #{'name': 'VINX Indexes', 'id': 55},
        ]

    # project specific class variables
    market_name = 'nasdaqomx'
    market_name_long = 'Nasdaq OMX'

    # this function overloads the default start_requests() function
    def start_requests(self):

        # used for checking that a ticker isn't downloaded twice
        self.requested_tickers = set()

        for category in self.categories:
            self.logger.info('POST request for category "' + category['name'] + '"')
                             
            # return a POST request for getting the index list in this category group
            yield FormRequest(url="https://indexes.nasdaqomx.com/Index/DirectoryData",
                              formdata={'categoryID': str(category['id'])},
                              callback=self.parse_categories)

    def parse_categories(self, response):

        # get a dict with the json data
        data = json.loads(response.body_as_unicode())

        # for all instruments in the list
        for instrument in data['aaData']:
            
            ticker = instrument['Symbol']
            name = instrument['Name']
            paper_type = instrument['AssetType']

            if ticker in self.requested_tickers:
                self.logger.warning('Ticker "' + ticker + '" has already been requested. Skipping')
                continue

            # POST request for historical data for this ticker
            self.logger.info('Sending POST request for ticker "' + ticker + '"')
            yield FormRequest(url="https://indexes.nasdaqomx.com/Index/HistoryData",
                              formdata={
                                  'id': ticker,
                                  'startDate': '1950-09-03T00:00:00.000',
                                  'endDate': '2050-09-03T00:00:00.000',
                                  'timeOfDay': 'EOD'},
                              meta={'ticker': ticker, 'name': name, 'paper_type': paper_type},
                              callback=self.parse_historical_data)

    # parse the POST response containing the ticker data
    def parse_historical_data(self, response):

        # unpack the meta values that we attached to this request
        ticker = response.meta['ticker']
        name = response.meta['name']
        paper_type = response.meta['paper_type']

        # get a dict with the json data
        data = json.loads(response.body_as_unicode())

        # rows of dicts which is the historical data for this ticker
        rows = data['aaData']

        # reverse the list to get the earlies date at index 0
        rows.reverse()

        # create an empty matrix to store the CSV data in
        matrix = np.zeros(shape=len(rows),
                          dtype=[('date', 'f8'),
                                 ('value', 'f8'),
                                 ('high', 'f8'),
                                 ('low', 'f8'),
                                 ('net_change', 'f8')])

        # populate the matrix with the extracted data
        for row_num, row in enumerate(rows):

            # convert to datetime.datetime
            match = re.search(r"Date\((.*)\)", row['TimeStamp'])
            parsed_date = datetime.datetime.fromtimestamp(float(match.group(1))/1000.0)

            # Strip hours and minutes from the date string.
            # It has been observed that some tickers have an hour offset to the timestamp.
            # For example OMXC25DVP: datetime.datetime(2017, 1, 2, 6, 0)
            stripped_date = datetime.datetime(parsed_date.year, parsed_date.month, parsed_date.day)
            
            # convert to timestamp
            date = stripped_date.timestamp()
            
            # convert to float, None values will be converted to 0.0
            value = 0.0 if row['Value'] is None else float(row['Value'])
            high = 0.0 if row['High'] is None else float(row['High'])
            low = 0.0 if row['Low'] is None else float(row['Low'])
            net_change = 0.0 if row['NetChange'] is None else float(row['NetChange'])

            matrix[row_num] = date, value, high, low, net_change

        # print some info so that the user can see what's going on
        self.logger.info("Scraped " + ticker)

        # returned the parsed data in this storage class
        return {'ticker': ticker,
                'name': name,
                'paper_type': paper_type,
                'data': matrix}
