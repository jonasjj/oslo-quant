# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
import json
import re
import datetime
import numpy as np

# A lua script which shall be passed to the splash browser.
# The script will wait for a specific tag to be loaded.
#
# usage: LUA_SCRIPT % css_item_to_wait_for
#
LUA_SCRIPT = """
function main(splash)
  splash:set_user_agent('splash.args.ua')
  assert(splash:go(splash.args.url))
  
  -- requires Splash 2.3  
  while not splash:select('%s') do
    splash:wait(0.1)
  end
  return {html=splash:html()}
end
"""

class NasdaqOmxSpider(scrapy.Spider):
    name = 'nasdaqomx'
    allowed_domains = ['nasdaqomx.com']

    # Indexes that are relevant to Norwegian traders
    start_urls = [#'https://indexes.nasdaqomx.com/Index/Directory/Iceland',
                  #'https://indexes.nasdaqomx.com/Index/Directory/Stockholm',
                  'https://indexes.nasdaqomx.com/Index/Directory/Oslo',
                  #'https://indexes.nasdaqomx.com/Index/Directory/Helsinki',
                  #'https://indexes.nasdaqomx.com/Index/Directory/Nordic',
                  #'https://indexes.nasdaqomx.com/Index/Directory/Copenhagen',
                  #'https://indexes.nasdaqomx.com/Index/Directory/Europe',
    ]
        
    # project specific class variables
    market_name = 'nasdaqomx'
    market_name_long = 'Nasdaq OMX'

    # this function overloads the default start_requests() function
    def start_requests(self):

        for url in self.start_urls:
            yield SplashRequest(url=url,
                                callback=self.parse,
                                endpoint='execute',
                                args={
                                    'lua_source': LUA_SCRIPT % '.dataTables_info',
                                })



    # parse the top level list of indexes
    def parse(self, response):

        # the table element which contains the index list
        table = response.css('#directory')

        # table headers
        headers = table.css('th')

        # column headers
        header_texts = headers.css('::text').extract()

        # strip whitespace from the headers
        stripped_headers = []
        for h in header_texts:
            stripped_headers.append(h.strip())

        # check that the headers have the expected format
        assert stripped_headers == ['Symbol',
                                    'Name',
                                    'Brand',
                                    'Series',
                                    'Currency',
                                    'Schedule',
                                    'DataSet',
                                    'Dissemination Frequency',
                                    'Entitlement',
                                    'Asset Type']

        # all table rows that contain the indexes
        rows = table.css('tbody tr')

        for row in rows:

            # table cells
            cell = row.css('td')

            # the relative URL to the index page
            rel_url = row.css('a::attr(href)').extract_first()

            # the absolute URL to the index page
            abs_url = response.urljoin(rel_url)
            
            # ticker name
            ticker = row.css('a::text').extract_first()

            texts = row.css('td::text').extract()

            # unpack the text items
            name = texts[0]
            brands = texts[1]
            series = texts[2]
            currency = texts[3]
            schedule = texts[4]
            dataset = texts[5]
            dissenmination_frequency = texts[6]
            entitlement = texts[7]
            asset_type = texts[8]

            # POST request for historical data for this ticker
            yield FormRequest(url="https://indexes.nasdaqomx.com/Index/HistoryData",
                              formdata={
                                  'id': ticker,
                                  'startDate': '1950-09-03T00:00:00.000',
                                  'endDate': '2050-09-03T00:00:00.000',
                                  'timeOfDay': 'EOD'},
                              meta={'ticker': ticker, 'name': name},
                              callback=self.parse_json)

                    
        # TODO: need to click next page here

    # parse the POST response containing the ticker data
    def parse_json(self, response):

        # unpack the meta values that we attached to this request
        ticker = response.meta['ticker']
        name = response.meta['name']

        # get a dict with the json data
        data = json.loads(response.body_as_unicode())

        # rows of dicts which is the historical data for this ticker
        rows = data['aaData']

        # create an empty matrix to store the CSV data in
        matrix = np.zeros(shape=len(rows),
                          dtype=[('date', 'f8'),
                                 ('value', 'f8'),
                                 ('high', 'f8'),
                                 ('low', 'f8'),
                                 ('close', 'f8'),
                                 ('net_change', 'f8')])

        # populate the matrix with the extracted data
        for row_num, row in enumerate(rows):

            # convert to timestamp
            match = re.search(r"Date\((.*)\)", row['TimeStamp'])
            date = datetime.datetime.fromtimestamp(float(match.group(1))/1000.0).timestamp()

            # convert to float, None values will be converted to 0.0
            value = 0.0 if row['Value'] is None else float(row['Value'])
            high = 0.0 if row['High'] is None else float(row['High'])
            low = 0.0 if row['Low'] is None else float(row['Low'])
            close = 0.0 if row['Close'] is None else float(row['Close'])
            net_change = 0.0 if row['NetChange'] is None else float(row['NetChange'])
            
            matrix[row_num] = date, value, high, low, close, net_change

        # print some info so that the user can see what's going on
        self.logger.info("Scraped " + ticker)

        # returned the parsed data in this storage class
        return {'ticker': ticker,
                'name': name,
                'data': matrix}
