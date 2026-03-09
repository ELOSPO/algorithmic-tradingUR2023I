"""
Easy_Trading_Mega.py
====================
Clase unificada para operar con MetaTrader 5, Interactive Brokers y NinjaTrader
usando exactamente la misma interfaz de métodos.

Uso:
    # MetaTrader 5
    bot = EasyTrading('MT5', nombre=login, clave='pass', servidor='ICMarkets-Demo', path='C:/MT5/terminal64.exe')

    # Interactive Brokers (TWS o IB Gateway debe estar abierto)
    bot = EasyTrading('IB', host='127.0.0.1', port=7497, client_id=1)

    # NinjaTrader (ATI debe estar habilitado: Tools → Options → ATI)
    bot = EasyTrading('NT', host='127.0.0.1', port=36973, account='Sim101', data_folder='C:/NT_Data/')

    # Misma interfaz para los tres:
    bot.buy('EURUSD', 0.1, sl=1.0800, tp=1.1000)
    bot.sell('EURUSD', 0.1)
    df = bot.extract_data('EURUSD', 'H1', 500)
    balance, profit, equity, free_margin = bot.info_account()
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime

# ── Imports opcionales: solo se importan si el broker correspondiente se usa ──
try:
    import MetaTrader5 as mt5
    _MT5_AVAILABLE = True
except ImportError:
    _MT5_AVAILABLE = False

try:
    from ib_insync import (IB, Stock, Forex, Contract,
                           MarketOrder, LimitOrder, StopOrder, util)
    _IB_AVAILABLE = True
except ImportError:
    _IB_AVAILABLE = False

try:
    import socket as _socket
    import os as _os
    _NT_AVAILABLE = True
except ImportError:
    _NT_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
#  CLASE BASE ABSTRACTA
# ══════════════════════════════════════════════════════════════════════════════

class _BaseBroker(ABC):
    """
    Define la interfaz común a todos los brokers.
    Los métodos independientes del broker (Kelly, calendario) están implementados aquí.
    """

    inicializado: bool = False

    # ── Métodos abstractos (cada broker los implementa) ───────────────────────

    @abstractmethod
    def extract_data(self, par: str, periodo, cantidad: int) -> pd.DataFrame:
        """Extrae datos históricos y los devuelve como DataFrame."""

    @abstractmethod
    def get_data_from_dates(self, year_ini, month_ini, day_ini,
                             year_fin, month_fin, day_fin,
                             symbol, timeframe, for_bt=False) -> pd.DataFrame:
        """Obtiene datos históricos en un rango de fechas."""

    @abstractmethod
    def buy(self, symbol: str, volumen: float, nom_bot: str = 'Py',
            sl: float = None, tp: float = None):
        """Abre una operación larga (compra)."""

    @abstractmethod
    def sell(self, symbol: str, volumen: float, nom_bot: str = 'Py',
             sl: float = None, tp: float = None):
        """Abre una operación corta (venta)."""

    @abstractmethod
    def buy_limit(self, symbol: str, volume: float, price: float, **kwargs):
        """Coloca una orden Buy Limit."""

    @abstractmethod
    def sell_limit(self, symbol: str, volume: float, price: float, **kwargs):
        """Coloca una orden Sell Limit."""

    @abstractmethod
    def buy_stop(self, symbol: str, volume: float, price: float, **kwargs):
        """Coloca una orden Buy Stop."""

    @abstractmethod
    def sell_stop(self, symbol: str, volume: float, price: float, **kwargs):
        """Coloca una orden Sell Stop."""

    @abstractmethod
    def get_opened_positions(self, par: str = None) -> tuple:
        """Retorna (cantidad, DataFrame) con las posiciones abiertas."""

    @abstractmethod
    def get_all_positions(self) -> pd.DataFrame:
        """Retorna un DataFrame con todas las posiciones abiertas."""

    @abstractmethod
    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        """Retorna un DataFrame con las órdenes pendientes."""

    @abstractmethod
    def remover_operacion_pendiente(self, nom_est: str, type_fill=None) -> None:
        """Cancela órdenes pendientes de una estrategia."""

    @abstractmethod
    def modify_orders(self, symb: str, ticket, stop_loss: float = None,
                      take_profit: float = None, type_order=None, type_fill=None) -> None:
        """Modifica SL y/o TP de una orden abierta."""

    @abstractmethod
    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=None) -> None:
        """Cierra todas las operaciones del DataFrame."""

    @abstractmethod
    def close_partial(self, type_op, id_position, symbol: str, volume_to_close: float):
        """Cierra parcialmente una posición."""

    @abstractmethod
    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float) -> None:
        """Mueve el SL a Break Even cuando el precio recorre un % del TP."""

    @abstractmethod
    def info_account(self) -> tuple:
        """Retorna (balance, profit, equity, free_margin)."""

    @abstractmethod
    def calculate_position_size(self, symbol: str, capital: float,
                                  per_to_risk: float) -> float:
        """Calcula el tamaño de posición óptimo."""

    # ── Métodos independientes del broker (implementados aquí) ────────────────

    def kelly_criterion_pct_risk(self, win_rate: float, profit_factor: float) -> float:
        """
        Calcula el porcentaje de capital a arriesgar según el Criterio de Kelly.

        # Parámetros
        - win_rate: Tasa de ganancia de la estrategia (0 a 1)
        - profit_factor: Profit factor de la estrategia
        """
        k_c = (profit_factor * win_rate + win_rate - 1) / profit_factor
        return max(k_c, 0.01)

    def get_today_calendar(self) -> pd.DataFrame:
        """
        Retorna un DataFrame con las noticias económicas del día
        con columnas: currency, time, intensity (1=baja, 2=media, 3=alta).
        """
        r = Request('https://es.investing.com/economic-calendar/',
                    headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(urlopen(r).read(), 'html.parser')
        table = soup.find_all(class_='js-event-item')

        base = {}
        for bl in table:
            time_text = bl.find(class_='first left time js-time').text
            currency  = bl.find(class_='left flagCur noWrap').text.split(' ')
            intensity = bl.find_all(class_='left textNum sentiment noWrap')
            id_hour   = currency[1] + '_' + time_text

            if id_hour not in base:
                base[id_hour] = {'currency': currency[1], 'time': time_text, 'intensity': 0}

            intencity = 0
            for intence in intensity:
                n = len(intence.find_all(class_='grayFullBullishIcon'))
                if n in (1, 2, 3):
                    intencity = n

            base[id_hour]['intensity'] = intencity

        return pd.DataFrame.from_records(list(base.values()))


# ══════════════════════════════════════════════════════════════════════════════
#  BROKER 1 — MetaTrader 5
# ══════════════════════════════════════════════════════════════════════════════

class _MT5Broker(_BaseBroker):

    def __init__(self, nombre, clave, servidor, path):
        if not _MT5_AVAILABLE:
            raise ImportError("MetaTrader5 no está instalado. Ejecuta: pip install MetaTrader5")
        self.nombre   = nombre
        self.clave    = clave
        self.servidor = servidor
        self.path     = path
        mt5.initialize(login=self.nombre, password=self.clave,
                       server=self.servidor, path=self.path)
        self.inicializado = True

    # ── Datos ─────────────────────────────────────────────────────────────────

    def extract_data(self, par: str, periodo, cantidad: int) -> pd.DataFrame:
        mt5.initialize(login=self.nombre, password=self.clave,
                       server=self.servidor, path=self.path)
        rates = mt5.copy_rates_from_pos(par, periodo, 0, cantidad)
        tabla = pd.DataFrame(rates)
        tabla['time'] = pd.to_datetime(tabla['time'], unit='s')
        return tabla

    def get_data_from_dates(self, year_ini, month_ini, day_ini,
                             year_fin, month_fin, day_fin,
                             symbol, timeframe, for_bt=False) -> pd.DataFrame:
        mt5.initialize(login=self.nombre, server=self.servidor,
                       password=self.clave, path=self.path)
        from_date = datetime(year_ini, month_ini, day_ini)
        to_date   = datetime(year_fin,  month_fin,  day_fin)
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        if for_bt:
            df = df.iloc[:, [0,1,2,3,4,5,7]]
            df.columns = ['time','Open','High','Low','Close','Volume','OpenInterest']
            df = df.set_index('time')
        return df

    def _get_data_for_bt(self, timeframe, symbol, cantidad):
        mt5.initialize(login=self.nombre, server=self.servidor,
                       password=self.clave, path=self.path)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, cantidad)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.iloc[:, [0,1,2,3,4,5,7]]
        df.columns = ['time','Open','High','Low','Close','Volume','OpenInterest']
        return df.set_index('time')

    # ── Órdenes ───────────────────────────────────────────────────────────────

    def _open_operations(self, par, volumen, tipo_operacion, nombre_bot,
                          sl=None, tp=None, type_fill=mt5.ORDER_FILLING_FOK):
        base = {
            'action':       mt5.TRADE_ACTION_DEAL,
            'symbol':       par,
            'volume':       volumen,
            'type':         tipo_operacion,
            'magic':        202204,
            'comment':      nombre_bot,
            'type_time':    mt5.ORDER_TIME_GTC,
            'type_filling': type_fill,
        }
        if sl  is not None: base['sl'] = sl
        if tp  is not None: base['tp'] = tp
        result = mt5.order_send(base)
        print(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen}')
        return result

    def buy(self, symbol, volumen, nom_bot='Py', sl=None, tp=None, type_fill=mt5.ORDER_FILLING_FOK):
        return self._open_operations(symbol, volumen, mt5.ORDER_TYPE_BUY, nom_bot, sl, tp, type_fill)

    def sell(self, symbol, volumen, nom_bot='Py', sl=None, tp=None, type_fill=mt5.ORDER_FILLING_FOK):
        return self._open_operations(symbol, volumen, mt5.ORDER_TYPE_SELL, nom_bot, sl, tp, type_fill)

    def send_pending_order(self, symbol, volume, price, type_op, expirationdate,
                            type_fill, sl=None, tp=None, nombre_bot='Py'):
        order = {
            'action':       mt5.TRADE_ACTION_PENDING,
            'symbol':       symbol,
            'volume':       volume,
            'price':        price,
            'type':         type_op,
            'type_time':    mt5.ORDER_TIME_SPECIFIED,
            'expiration':   expirationdate,
            'comment':      nombre_bot,
            'type_filling': type_fill,
        }
        if expirationdate is None:
            del order['expiration']
        if sl is not None: order['sl'] = sl
        if tp is not None: order['tp'] = tp
        return mt5.order_send(order)

    def buy_limit(self, symbol, volume, price, expirationdate=None, type_fill=mt5.ORDER_FILLING_FOK,
                  sl=None, tp=None, nombre_bot='Py'):
        self.send_pending_order(symbol, volume, price, mt5.ORDER_TYPE_BUY_LIMIT,
                                expirationdate, type_fill, sl, tp, nombre_bot)

    def sell_limit(self, symbol, volume, price, expirationdate=None, type_fill=mt5.ORDER_FILLING_FOK,
                   sl=None, tp=None, nombre_bot='Py'):
        self.send_pending_order(symbol, volume, price, mt5.ORDER_TYPE_SELL_LIMIT,
                                expirationdate, type_fill, sl, tp, nombre_bot)

    def buy_stop(self, symbol, volume, price, expirationdate=None, type_fill=mt5.ORDER_FILLING_FOK,
                 sl=None, tp=None, nombre_bot='Py'):
        self.send_pending_order(symbol, volume, price, mt5.ORDER_TYPE_BUY_STOP,
                                expirationdate, type_fill, sl, tp, nombre_bot)

    def sell_stop(self, symbol, volume, price, expirationdate=None, type_fill=mt5.ORDER_FILLING_FOK,
                  sl=None, tp=None, nombre_bot='Py'):
        self.send_pending_order(symbol, volume, price, mt5.ORDER_TYPE_SELL_STOP,
                                expirationdate, type_fill, sl, tp, nombre_bot)

    def modify_orders(self, symb, ticket, stop_loss=None, take_profit=None,
                      type_order=mt5.ORDER_TYPE_BUY, type_fill=mt5.ORDER_FILLING_FOK):
        req = {
            'action':       mt5.TRADE_ACTION_SLTP,
            'symbol':       symb,
            'position':     ticket,
            'type':         type_order,
            'type_time':    mt5.ORDER_TIME_GTC,
            'type_filling': type_fill,
        }
        if stop_loss    is not None: req['sl'] = stop_loss
        if take_profit  is not None: req['tp'] = take_profit
        mt5.order_send(req)

    def close_partial(self, type_op, id_position, symbol, volume_to_close):
        order = {
            'action':   mt5.TRADE_ACTION_DEAL,
            'type':     type_op,
            'position': id_position,
            'symbol':   symbol,
            'volume':   volume_to_close,
        }
        return mt5.order_send(order)

    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=mt5.ORDER_FILLING_FOK):
        for operacion in data['ticket'].unique().tolist():
            row = data[data['ticket'] == operacion]
            tipo_op  = row['type'].item()
            simbolo  = row['symbol'].item()
            volumen  = row['volume'].item()
            tip_op   = mt5.ORDER_TYPE_BUY if tipo_op == 1 else mt5.ORDER_TYPE_SELL
            req = {
                'action':       mt5.TRADE_ACTION_DEAL,
                'symbol':       simbolo,
                'volume':       volumen,
                'type':         tip_op,
                'position':     operacion,
                'comment':      'Cerrar posiciones',
                'type_filling': filling_mode,
            }
            mt5.order_send(req)

    # ── Posiciones ────────────────────────────────────────────────────────────

    def get_opened_positions(self, par=None) -> tuple:
        try:
            o_pos = mt5.positions_get()
            df = pd.DataFrame(list(o_pos), columns=o_pos[0]._asdict().keys())
            df_temp = df if par is None else df[df['symbol'] == par]
            print("Se logró obtener la historia correctamente")
            return len(df_temp), df_temp
        except:
            print("No se logró obtener la historia correctamente")
            return 0, pd.DataFrame()

    def get_all_positions(self) -> pd.DataFrame:
        try:
            mt5.initialize(login=self.nombre, server=self.servidor,
                           password=self.clave, path=self.path)
            o_pos = mt5.positions_get()
            df = pd.DataFrame(list(o_pos), columns=o_pos[0]._asdict().keys())
            print("Se logró obtener la historia correctamente")
            return df
        except:
            print("No se logró obtener la historia correctamente")
            return pd.DataFrame()

    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        try:
            ordenes = mt5.orders_get()
            return pd.DataFrame(list(ordenes), columns=ordenes[0]._asdict().keys())
        except:
            return pd.DataFrame()

    def remover_operacion_pendiente(self, nom_est, type_fill=mt5.ORDER_FILLING_FOK):
        df = self.obtener_ordenes_pendientes()
        tickets = df[df['comment'] == nom_est]['ticket'].unique().tolist()
        for ticket in tickets:
            mt5.order_send({
                'action':       mt5.TRADE_ACTION_REMOVE,
                'order':        ticket,
                'type_filling': type_fill,
            })

    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float):
        if df_pos.empty:
            print('No hay operaciones abiertas')
            return
        for op in df_pos['ticket'].tolist():
            row           = df_pos[df_pos['ticket'] == op]
            symb          = row['symbol'].iloc[0]
            stop_loss     = row['price_open'].iloc[0]
            take_profit   = row['tp'].iloc[0]
            precio_actual = row['price_current'].iloc[0]
            tipo_op       = row['type'].iloc[0]
            if tipo_op == 1 and precio_actual < stop_loss:
                self.modify_orders(symb, op, stop_loss, take_profit, mt5.ORDER_TYPE_BUY)
            if tipo_op == 0 and precio_actual > stop_loss:
                self.modify_orders(symb, op, stop_loss, take_profit, mt5.ORDER_TYPE_SELL)

    # ── Cuenta ────────────────────────────────────────────────────────────────

    def info_account(self) -> tuple:
        mt5.initialize(path=self.path, login=self.nombre,
                       password=self.clave, server=self.servidor)
        d = mt5.account_info()._asdict()
        return d['balance'], d['profit'], d['equity'], d['margin_free']

    def calculate_position_size(self, symbol, capital, per_to_risk) -> float:
        print(f"Total Account Capital: {capital}")
        leverage = mt5.account_info().leverage
        print(f"LEVERAGE: {leverage}")
        invested = capital * leverage * per_to_risk
        trade_size = mt5.symbol_info(symbol).trade_contract_size
        price = (mt5.symbol_info(symbol).ask + mt5.symbol_info(symbol).bid) / 2
        lot_size = invested / trade_size / price
        min_lot  = mt5.symbol_info(symbol).volume_min
        max_lot  = mt5.symbol_info(symbol).volume_max
        if min_lot < lot_size:
            nd = str(min_lot)[::-1].find('.')
            if nd > 0:
                lot_size = np.round(lot_size, nd)
                if lot_size < np.round(lot_size, nd):
                    lot_size = np.round(lot_size - min_lot, nd)
            else:
                ns = len(str(min_lot))
                lot_size = int(np.round(lot_size, -ns))
            lot_size = min(lot_size, max_lot)
            print(f"GOOD SIZE LOT: {lot_size}")
            return lot_size

    def get_history_data(self, from_date: datetime, nom_estrategia: str, symbol: str) -> tuple:
        history = mt5.history_deals_get(from_date, datetime.now())
        df = pd.DataFrame(list(history), columns=history[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        names = df[df['entry'] == 0][['position_id','comment']].rename(
            columns={'comment': 'strategy_name'})
        df_new  = df.merge(names, how='left', on='position_id')
        df_new  = df_new[df_new['entry'] == 1]
        df_est  = df_new[df_new['strategy_name'] == nom_estrategia]
        df_est  = df_est[df_est['symbol'] == symbol].copy()
        df_est['win'] = np.where(df_est['profit'] > 0, 1, 0)
        return df_est, df_est['win'].sum(), len(df_est)


# ══════════════════════════════════════════════════════════════════════════════
#  BROKER 2 — Interactive Brokers
# ══════════════════════════════════════════════════════════════════════════════

_IB_TIMEFRAME_MAP = {
    'M1': '1 min',  'M5': '5 mins',  'M15': '15 mins', 'M30': '30 mins',
    'H1': '1 hour', 'H4': '4 hours', 'D1':  '1 day',
    'W1': '1 week', 'MN1': '1 month',
}


class _IBBroker(_BaseBroker):

    def __init__(self, host='127.0.0.1', port=7497, client_id=1):
        if not _IB_AVAILABLE:
            raise ImportError("ib_insync no está instalado. Ejecuta: pip install ib_insync")
        self.host      = host
        self.port      = port
        self.client_id = client_id
        self.ib        = IB()
        self.ib.connect(host, port, clientId=client_id)
        self.inicializado = self.ib.isConnected()
        print(f"Conectado a IB: {self.inicializado}")

    def _get_contract(self, symbol: str) -> Contract:
        contract = (Forex(symbol) if len(symbol) == 6 and symbol.isalpha()
                    else Stock(symbol, 'SMART', 'USD'))
        self.ib.qualifyContracts(contract)
        return contract

    # ── Datos ─────────────────────────────────────────────────────────────────

    def extract_data(self, par, periodo, cantidad) -> pd.DataFrame:
        bar_size = _IB_TIMEFRAME_MAP.get(periodo, periodo)
        contract = self._get_contract(par)
        duration = f"{cantidad} D" if 'min' in bar_size or 'hour' in bar_size else f"{cantidad * 2} D"
        bars = self.ib.reqHistoricalData(contract, endDateTime='', durationStr=duration,
                                          barSizeSetting=bar_size, whatToShow='MIDPOINT',
                                          useRTH=True, formatDate=1)
        tabla = util.df(bars)
        if not tabla.empty:
            tabla = tabla.rename(columns={'date': 'time', 'volume': 'tick_volume'})
            tabla['time'] = pd.to_datetime(tabla['time'])
            tabla = tabla.tail(cantidad).reset_index(drop=True)
        return tabla

    def get_data_from_dates(self, year_ini, month_ini, day_ini,
                             year_fin, month_fin, day_fin,
                             symbol, timeframe, for_bt=False) -> pd.DataFrame:
        bar_size  = _IB_TIMEFRAME_MAP.get(timeframe, timeframe)
        contract  = self._get_contract(symbol)
        from_date = datetime(year_ini, month_ini, day_ini)
        to_date   = datetime(year_fin,  month_fin,  day_fin)
        duration  = f"{(to_date - from_date).days + 1} D"
        bars = self.ib.reqHistoricalData(contract,
                                          endDateTime=to_date.strftime('%Y%m%d %H:%M:%S'),
                                          durationStr=duration, barSizeSetting=bar_size,
                                          whatToShow='MIDPOINT', useRTH=True, formatDate=1)
        df = util.df(bars)
        if not df.empty:
            df = df.rename(columns={'date': 'time'})
            df['time'] = pd.to_datetime(df['time'])
            df = df[df['time'] >= from_date]
        if for_bt and not df.empty:
            df = df[['time','open','high','low','close','volume']].copy()
            df.columns = ['time','Open','High','Low','Close','Volume']
            df['OpenInterest'] = 0
            df = df.set_index('time')
        return df

    # ── Órdenes ───────────────────────────────────────────────────────────────

    def _open_operations(self, par, volumen, tipo_operacion, nombre_bot, sl=None, tp=None):
        contract = self._get_contract(par)
        action   = tipo_operacion

        if sl is None and tp is None:
            trade = self.ib.placeOrder(contract, MarketOrder(action, volumen, orderRef=nombre_bot))

        elif sl is not None and tp is None:
            trade = self.ib.placeOrder(contract, MarketOrder(action, volumen, orderRef=nombre_bot))
            sl_action = 'SELL' if action == 'BUY' else 'BUY'
            sl_order = StopOrder(sl_action, volumen, sl, orderRef=nombre_bot + '_SL')
            sl_order.parentId = trade.order.orderId
            self.ib.placeOrder(contract, sl_order)

        elif sl is None and tp is not None:
            trade = self.ib.placeOrder(contract, MarketOrder(action, volumen, orderRef=nombre_bot))
            tp_action = 'SELL' if action == 'BUY' else 'BUY'
            tp_order = LimitOrder(tp_action, volumen, tp, orderRef=nombre_bot + '_TP')
            tp_order.parentId = trade.order.orderId
            self.ib.placeOrder(contract, tp_order)

        else:
            bracket = self.ib.bracketOrder(action, volumen, None, tp, sl)
            for o in bracket: o.orderRef = nombre_bot
            trade = self.ib.placeOrder(contract, bracket.parent)
            self.ib.placeOrder(contract, bracket.takeProfit)
            self.ib.placeOrder(contract, bracket.stopLoss)

        print(f'Se ejecutó una {action} con un volumen de {volumen}')
        return trade

    def buy(self, symbol, volumen, nom_bot='Py', sl=None, tp=None):
        return self._open_operations(symbol, volumen, 'BUY', nom_bot, sl, tp)

    def sell(self, symbol, volumen, nom_bot='Py', sl=None, tp=None):
        return self._open_operations(symbol, volumen, 'SELL', nom_bot, sl, tp)

    def buy_limit(self, symbol, volume, price, sl=None, tp=None, nombre_bot='Py', **kwargs):
        self.ib.placeOrder(self._get_contract(symbol),
                           LimitOrder('BUY', volume, price, orderRef=nombre_bot))

    def sell_limit(self, symbol, volume, price, sl=None, tp=None, nombre_bot='Py', **kwargs):
        self.ib.placeOrder(self._get_contract(symbol),
                           LimitOrder('SELL', volume, price, orderRef=nombre_bot))

    def buy_stop(self, symbol, volume, price, sl=None, tp=None, nombre_bot='Py', **kwargs):
        self.ib.placeOrder(self._get_contract(symbol),
                           StopOrder('BUY', volume, price, orderRef=nombre_bot))

    def sell_stop(self, symbol, volume, price, sl=None, tp=None, nombre_bot='Py', **kwargs):
        self.ib.placeOrder(self._get_contract(symbol),
                           StopOrder('SELL', volume, price, orderRef=nombre_bot))

    def modify_orders(self, symb, ticket, stop_loss=None, take_profit=None,
                      type_order=None, type_fill=None):
        for trade in self.ib.openTrades():
            if trade.order.orderId == ticket:
                if stop_loss    is not None: trade.order.auxPrice = stop_loss
                if take_profit  is not None: trade.order.lmtPrice = take_profit
                self.ib.placeOrder(trade.contract, trade.order)
                break

    def close_partial(self, type_op, id_position, symbol, volume_to_close):
        return self.ib.placeOrder(self._get_contract(symbol),
                                   MarketOrder(type_op, volume_to_close, orderRef='Partial Close'))

    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=None):
        for _, row in data.iterrows():
            action = 'SELL' if row['type'] == 0 else 'BUY'
            self.ib.placeOrder(self._get_contract(row['symbol']),
                               MarketOrder(action, row['volume'], orderRef='Cerrar posiciones'))

    # ── Posiciones ────────────────────────────────────────────────────────────

    def get_opened_positions(self, par=None) -> tuple:
        try:
            records = [{'symbol': p.contract.symbol, 'volume': abs(p.position),
                        'type': 0 if p.position > 0 else 1, 'avgCost': p.avgCost,
                        'account': p.account} for p in self.ib.positions()]
            df = pd.DataFrame(records)
            if par is not None and not df.empty:
                df = df[df['symbol'] == par]
            print("Se logró obtener las posiciones correctamente")
            return len(df), df
        except Exception as e:
            print(f"No se logró obtener las posiciones: {e}")
            return 0, pd.DataFrame()

    def get_all_positions(self) -> pd.DataFrame:
        _, df = self.get_opened_positions()
        return df

    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        try:
            return pd.DataFrame([{
                'ticket':  t.order.orderId,
                'symbol':  t.contract.symbol,
                'type':    t.order.action,
                'volume':  t.order.totalQuantity,
                'price':   getattr(t.order, 'lmtPrice', None),
                'comment': t.order.orderRef,
                'status':  t.orderStatus.status,
            } for t in self.ib.openTrades()])
        except Exception as e:
            print(f"Error obteniendo órdenes pendientes: {e}")
            return pd.DataFrame()

    def remover_operacion_pendiente(self, nom_est, type_fill=None):
        df = self.obtener_ordenes_pendientes()
        if df.empty: return
        tickets = set(df[df['comment'] == nom_est]['ticket'].tolist())
        for trade in self.ib.openTrades():
            if trade.order.orderId in tickets:
                self.ib.cancelOrder(trade.order)

    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float):
        if df_pos.empty:
            print('No hay operaciones abiertas')
            return
        for _, row in df_pos.iterrows():
            tipo_op       = row['type']
            precio_open   = row.get('price_open', row.get('avgCost', 0))
            take_profit   = row.get('tp', None)
            precio_actual = row.get('price_current', precio_open)
            if take_profit is None: continue
            if tipo_op == 1 and precio_actual < precio_open:
                self.modify_orders(row['symbol'], row.get('ticket'), stop_loss=precio_open, take_profit=take_profit)
            if tipo_op == 0 and precio_actual > precio_open:
                self.modify_orders(row['symbol'], row.get('ticket'), stop_loss=precio_open, take_profit=take_profit)

    # ── Cuenta ────────────────────────────────────────────────────────────────

    def info_account(self) -> tuple:
        data = {i.tag: float(i.value) for i in self.ib.accountSummary()
                if i.currency in ('USD', '')}
        balance     = data.get('TotalCashBalance', data.get('NetLiquidation', 0.0))
        equity      = data.get('NetLiquidation', 0.0)
        profit      = data.get('UnrealizedPnL', 0.0)
        free_margin = data.get('AvailableFunds', data.get('BuyingPower', 0.0))
        return balance, profit, equity, free_margin

    def calculate_position_size(self, symbol, capital, per_to_risk) -> float:
        print(f"Total Account Capital: {capital}")
        ticker = self.ib.reqMktData(self._get_contract(symbol), '', False, False)
        self.ib.sleep(1)
        price = ((ticker.bid + ticker.ask) / 2
                 if ticker.bid and ticker.ask else ticker.last)
        print(f"PRICE: {price}")
        lot_size = (capital * per_to_risk / price) if price else 0
        print(f"Lot size weighted by risk: {lot_size}")
        return round(lot_size, 2)

    def disconnect(self):
        self.ib.disconnect()
        print("Desconectado de Interactive Brokers")


# ══════════════════════════════════════════════════════════════════════════════
#  BROKER 3 — NinjaTrader (ATI via TCP)
# ══════════════════════════════════════════════════════════════════════════════

_NT_TIMEFRAME_MAP = {
    'M1': '1', 'M5': '5', 'M15': '15', 'M30': '30',
    'H1': '60', 'H4': '240', 'D1': '1440', 'W1': '10080',
}


class _NTBroker(_BaseBroker):

    def __init__(self, host='127.0.0.1', port=36973,
                 account='Sim101', data_folder=None):
        if not _NT_AVAILABLE:
            raise ImportError("El módulo 'socket' no está disponible.")
        self.host           = host
        self.port           = port
        self.account        = account
        self.data_folder    = data_folder
        self._order_counter = 1
        try:
            self._send_command('PING')
            self.inicializado = True
            print(f"Conectado a NinjaTrader ATI en {host}:{port}")
        except Exception as e:
            self.inicializado = False
            print(f"No se pudo conectar a NinjaTrader ATI: {e}")
            print("Asegúrate de que NinjaTrader esté abierto con ATI habilitado.")

    def _send_command(self, command: str, timeout: float = 5.0) -> str:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((self.host, self.port))
            s.sendall((command + '\n').encode('utf-8'))
            response = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk: break
                    response += chunk
                    if b'\n' in chunk: break
                except socket.timeout:
                    break
        return response.decode('utf-8').strip()

    def _next_order_id(self) -> str:
        oid = f'PY_{self.account}_{self._order_counter:05d}'
        self._order_counter += 1
        return oid

    # ── Datos ─────────────────────────────────────────────────────────────────

    def extract_data(self, par, periodo, cantidad) -> pd.DataFrame:
        import os
        if self.data_folder is None:
            raise ValueError("Debes especificar data_folder en el constructor para usar extract_data.")
        filename = os.path.join(self.data_folder, f"{par}_{periodo}.csv")
        if not os.path.exists(filename):
            raise FileNotFoundError(
                f"No se encontró: {filename}\n"
                f"Exporta desde NinjaTrader: Tools → Export → Historical data")
        tabla = pd.read_csv(filename, sep=';', header=0)
        tabla.columns = [c.strip().lower() for c in tabla.columns]
        if 'date' in tabla.columns and 'time' in tabla.columns:
            tabla['time'] = pd.to_datetime(tabla['date'] + ' ' + tabla['time'])
            tabla = tabla.drop(columns=['date'])
        elif 'datetime' in tabla.columns:
            tabla['time'] = pd.to_datetime(tabla['datetime'])
            tabla = tabla.drop(columns=['datetime'])
        return tabla.sort_values('time').tail(cantidad).reset_index(drop=True)

    def get_data_from_dates(self, year_ini, month_ini, day_ini,
                             year_fin, month_fin, day_fin,
                             symbol, timeframe, for_bt=False) -> pd.DataFrame:
        tabla     = self.extract_data(symbol, timeframe, cantidad=999999)
        from_date = datetime(year_ini, month_ini, day_ini)
        to_date   = datetime(year_fin,  month_fin,  day_fin)
        df = tabla[(tabla['time'] >= from_date) & (tabla['time'] <= to_date)].copy()
        if for_bt and not df.empty:
            df = df.rename(columns={'open':'Open','high':'High','low':'Low',
                                    'close':'Close','volume':'Volume'})
            df['OpenInterest'] = 0
            df = df.set_index('time')
        return df

    # ── Órdenes ───────────────────────────────────────────────────────────────

    def _open_operations(self, par, volumen, tipo_operacion, nombre_bot, sl=None, tp=None):
        oid    = self._next_order_id()
        result = self._send_command(
            f"PLACE;{par};{self.account};{tipo_operacion};{int(volumen)};"
            f"MARKET;0;0;GTC;;{oid};{nombre_bot};1")
        print(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen} → {result}')
        if sl is not None:
            sl_action = 'SELL' if tipo_operacion == 'BUY' else 'BUY'
            self._send_command(
                f"PLACE;{par};{self.account};{sl_action};{int(volumen)};"
                f"STOP;0;{sl};GTC;;{oid}_SL;{nombre_bot}_SL;1")
        if tp is not None:
            tp_action = 'SELL' if tipo_operacion == 'BUY' else 'BUY'
            self._send_command(
                f"PLACE;{par};{self.account};{tp_action};{int(volumen)};"
                f"LIMIT;{tp};0;GTC;;{oid}_TP;{nombre_bot}_TP;1")
        return result

    def buy(self, symbol, volumen, nom_bot='Py', sl=None, tp=None):
        return self._open_operations(symbol, volumen, 'BUY', nom_bot, sl, tp)

    def sell(self, symbol, volumen, nom_bot='Py', sl=None, tp=None):
        return self._open_operations(symbol, volumen, 'SELL', nom_bot, sl, tp)

    def buy_limit(self, symbol, volume, price, expirationdate=None, type_fill=None,
                  sl=None, tp=None, nombre_bot='Py', **kwargs):
        oid = self._next_order_id()
        return self._send_command(
            f"PLACE;{symbol};{self.account};BUY;{int(volume)};"
            f"LIMIT;{price};0;GTC;;{oid};{nombre_bot};1")

    def sell_limit(self, symbol, volume, price, expirationdate=None, type_fill=None,
                   sl=None, tp=None, nombre_bot='Py', **kwargs):
        oid = self._next_order_id()
        return self._send_command(
            f"PLACE;{symbol};{self.account};SELL;{int(volume)};"
            f"LIMIT;{price};0;GTC;;{oid};{nombre_bot};1")

    def buy_stop(self, symbol, volume, price, expirationdate=None, type_fill=None,
                 sl=None, tp=None, nombre_bot='Py', **kwargs):
        oid = self._next_order_id()
        return self._send_command(
            f"PLACE;{symbol};{self.account};BUY;{int(volume)};"
            f"STOP;0;{price};GTC;;{oid};{nombre_bot};1")

    def sell_stop(self, symbol, volume, price, expirationdate=None, type_fill=None,
                  sl=None, tp=None, nombre_bot='Py', **kwargs):
        oid = self._next_order_id()
        return self._send_command(
            f"PLACE;{symbol};{self.account};SELL;{int(volume)};"
            f"STOP;0;{price};GTC;;{oid};{nombre_bot};1")

    def modify_orders(self, symb, ticket, stop_loss=None, take_profit=None,
                      type_order=None, type_fill=None):
        limit_p = take_profit if take_profit is not None else 0
        stop_p  = stop_loss   if stop_loss   is not None else 0
        self._send_command(f"CHANGE;{ticket};{limit_p};{stop_p};0")

    def close_partial(self, type_op, id_position, symbol, volume_to_close):
        return self._send_command(
            f"PLACE;{symbol};{self.account};{type_op};{int(volume_to_close)};"
            f"MARKET;0;0;GTC;;PARTIAL_{id_position};Partial Close;1")

    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=None):
        for _, row in data.iterrows():
            action = 'SELL' if row['type'] == 0 else 'BUY'
            self._send_command(
                f"PLACE;{row['symbol']};{self.account};{action};{int(row['volume'])};"
                f"MARKET;0;0;GTC;;CLOSE_{row['symbol']};Cerrar posiciones;1")

    # ── Posiciones ────────────────────────────────────────────────────────────

    def get_opened_positions(self, par=None) -> tuple:
        try:
            response = self._send_command(f"POSITIONS;{self.account}")
            records = []
            for line in response.split('\n'):
                line = line.strip()
                if not line or line == 'POSITIONS': continue
                parts = line.split('|')
                if len(parts) >= 4 and parts[1].lower() != 'flat' and float(parts[2]) > 0:
                    records.append({
                        'symbol':        parts[0],
                        'volume':        float(parts[2]),
                        'type':          0 if parts[1].lower() == 'long' else 1,
                        'price_open':    float(parts[3]),
                        'price_current': float(parts[3]),
                        'ticket':        parts[0] + '_' + parts[1],
                    })
            df = pd.DataFrame(records)
            if par is not None and not df.empty:
                df = df[df['symbol'] == par]
            print("Se logró obtener la historia correctamente")
            return len(df), df
        except Exception as e:
            print(f"No se logró obtener la historia correctamente: {e}")
            return 0, pd.DataFrame()

    def get_all_positions(self) -> pd.DataFrame:
        _, df = self.get_opened_positions()
        return df

    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        try:
            response = self._send_command(f"ORDERS;{self.account}")
            records = []
            for line in response.split('\n'):
                line = line.strip()
                if not line or line == 'ORDERS': continue
                parts = line.split('|')
                if len(parts) >= 6:
                    records.append({
                        'ticket':  parts[0], 'symbol': parts[1], 'type':   parts[2],
                        'volume':  float(parts[3]),
                        'price':   float(parts[4]) if parts[4] else None,
                        'comment': parts[5] if len(parts) > 5 else '',
                        'status':  parts[6] if len(parts) > 6 else 'Working',
                    })
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error obteniendo órdenes pendientes: {e}")
            return pd.DataFrame()

    def remover_operacion_pendiente(self, nom_est, type_fill=None):
        df = self.obtener_ordenes_pendientes()
        if df.empty: return
        for ticket in df[df['comment'] == nom_est]['ticket'].tolist():
            self._send_command(f"CANCEL;{ticket}")

    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float):
        if df_pos.empty:
            print('No hay operaciones abiertas')
            return
        for _, row in df_pos.iterrows():
            tipo_op       = row['type']
            precio_open   = row.get('price_open', 0)
            take_profit   = row.get('tp', None)
            precio_actual = row.get('price_current', precio_open)
            if take_profit is None: continue
            if tipo_op == 1 and precio_actual < precio_open:
                self.modify_orders(row['symbol'], row.get('ticket'), stop_loss=precio_open, take_profit=take_profit)
            if tipo_op == 0 and precio_actual > precio_open:
                self.modify_orders(row['symbol'], row.get('ticket'), stop_loss=precio_open, take_profit=take_profit)

    # ── Cuenta ────────────────────────────────────────────────────────────────

    def info_account(self) -> tuple:
        try:
            response = self._send_command(f"ACCOUNTDATA;{self.account}")
            data = {}
            for item in response.split('|'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    data[k.strip()] = v.strip()
            balance     = float(data.get('CashValue',      data.get('Balance',   0)))
            equity      = float(data.get('NetLiquidation', data.get('Equity',    balance)))
            profit      = float(data.get('UnrealizedPnL',  data.get('OpenPnL',   0)))
            free_margin = float(data.get('BuyingPower',    data.get('Available', equity)))
            return balance, profit, equity, free_margin
        except Exception as e:
            print(f"Error obteniendo info de cuenta: {e}")
            return 0.0, 0.0, 0.0, 0.0

    def calculate_position_size(self, symbol, capital, per_to_risk) -> float:
        print(f"Total Account Capital: {capital}")
        amount_to_risk = capital * per_to_risk
        print(f"Amount to risk: {amount_to_risk}")
        lot_size = per_to_risk  # NT no expone leverage via ATI; usar per_to_risk directamente
        print(f"Lot size weighted by risk: {lot_size}")
        return round(lot_size, 2)


# ══════════════════════════════════════════════════════════════════════════════
#  MEGACLASE — Facade unificado
# ══════════════════════════════════════════════════════════════════════════════

class EasyTrading:
    """
    Clase unificada para operar con MT5, Interactive Brokers o NinjaTrader
    con exactamente la misma interfaz de métodos.

    Parámetros
    ----------
    broker : str
        'MT5', 'IB' o 'NT'
    **kwargs : dict
        Parámetros de conexión específicos del broker:

        MT5  → nombre, clave, servidor, path
        IB   → host='127.0.0.1', port=7497, client_id=1
        NT   → host='127.0.0.1', port=36973, account='Sim101', data_folder=None

    Ejemplos
    --------
    >>> bot = EasyTrading('MT5', nombre=12345, clave='pass', servidor='Demo-Server', path='C:/MT5/terminal64.exe')
    >>> bot = EasyTrading('IB', port=7497)
    >>> bot = EasyTrading('NT', account='Sim101', data_folder='C:/Data/')

    >>> bot.buy('EURUSD', 0.1, sl=1.08, tp=1.10)
    >>> df = bot.extract_data('EURUSD', 'H1', 500)
    >>> balance, profit, equity, margin = bot.info_account()
    >>> pct = bot.kelly_criterion_pct_risk(win_rate=0.55, profit_factor=1.5)
    >>> news = bot.get_today_calendar()
    """

    _BROKERS = {
        'MT5': _MT5Broker,
        'IB':  _IBBroker,
        'NT':  _NTBroker,
    }

    def __init__(self, broker: str, **kwargs):
        broker_key = broker.upper()
        if broker_key not in self._BROKERS:
            raise ValueError(
                f"Broker '{broker}' no reconocido. Opciones válidas: {list(self._BROKERS.keys())}")
        self._broker_name = broker_key
        self._broker: _BaseBroker = self._BROKERS[broker_key](**kwargs)

    @property
    def inicializado(self) -> bool:
        """True si la conexión con el broker está activa."""
        return self._broker.inicializado

    @property
    def broker(self) -> str:
        """Nombre del broker activo ('MT5', 'IB' o 'NT')."""
        return self._broker_name

    def __getattr__(self, name: str):
        """
        Delega cualquier método o atributo al broker subyacente.
        Esto permite añadir nuevos métodos a los brokers sin modificar EasyTrading.
        """
        return getattr(self._broker, name)

    def __repr__(self) -> str:
        status = 'conectado' if self.inicializado else 'desconectado'
        return f"EasyTrading(broker='{self._broker_name}', status='{status}')"
