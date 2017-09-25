# oslo-quant
This framework is intended for traders based on Oslo Stock Exchange who wishes to perform quantitative analysis on market data using Python.
Download, plot and play with data from Oslo Børs and Nasdaq OMX

This program works with data that has day-to-day resolution, 
which happens to be what is available for free from Oslo Børs and Nasdaq OMX.

The [Scrapy](https://scrapy.org/) framework is used for the web scraping.

## How to install dependencies on a fresh Ubuntu 17.04 installation
```
sudo apt-get install python3-numpy
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqtgraph
sudo apt-get install python3-progressbar
sudo apt-get install python3-tabulate
sudo apt-get install python3-setproctitle
sudo apt-get install python3-scrapy
```

## How to install dependencies on a fresh macOS Sierra (10.12) installation
```
# Install homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install python3
brew install pyqt
pip3 install numpy
pip3 install scrapy
pip3 install pyqtgraph
pip3 install setproctitle
pip3 install tabulate
```

## How to download all available data
```
cd spiders
./download --all
```

The data will be in the ./data dir in the project root.

## How to plot tickers
Example plotting the OBX Total Return Index daily close prices:
```
./python/plot_instrument.py -i OBX.OSE close
```
![plot_instrument_obx_close_2.png](https://jonasjulianjensen.com/wp-content/uploads/2017/08/plot_instrument_obx_close_2.png)

Linked plot with Statoil and Norwegian daily low prices:
```
./python/plot_instrument.py -i STL.OSE low -i NAS.OSE low
```
![plot_instrument_stl_nas_low_2.png](https://jonasjulianjensen.com/wp-content/uploads/2017/08/plot_instrument_stl_nas_low_2.png)

Find the historical return from holding the OBX index through december:
```
./python/historical_return_from_to_date.py OBX.OSE 2017-12-01 2017-12-31
OrderedDict([('trades',
              ...
             ('year_count', 20),
             ('avg_gain_ratio', 0.042368806614828204),
             ('pos_gain_ratio', 0.9),
             ('variance', 0.0036060780794071154),
             ('std_deviation', 0.060050629300675236)])
```

Find the expected average gain, based on historical data,
if the OBX is purchased and held for 31 days. 
Present the data in a plot which is averaged over a 7 days long sliding window:
```
./python/historical_return_best_dates.py --avg_gain --avg 7 --plot OBX.OSE 31
```
![historical_return_best_dates_obx_2.png](https://jonasjulianjensen.com/wp-content/uploads/2017/08/historical_return_best_dates_obx_2.png)
