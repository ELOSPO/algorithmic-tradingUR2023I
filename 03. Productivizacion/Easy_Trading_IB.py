import pandas as pd
import numpy as np
from ib_insync import IB, Stock, Forex, Future, Contract, MarketOrder, LimitOrder, StopOrder, Order
from ib_insync import util
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# Mapeo de timeframes (equivalente a los periodos de MT5)
TIMEFRAME_MAP = {
    'M1':  '1 min',
    'M5':  '5 mins',
    'M15': '15 mins',
    'M30': '30 mins',
    'H1':  '1 hour',
    'H4':  '4 hours',
    'D1':  '1 day',
    'W1':  '1 week',
    'MN1': '1 month',
}

# Tipos de orden (equivalente a mt5.ORDER_TYPE_BUY / SELL)
ORDER_TYPE_BUY  = 'BUY'
ORDER_TYPE_SELL = 'SELL'


class Basic_funcs():

    def __init__(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1):
        """
        Inicializa la conexión con Interactive Brokers TWS o IB Gateway.

        # Parámetros

        - host: Dirección IP de TWS/IB Gateway (por defecto '127.0.0.1')
        - port: Puerto de conexión (TWS paper: 7497, TWS live: 7496, Gateway paper: 4002, Gateway live: 4001)
        - client_id: ID único del cliente (diferente por cada instancia)
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)
        self.inicializado = self.ib.isConnected()
        print(f"Conectado a IB: {self.inicializado}")

    def _get_contract(self, symbol: str) -> Contract:
        """
        Crea un contrato de IB a partir de un símbolo.
        Soporta Forex (ej: 'EURUSD'), acciones (ej: 'AAPL') y futuros (ej: 'ESZ4').
        """
        if len(symbol) == 6 and symbol.isalpha():
            # Par Forex (ej: EURUSD)
            contract = Forex(symbol[:3] + symbol[3:])
        else:
            # Acción por defecto en NYSE/NASDAQ
            contract = Stock(symbol, 'SMART', 'USD')

        self.ib.qualifyContracts(contract)
        return contract

    def extract_data(self, par: str, periodo: str, cantidad: int) -> pd.DataFrame:
        """
        Extrae datos históricos de IB y los convierte en un DataFrame.

        # Parámetros

        - par: Símbolo (ej: 'EURUSD', 'AAPL')
        - periodo: Timeframe como string ('M1','M5','H1','D1', etc.)
        - cantidad: Número de barras a extraer

        """
        bar_size = TIMEFRAME_MAP.get(periodo, periodo)
        contract = self._get_contract(par)

        # Calcular el rango de tiempo necesario según cantidad de barras
        duration = f"{cantidad} D" if 'min' in bar_size or 'hour' in bar_size else f"{cantidad * 2} D"

        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1
        )

        tabla = util.df(bars)
        if tabla is None or tabla.empty:
            print(f"No se obtuvieron datos para {par} con timeframe {periodo}")
            return pd.DataFrame()

        tabla = tabla.rename(columns={'date': 'time', 'open': 'open', 'high': 'high',
                                      'low': 'low', 'close': 'close', 'volume': 'tick_volume'})
        tabla['time'] = pd.to_datetime(tabla['time'])
        tabla = tabla.tail(cantidad).reset_index(drop=True)

        return tabla

    def get_data_from_dates(self, year_ini: int, month_ini: int, day_ini: int,
                             year_fin: int, month_fin: int, day_fin: int,
                             symbol: str, timeframe: str, for_bt: bool = False) -> pd.DataFrame:
        """
        Obtiene datos históricos en un rango de fechas.
        """
        bar_size = TIMEFRAME_MAP.get(timeframe, timeframe)
        contract = self._get_contract(symbol)

        from_date = datetime(year_ini, month_ini, day_ini)
        to_date   = datetime(year_fin,  month_fin,  day_fin)
        delta_days = (to_date - from_date).days + 1
        duration = f"{delta_days} D"

        end_dt = to_date.strftime('%Y%m%d %H:%M:%S')

        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_dt,
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1
        )

        rates_frame = util.df(bars)
        if not rates_frame.empty:
            rates_frame = rates_frame.rename(columns={'date': 'time'})
            rates_frame['time'] = pd.to_datetime(rates_frame['time'])
            rates_frame = rates_frame[rates_frame['time'] >= from_date]

        if for_bt and not rates_frame.empty:
            rates_frame = rates_frame[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
            rates_frame.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume']
            rates_frame['OpenInterest'] = 0
            rates_frame = rates_frame.set_index('time')

        return rates_frame

    def _open_operations(self, par: str, volumen: float, tipo_operacion: str,
                          nombre_bot: str, sl: float = None, tp: float = None) -> object:
        """
        Función interna para abrir operaciones en IB.

        # Parámetros

        - par: Símbolo
        - volumen: Cantidad de unidades/contratos
        - tipo_operacion: ORDER_TYPE_BUY o ORDER_TYPE_SELL
        - nombre_bot: Referencia/etiqueta de la estrategia
        - sl: Stop Loss (precio)
        - tp: Take Profit (precio)
        """
        contract = self._get_contract(par)
        action = tipo_operacion  # 'BUY' o 'SELL'

        if sl is None and tp is None:
            order = MarketOrder(action, volumen, orderRef=nombre_bot)
            trade = self.ib.placeOrder(contract, order)

        elif sl is not None and tp is None:
            order = MarketOrder(action, volumen, orderRef=nombre_bot)
            trade = self.ib.placeOrder(contract, order)
            # Adjuntar stop loss como orden vinculada
            stop_action = 'SELL' if action == 'BUY' else 'BUY'
            sl_order = StopOrder(stop_action, volumen, sl, orderRef=nombre_bot + '_SL')
            sl_order.parentId = trade.order.orderId
            self.ib.placeOrder(contract, sl_order)

        elif sl is None and tp is not None:
            order = MarketOrder(action, volumen, orderRef=nombre_bot)
            trade = self.ib.placeOrder(contract, order)
            tp_action = 'SELL' if action == 'BUY' else 'BUY'
            tp_order = LimitOrder(tp_action, volumen, tp, orderRef=nombre_bot + '_TP')
            tp_order.parentId = trade.order.orderId
            self.ib.placeOrder(contract, tp_order)

        else:
            # Bracket order: entrada + SL + TP
            bracket = self.ib.bracketOrder(action, volumen, None, tp, sl)
            for o in bracket:
                o.orderRef = nombre_bot
            trade = self.ib.placeOrder(contract, bracket.parent)
            self.ib.placeOrder(contract, bracket.takeProfit)
            self.ib.placeOrder(contract, bracket.stopLoss)

        print(f'Se ejecutó una {action} con un volumen de {volumen}')
        return trade

    def buy(self, symbol: str, volumen: float, nom_bot: str = 'Py',
            sl: float = None, tp: float = None):
        """Open a long trade."""
        return self._open_operations(symbol, volumen, ORDER_TYPE_BUY, nom_bot, sl, tp)

    def sell(self, symbol: str, volumen: float, nom_bot: str = 'Py',
             sl: float = None, tp: float = None):
        """Open a short trade."""
        return self._open_operations(symbol, volumen, ORDER_TYPE_SELL, nom_bot, sl, tp)

    def buy_limit(self, symbol: str, volume: float, price: float,
                  sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        contract = self._get_contract(symbol)
        order = LimitOrder('BUY', volume, price, orderRef=nombre_bot)
        self.ib.placeOrder(contract, order)

    def sell_limit(self, symbol: str, volume: float, price: float,
                   sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        contract = self._get_contract(symbol)
        order = LimitOrder('SELL', volume, price, orderRef=nombre_bot)
        self.ib.placeOrder(contract, order)

    def buy_stop(self, symbol: str, volume: float, price: float,
                 sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        contract = self._get_contract(symbol)
        order = StopOrder('BUY', volume, price, orderRef=nombre_bot)
        self.ib.placeOrder(contract, order)

    def sell_stop(self, symbol: str, volume: float, price: float,
                  sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        contract = self._get_contract(symbol)
        order = StopOrder('SELL', volume, price, orderRef=nombre_bot)
        self.ib.placeOrder(contract, order)

    def get_opened_positions(self, par: str = None) -> tuple:
        """
        Obtiene las posiciones abiertas actuales.

        Retorna una tupla (cantidad, DataFrame).
        """
        try:
            positions = self.ib.positions()
            records = []
            for pos in positions:
                records.append({
                    'symbol':   pos.contract.symbol,
                    'volume':   abs(pos.position),
                    'type':     0 if pos.position > 0 else 1,  # 0=Buy, 1=Sell
                    'avgCost':  pos.avgCost,
                    'account':  pos.account,
                })
            df_pos = pd.DataFrame(records)

            if par is not None and not df_pos.empty:
                df_pos = df_pos[df_pos['symbol'] == par]

            print("Se logró obtener las posiciones correctamente")
            return len(df_pos), df_pos

        except Exception as e:
            print(f"No se logró obtener las posiciones: {e}")
            return 0, pd.DataFrame()

    def get_all_positions(self) -> pd.DataFrame:
        """Retorna un DataFrame con todas las posiciones abiertas."""
        _, df = self.get_opened_positions()
        return df

    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        """Obtiene las órdenes pendientes (no ejecutadas)."""
        try:
            trades = self.ib.openTrades()
            records = []
            for trade in trades:
                records.append({
                    'ticket':   trade.order.orderId,
                    'symbol':   trade.contract.symbol,
                    'type':     trade.order.action,
                    'volume':   trade.order.totalQuantity,
                    'price':    trade.order.lmtPrice if hasattr(trade.order, 'lmtPrice') else None,
                    'comment':  trade.order.orderRef,
                    'status':   trade.orderStatus.status,
                })
            df = pd.DataFrame(records)
        except Exception as e:
            print(f"Error obteniendo órdenes pendientes: {e}")
            df = pd.DataFrame()

        return df

    def remover_operacion_pendiente(self, nom_est: str, type_fill=None) -> None:
        """Cancela las órdenes pendientes de una estrategia particular."""
        df = self.obtener_ordenes_pendientes()
        if df.empty:
            return
        df_estrategia = df[df['comment'] == nom_est]
        for _, row in df_estrategia.iterrows():
            trades = self.ib.openTrades()
            for trade in trades:
                if trade.order.orderId == row['ticket']:
                    self.ib.cancelOrder(trade.order)

    def modify_orders(self, symb: str, ticket: int, stop_loss: float = None,
                      take_profit: float = None, type_order: str = ORDER_TYPE_BUY,
                      type_fill=None) -> None:
        """
        Modifica el SL y/o TP de una orden existente.
        En IB esto se hace cancelando y reemplazando la orden vinculada.
        """
        trades = self.ib.openTrades()
        for trade in trades:
            if trade.order.orderId == ticket:
                modified_order = trade.order
                if stop_loss is not None:
                    modified_order.auxPrice = stop_loss
                if take_profit is not None:
                    modified_order.lmtPrice = take_profit
                self.ib.placeOrder(trade.contract, modified_order)
                break

    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=None) -> None:
        """
        Cierra todas las operaciones contenidas en el DataFrame proporcionado.

        El DataFrame debe tener columnas: 'symbol', 'volume', 'type'
        """
        for _, row in data.iterrows():
            symbol   = row['symbol']
            volume   = row['volume']
            tipo_op  = row['type']  # 0=Buy abierto -> cerrar con Sell, 1=Sell abierto -> cerrar con Buy
            action   = ORDER_TYPE_SELL if tipo_op == 0 else ORDER_TYPE_BUY
            contract = self._get_contract(symbol)
            order = MarketOrder(action, volume, orderRef='Cerrar posiciones')
            self.ib.placeOrder(contract, order)

    def close_partial(self, type_op: str, id_position: int, symbol: str, volume_to_close: float):
        """Cierra parcialmente una posición."""
        contract = self._get_contract(symbol)
        order = MarketOrder(type_op, volume_to_close, orderRef='Partial Close')
        return self.ib.placeOrder(contract, order)

    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float) -> None:
        """
        Envía a Break Even todas las posiciones del DataFrame dado el porcentaje de recorrido.
        """
        if df_pos.empty:
            print('No hay operaciones abiertas')
            return

        for _, row in df_pos.iterrows():
            tipo_op      = row['type']
            precio_open  = row.get('price_open', row.get('avgCost', 0))
            take_profit  = row.get('tp', None)
            precio_actual = row.get('price_current', precio_open)
            ticket       = row.get('ticket', None)

            if take_profit is None:
                continue

            recorrido = abs(take_profit - precio_open) * perc_rec

            if tipo_op == 1 and precio_actual < precio_open:  # Sell en ganancia
                self.modify_orders(row['symbol'], ticket, stop_loss=precio_open, take_profit=take_profit)
            if tipo_op == 0 and precio_actual > precio_open:  # Buy en ganancia
                self.modify_orders(row['symbol'], ticket, stop_loss=precio_open, take_profit=take_profit)

    def info_account(self) -> tuple:
        """
        Retorna una tupla con (balance, profit_actual, equity, margen_libre).
        """
        summary = self.ib.accountSummary()
        data = {item.tag: float(item.value) for item in summary if item.currency == 'USD' or item.currency == ''}

        balance      = data.get('TotalCashBalance', data.get('NetLiquidation', 0.0))
        equity       = data.get('NetLiquidation', 0.0)
        profit       = data.get('UnrealizedPnL', 0.0)
        free_margin  = data.get('AvailableFunds', data.get('BuyingPower', 0.0))

        return balance, profit, equity, free_margin

    def calculate_position_size(self, symbol: str, capital: float, per_to_risk: float) -> float:
        """
        Calcula el tamaño de posición óptimo dado el capital y porcentaje de riesgo.

        # Parámetros

        - symbol: Símbolo
        - capital: Capital total de la cuenta
        - per_to_risk: Porcentaje de la cuenta a arriesgar
        """
        print(f"Total Account Capital: {capital}")

        ticker = self.ib.reqMktData(self._get_contract(symbol), '', False, False)
        self.ib.sleep(1)
        price = (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else ticker.last
        print(f"PRICE: {price}")

        amount_to_risk = capital * per_to_risk
        lot_size = amount_to_risk / price if price else 0

        print(f"Lot size weighted by risk: {lot_size}")
        return round(lot_size, 2)

    def kelly_criterion_pct_risk(self, win_rate: float, profit_factor: float) -> float:
        """
        Calcula el porcentaje de capital a arriesgar según el criterio de Kelly.

        # Parámetros

        - win_rate: Tasa de ganancia de la estrategia
        - profit_factor: Profit factor de la estrategia
        """
        k_c = (profit_factor * win_rate + win_rate - 1) / profit_factor

        if k_c < 0:
            k_c = 0.01

        return k_c

    def get_today_calendar(self) -> pd.DataFrame:
        """Retorna un DataFrame con las noticias económicas del día."""
        r = Request('https://es.investing.com/economic-calendar/', headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(r).read()
        soup = BeautifulSoup(response, "html.parser")
        table = soup.find_all(class_="js-event-item")

        result = []
        base = {}

        for bl in table:
            time_text = bl.find(class_="first left time js-time").text
            currency  = bl.find(class_="left flagCur noWrap").text.split(' ')
            intensity = bl.find_all(class_="left textNum sentiment noWrap")
            id_hour   = currency[1] + '_' + time_text

            if id_hour not in base:
                base[id_hour] = {'currency': currency[1], 'time': time_text, 'intensity': 0}

            intencity = 0
            for intence in intensity:
                _true  = intence.find_all(class_="grayFullBullishIcon")
                if   len(_true) == 1: intencity = 1
                elif len(_true) == 2: intencity = 2
                elif len(_true) == 3: intencity = 3

            base[id_hour].update({'intensity': intencity})

        for b in base:
            result.append(base[b])

        return pd.DataFrame.from_records(result)

    def disconnect(self):
        """Desconecta de TWS / IB Gateway."""
        self.ib.disconnect()
        print("Desconectado de Interactive Brokers")
