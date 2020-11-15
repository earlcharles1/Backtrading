from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.indicators
import backtrader.feeds as btfeeds

class BollingerBand(bt.Strategy):

    params = (('period', 5),
        ('devfactor', 3.0),)


    def __init__(self):
        self.period = self.params.period
        self.devfactor = self.params.devfactor
        self.close = self.datas[0].close
        self.midband = backtrader.indicators.SimpleMovingAverage(self.period)
        self.topband = self.midband + self.devfactor*StandardDeviation(data,period)
        self.botband = self.midband - self.devfactor*StandardDeviation(data,period)

    def next(self):
        self.log('Close, %.2f' % self.close[0])
        if self.order:
            return
        if not self.position:
            if self.close[0] > self.topband:
                self.log('Short/Sale, %.2f' % self.close)
                self.order = self.sell()
        else:
            if self.close[0] < self.botband:
                self.log('Buy, %.2f' % self.close)
                self.order = self.buy()
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BollingerBand)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'RICK.csv')
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2019, 11, 13),
        # Do not pass values before this date
        todate=datetime.datetime(2020, 11, 13),
        # Do not pass values after this date
        reverse=False)
    cerebro.adddata(data)
    cerebro.broker.setcash(5000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake =10)
    cerebro.broker.setcommission(commission=0.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
