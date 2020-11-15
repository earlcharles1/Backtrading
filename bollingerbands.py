from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt
from backtrader import Indicator
from backtrader.indicators.mabase import MovAv
from backtrader.indicators.deviation import StandardDeviation as StdDev


class BollingerBands(bt.Strategy):
    '''
    Defined by John Bollinger in the 80s. It measures volatility by defining
    upper and lower bands at distance x standard deviations
    Formula:
      - midband = SimpleMovingAverage(close, period)
      - topband = midband + devfactor * StandardDeviation(data, period)
      - botband = midband - devfactor * StandardDeviation(data, period)
    See:
      - http://en.wikipedia.org/wiki/Bollinger_Bands
    '''
    alias = ('BBands',)

    lines = ('mid', 'top', 'bot',)
    params = (('period', 20), ('devfactor', 1.5), ('movav', MovAv.Simple),)

    plotinfo = dict(subplot=False)
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.boll=bt.indicators.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
        ma = self.params.movav(self.data, period=self.params.period)
        self.lines.mid = ma
        stddev = self.p.devfactor * StdDev(self.data, ma, period=self.params.period,
                                           movav=self.params.movav)
        self.lines.top = ma + stddev
        self.lines.bot = ma - stddev

    def next(self):
        if self.position:
            if self.data.close > self.boll.lines.top:
                self.log('SELL, %.2f' % self.data.close[0])
                self.close()
            else:
                if self.data.close < self.boll.lines.bot:
                    self.log('BUY, %.2f' % self.data.close[0])
                    self.order = self.buy()
        # if not self.position:
        #     if self.data.close > self.boll.lines.top:
        #         self.log('SELL CREATE, %.2f' % self.data.close[0])
        #         self.order = self.sell()
        else:
            if self.data.close > self.boll.lines.top:
                self.log('SELL, %.2f' % self.data.close[0])
                self.close()
            else:
                if self.data.close < self.boll.lines.bot:
                    self.log('BUY, %.2f' % self.data.close[0])
                    self.order = self.buy()
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BollingerBands)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'TSLA.csv')
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2017, 11, 13),
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
    cerebro.plot()