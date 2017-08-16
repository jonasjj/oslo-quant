# oslo-quant
This frameworks is intended for traders based on Oslo Stock Exchange who wishes to perfom quantitative analysis on market data using Python.
Download, plot and play with data from Oslo Børs and Nasdaq OMX

This program works with data that has day-to-day resolution, 
which happens to be what is available for free from Oslo Børs and Nasdaq OMX.

## How to install dependencies on a fresh Ubuntu 17.04 installation
```
sudo apt-get install python3-numpy
sudo apt-get install python3-pyqt4
sudo apt-get install python3-pyqtgraph
sudo apt-get install python3-progressbar
sudo apt-get install python3-setproctitle
sudo apt-get install unoconv
```

## How to download all available data
```
./scripts/download_load_and_pickle --all
```

The data will be in the ./data dir in the project root.

## How to plot tickers
Example plotting the OBX Total Return Index daily close prices:
```
python3 python/plot_instrument.py -i OBX close
```
![alt text](https://jonasjulianjensen.com/wp-content/uploads/2017/08/plot_instrument_obx_close.png)

Linked plot with Statoil and Norwegian daily low prices:
```
python3 python/plot_instrument.py -i STL low -i NAS low
```
![alt text](https://jonasjulianjensen.com/wp-content/uploads/2017/08/plot_instrument_stl_nas_low.png)

Find the historical return from holding the OBX index through december:
```
python3 python/historical_return_from_to_date.py OBX 2017-12-01 2017-12-31
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
python3 python/historical_return_best_dates.py --avg_gain --avg 7 --plot OBX 31
```
![alt text](https://jonasjulianjensen.com/wp-content/uploads/2017/08/historical_return_best_dates_obx.png)
