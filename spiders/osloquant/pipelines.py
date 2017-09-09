# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import pickle

# Append to the Python path
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_dir, "../../python"))

from markets import DATA_DIR
from markets._classes import Market, Ticker

class OsloquantPipeline(object):

    # This method is called when the spider is opened
    def open_spider(self, spider):

        # Create a new Market object
        self.market = Market(spider.market_name, spider.market_name_long)

    # This method is called when the spider is closed
    def close_spider(self, spider):

        # sort the market tickers alphabetically
        self.market.tickers.sort(key=lambda x: x.name)
        
        # full path to the pickle file
        path = os.path.join(DATA_DIR, spider.market_name + '.p')

        # write the Market object to the pickle file
        with open(path, "wb" ) as f:
            pickle.dump(self.market, f)

        spider.logger.info('Wrote "' + path + '"')
 
    # This method is called for every item in the pipeline
    def process_item(self, item, spider):

        # create a new Ticker instance and add it to the market
        ticker = Ticker(item['ticker'], item['name'], item['data'])
        self.market.tickers.append(ticker)

        # return the original item, it won't be used anyway
        return item
