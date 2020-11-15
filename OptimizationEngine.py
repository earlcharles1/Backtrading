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

    alias = ('BBands',)

    lines = ('mid', 'top', 'bot',)
    params = (('period', 10),
         ('devfactor', 1.45), 
         ('movav', MovAv.Simple),
         ('stake',1),
         ('printlog',False)
         )

    plotinfo = dict(subplot=False)
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )
    def log(self, txt, dt=None, doprint=True):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0) or self.data.close
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.boll=bt.indicators.BollingerBands(period=self.params.period, 
            devfactor=self.params.devfactor)
        ma = self.params.movav(self.data, period=self.params.period)
        self.lines.mid = ma
        stddev = self.p.devfactor * StdDev(self.data, ma, period=self.params.period,
                                           movav=self.params.movav,)
        self.lines.top = ma + stddev
        self.lines.bot = ma - stddev
        self.sizer.setsizing(self.params.stake)
        self.order = None
        self.buyprice = None
        self.buycomm = None
    def next(self):
        Discount = self.boll.lines.top - (self.boll.lines.top * .12)
        posSize = self.position.size
        if self.position.size < 0:
            if self.data.close > self.boll.lines.top:

                pass
            elif self.data.close < Discount:

                self.buy(size=abs(posSize))

        else:
            if self.data.close > self.boll.lines.top:

                self.sell()

    def stop(self):
        self.log('(Period %2d) (DevFactor %.2d) Ending Value %.2f' %
                (self.params.period, self.params.devfactor, self.broker.getvalue()),
                 doprint=True)
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    strats = cerebro.optstrategy(
        BollingerBands,
        period=range(2,25),
        )
    # cerebro.addstrategy(BollingerBands)
    data = bt.feeds.YahooFinanceData(
    dataname = 'VXX',
        # Do not pass values before this date
    fromdate = datetime.datetime(2020, 3, 27),
        # Do not pass values before this date
    todate=datetime.datetime(2020, 11, 13),
        # Do not pass values after this date
    reverse=False)
    cerebro.adddata(data)
    cerebro.broker.setcash(5000.0)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.addsizer(bt.sizers.FixedSize,stake=100)
    cerebro.run(maxcpus=1)