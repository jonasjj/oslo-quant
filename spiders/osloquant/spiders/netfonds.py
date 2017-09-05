# -*- coding: utf-8 -*-
import scrapy


class NetfondsSpider(scrapy.Spider):
    name = 'netfonds'
    allowed_domains = ['netfonds.no']
    start_urls = ['http://www.netfonds.no/quotes/exchange.php']

    def parse(self, response):

        # select the table which contains the ticker list
        table_rows = response.css(".hcontent > .com tr")

        for row in table_rows:

            # if this row contains the table header
            if(len(row.css("th"))):

                # sanity check: check that the columns are as expected
                columns = row.css("th::text").extract()                
                assert columns == ['Tick', 'Åpning', 'Høy', 'Lav', 'Siste', 'Volum', 'Verdi']

            # if this row contains table data
            elif(len(row.css("td"))):

                # extract ticker name and url from this table row
                ticker = row.css("a::text").extract_first()
                url = row.css("a::attr(href)").extract_first()

                self.log("Found " + ticker + " " + url)

            else:
                self.log.error("This table row contains neither td or th elements")
                
