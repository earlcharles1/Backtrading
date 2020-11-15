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
    params = (('period', 20), ('devfactor', 1.85), ('movav', MovAv.Simple),
                ('stake',1),)

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
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

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
    def next(self):
        if self.position.size < 0:
            if self.data.close > self.boll.lines.top:
                # self.log('SHORT -100, %.2f' % self.data.close[0])
                self.sell()
                print(self.position.size)
            elif self.data.close < self.boll.lines.top - self.boll.lines.top*(.25):
                # self.log('COVER SHORT, %.2f' % self.data.close[0])
                self.close()
                print(self.position.size)
        else:
            if self.data.close > self.boll.lines.top:
                # self.log('SHORT, %.2f' % self.data.close[0])
                self.sell()
                print(self.position.size)
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BollingerBands)
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'ZM.csv')
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
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.addsizer(bt.sizers.FixedSize,stake=100)
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()