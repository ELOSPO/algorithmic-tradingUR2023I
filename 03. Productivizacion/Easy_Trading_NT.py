import pandas as pd
import numpy as np
import socket
import os
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# NinjaTrader ATI (Automated Trading Interface)
# ─────────────────────────────────────────────────────────────────────────────
# Este módulo se comunica con NinjaTrader 8 a través de su ATI via TCP/IP.
# Para activarlo en NinjaTrader:
#   Tools → Options → Automated Trading Interface → Enable ATI
#   (por defecto: host 127.0.0.1, puerto 36973)
#
# Comandos ATI soportados:
#   PLACE   - Colocar una orden
#   CANCEL  - Cancelar una orden pendiente
#   CHANGE  - Modificar una orden
#   CLOSEPOSITION - Cerrar posición
#   ACCOUNTDATA   - Consultar información de la cuenta
#   POSITIONS     - Consultar posiciones abiertas
# ─────────────────────────────────────────────────────────────────────────────

# Tipos de orden (equivalente a mt5.ORDER_TYPE_BUY / SELL)
ORDER_TYPE_BUY  = 'BUY'
ORDER_TYPE_SELL = 'SELL'

# Timeframes de NinjaTrader
TIMEFRAME_MAP = {
    'M1':  '1',
    'M5':  '5',
    'M15': '15',
    'M30': '30',
    'H1':  '60',
    'H4':  '240',
    'D1':  '1440',
    'W1':  '10080',
}


class Basic_funcs():

    def __init__(self, host: str = '127.0.0.1', port: int = 36973,
                 account: str = 'Sim101', data_folder: str = None):
        """
        Inicializa la conexión con NinjaTrader 8 via ATI (TCP/IP).

        # Parámetros

        - host: IP donde corre NinjaTrader (por defecto '127.0.0.1')
        - port: Puerto ATI de NinjaTrader (por defecto 36973)
        - account: Nombre de la cuenta en NinjaTrader (ej: 'Sim101', 'Live001')
        - data_folder: Ruta a la carpeta de datos exportados de NT (opcional,
                       para extract_data via archivos CSV)

        # Prerequisito en NinjaTrader:
          Tools → Options → Automated Trading Interface → Enable ATI
        """
        self.host = host
        self.port = port
        self.account = account
        self.data_folder = data_folder
        self._order_counter = 1

        # Verificar conectividad
        try:
            self._send_command('PING')
            self.inicializado = True
            print(f"Conectado a NinjaTrader ATI en {host}:{port}")
        except Exception as e:
            self.inicializado = False
            print(f"No se pudo conectar a NinjaTrader ATI: {e}")
            print("Asegúrate de que NinjaTrader esté abierto con ATI habilitado.")

    # ─────────────────────────────────────────────────────────────────────────
    # Comunicación TCP
    # ─────────────────────────────────────────────────────────────────────────

    def _send_command(self, command: str, timeout: float = 5.0) -> str:
        """
        Envía un comando al servidor ATI de NinjaTrader y retorna la respuesta.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((self.host, self.port))
            s.sendall((command + '\n').encode('utf-8'))
            response = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if b'\n' in chunk:
                        break
                except socket.timeout:
                    break
        return response.decode('utf-8').strip()

    def _next_order_id(self) -> str:
        oid = f'PY_{self.account}_{self._order_counter:05d}'
        self._order_counter += 1
        return oid

    # ─────────────────────────────────────────────────────────────────────────
    # Órdenes de mercado
    # ─────────────────────────────────────────────────────────────────────────

    def _open_operations(self, par: str, volumen: float, tipo_operacion: str,
                          nombre_bot: str, sl: float = None, tp: float = None) -> str:
        """
        Envía una orden de mercado a NinjaTrader vía ATI.

        Formato del comando ATI PLACE:
          PLACE;instrument;account;action;qty;order_type;limit_price;stop_price;tif;oco;order_id;strategy;strategy_id

        # Parámetros

        - par: Instrumento (ej: 'EURUSD', 'ES 03-25', 'AAPL')
        - volumen: Cantidad de contratos/lotes
        - tipo_operacion: ORDER_TYPE_BUY o ORDER_TYPE_SELL
        - nombre_bot: Nombre de la estrategia / comentario
        - sl: Stop Loss (precio)
        - tp: Take Profit (precio)
        """
        order_id = self._next_order_id()

        # Orden de entrada a mercado
        cmd = (f"PLACE;{par};{self.account};{tipo_operacion};{int(volumen)};"
               f"MARKET;0;0;GTC;;{order_id};{nombre_bot};1")
        result = self._send_command(cmd)
        print(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen} → {result}')

        # Stop Loss como orden separada
        if sl is not None:
            sl_id = order_id + '_SL'
            sl_action = ORDER_TYPE_SELL if tipo_operacion == ORDER_TYPE_BUY else ORDER_TYPE_BUY
            sl_cmd = (f"PLACE;{par};{self.account};{sl_action};{int(volumen)};"
                      f"STOP;0;{sl};GTC;;{sl_id};{nombre_bot}_SL;1")
            self._send_command(sl_cmd)

        # Take Profit como orden separada
        if tp is not None:
            tp_id = order_id + '_TP'
            tp_action = ORDER_TYPE_SELL if tipo_operacion == ORDER_TYPE_BUY else ORDER_TYPE_BUY
            tp_cmd = (f"PLACE;{par};{self.account};{tp_action};{int(volumen)};"
                      f"LIMIT;{tp};0;GTC;;{tp_id};{nombre_bot}_TP;1")
            self._send_command(tp_cmd)

        return result

    def buy(self, symbol: str, volumen: float, nom_bot: str = 'Py',
            sl: float = None, tp: float = None):
        """Open a long trade."""
        return self._open_operations(symbol, volumen, ORDER_TYPE_BUY, nom_bot, sl, tp)

    def sell(self, symbol: str, volumen: float, nom_bot: str = 'Py',
             sl: float = None, tp: float = None):
        """Open a short trade."""
        return self._open_operations(symbol, volumen, ORDER_TYPE_SELL, nom_bot, sl, tp)

    def buy_limit(self, symbol: str, volume: float, price: float,
                  expirationdate=None, type_fill=None,
                  sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        order_id = self._next_order_id()
        cmd = (f"PLACE;{symbol};{self.account};BUY;{int(volume)};"
               f"LIMIT;{price};0;GTC;;{order_id};{nombre_bot};1")
        return self._send_command(cmd)

    def sell_limit(self, symbol: str, volume: float, price: float,
                   expirationdate=None, type_fill=None,
                   sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        order_id = self._next_order_id()
        cmd = (f"PLACE;{symbol};{self.account};SELL;{int(volume)};"
               f"LIMIT;{price};0;GTC;;{order_id};{nombre_bot};1")
        return self._send_command(cmd)

    def buy_stop(self, symbol: str, volume: float, price: float,
                 expirationdate=None, type_fill=None,
                 sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        order_id = self._next_order_id()
        cmd = (f"PLACE;{symbol};{self.account};BUY;{int(volume)};"
               f"STOP;0;{price};GTC;;{order_id};{nombre_bot};1")
        return self._send_command(cmd)

    def sell_stop(self, symbol: str, volume: float, price: float,
                  expirationdate=None, type_fill=None,
                  sl: float = None, tp: float = None, nombre_bot: str = 'Py'):
        order_id = self._next_order_id()
        cmd = (f"PLACE;{symbol};{self.account};SELL;{int(volume)};"
               f"STOP;0;{price};GTC;;{order_id};{nombre_bot};1")
        return self._send_command(cmd)

    # ─────────────────────────────────────────────────────────────────────────
    # Gestión de posiciones y órdenes
    # ─────────────────────────────────────────────────────────────────────────

    def get_opened_positions(self, par: str = None) -> tuple:
        """
        Obtiene las posiciones abiertas desde NinjaTrader.

        Retorna una tupla (cantidad, DataFrame).
        """
        try:
            response = self._send_command(f"POSITIONS;{self.account}")
            # Respuesta esperada: instrument|marketpos|quantity|avgprice|... por línea
            records = []
            for line in response.split('\n'):
                line = line.strip()
                if not line or line == 'POSITIONS':
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    instrument = parts[0]
                    market_pos = parts[1]  # 'Long', 'Short', 'Flat'
                    qty        = float(parts[2])
                    avg_price  = float(parts[3])
                    if market_pos.lower() != 'flat' and qty > 0:
                        records.append({
                            'symbol':       instrument,
                            'volume':       qty,
                            'type':         0 if market_pos.lower() == 'long' else 1,
                            'price_open':   avg_price,
                            'price_current': avg_price,
                            'ticket':       instrument + '_' + market_pos,
                        })

            df_pos = pd.DataFrame(records)
            if par is not None and not df_pos.empty:
                df_pos = df_pos[df_pos['symbol'] == par]

            print("Se logró obtener la historia correctamente")
            return len(df_pos), df_pos

        except Exception as e:
            print(f"No se logró obtener la historia correctamente: {e}")
            return 0, pd.DataFrame()

    def get_all_positions(self) -> pd.DataFrame:
        """Retorna un DataFrame con todas las posiciones abiertas."""
        _, df = self.get_opened_positions()
        return df

    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        """Obtiene las órdenes pendientes (no ejecutadas)."""
        try:
            response = self._send_command(f"ORDERS;{self.account}")
            records = []
            for line in response.split('\n'):
                line = line.strip()
                if not line or line == 'ORDERS':
                    continue
                parts = line.split('|')
                if len(parts) >= 6:
                    records.append({
                        'ticket':  parts[0],
                        'symbol':  parts[1],
                        'type':    parts[2],
                        'volume':  float(parts[3]),
                        'price':   float(parts[4]) if parts[4] else None,
                        'comment': parts[5] if len(parts) > 5 else '',
                        'status':  parts[6] if len(parts) > 6 else 'Working',
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
            cmd = f"CANCEL;{row['ticket']}"
            self._send_command(cmd)

    def modify_orders(self, symb: str, ticket: int, stop_loss: float = None,
                      take_profit: float = None, type_order: str = ORDER_TYPE_BUY,
                      type_fill=None) -> None:
        """
        Modifica SL y/o TP de una orden.
        Formato ATI CHANGE: CHANGE;order_id;price;stop_price;qty
        """
        limit_p = take_profit if take_profit is not None else 0
        stop_p  = stop_loss   if stop_loss   is not None else 0
        cmd = f"CHANGE;{ticket};{limit_p};{stop_p};0"
        self._send_command(cmd)

    def close_all_open_operations(self, data: pd.DataFrame, filling_mode=None) -> None:
        """
        Cierra todas las operaciones contenidas en el DataFrame.

        El DataFrame debe tener columnas: 'symbol', 'volume', 'type'
        """
        for _, row in data.iterrows():
            symbol  = row['symbol']
            volume  = row['volume']
            tipo_op = row['type']  # 0=Buy abierto → cerrar con Sell, 1=Sell abierto → cerrar con Buy
            action  = ORDER_TYPE_SELL if tipo_op == 0 else ORDER_TYPE_BUY
            cmd = (f"PLACE;{symbol};{self.account};{action};{int(volume)};"
                   f"MARKET;0;0;GTC;;CLOSE_{symbol};Cerrar posiciones;1")
            self._send_command(cmd)

    def close_partial(self, type_op: str, id_position: str, symbol: str,
                      volume_to_close: float) -> str:
        """Cierra parcialmente una posición."""
        cmd = (f"PLACE;{symbol};{self.account};{type_op};{int(volume_to_close)};"
               f"MARKET;0;0;GTC;;PARTIAL_{id_position};Partial Close;1")
        return self._send_command(cmd)

    def send_to_breakeven(self, df_pos: pd.DataFrame, perc_rec: float) -> None:
        """
        Envía a Break Even todas las posiciones del DataFrame dado el porcentaje de recorrido.
        """
        if df_pos.empty:
            print('No hay operaciones abiertas')
            return

        for _, row in df_pos.iterrows():
            tipo_op       = row['type']
            precio_open   = row.get('price_open', 0)
            take_profit   = row.get('tp', None)
            precio_actual = row.get('price_current', precio_open)
            ticket        = row.get('ticket', None)

            if take_profit is None:
                continue

            if tipo_op == 1 and precio_actual < precio_open:  # Sell en ganancia
                self.modify_orders(row['symbol'], ticket, stop_loss=precio_open, take_profit=take_profit)
            if tipo_op == 0 and precio_actual > precio_open:  # Buy en ganancia
                self.modify_orders(row['symbol'], ticket, stop_loss=precio_open, take_profit=take_profit)

    # ─────────────────────────────────────────────────────────────────────────
    # Datos históricos (via exportación CSV de NinjaTrader)
    # ─────────────────────────────────────────────────────────────────────────

    def extract_data(self, par: str, periodo: str, cantidad: int) -> pd.DataFrame:
        """
        Extrae datos históricos desde archivos CSV exportados por NinjaTrader.

        NinjaTrader puede exportar datos históricos en:
          Tools → Export → Historical data (CSV)

        El archivo CSV debe estar en self.data_folder con el nombre: {par}_{periodo}.csv

        # Parámetros

        - par: Símbolo (ej: 'EURUSD', 'ES 03-25')
        - periodo: Timeframe ('M1','M5','H1','D1', etc.)
        - cantidad: Número de barras a retornar
        """
        if self.data_folder is None:
            raise ValueError("Debes especificar data_folder en el constructor para usar extract_data.")

        filename = os.path.join(self.data_folder, f"{par}_{periodo}.csv")
        if not os.path.exists(filename):
            raise FileNotFoundError(
                f"No se encontró el archivo: {filename}\n"
                f"Exporta los datos desde NinjaTrader: Tools → Export → Historical data"
            )

        # NinjaTrader CSV: Date;Time;Open;High;Low;Close;Volume
        tabla = pd.read_csv(filename, sep=';', header=0)
        tabla.columns = [c.strip().lower() for c in tabla.columns]

        if 'date' in tabla.columns and 'time' in tabla.columns:
            tabla['time'] = pd.to_datetime(tabla['date'] + ' ' + tabla['time'])
            tabla = tabla.drop(columns=['date'])
        elif 'datetime' in tabla.columns:
            tabla['time'] = pd.to_datetime(tabla['datetime'])
            tabla = tabla.drop(columns=['datetime'])

        tabla = tabla.sort_values('time').tail(cantidad).reset_index(drop=True)
        return tabla

    def get_data_from_dates(self, year_ini: int, month_ini: int, day_ini: int,
                             year_fin: int, month_fin: int, day_fin: int,
                             symbol: str, timeframe: str, for_bt: bool = False) -> pd.DataFrame:
        """
        Filtra datos históricos del CSV de NinjaTrader en un rango de fechas.
        """
        tabla = self.extract_data(symbol, timeframe, cantidad=999999)
        from_date = datetime(year_ini, month_ini, day_ini)
        to_date   = datetime(year_fin,  month_fin,  day_fin)

        rates_frame = tabla[(tabla['time'] >= from_date) & (tabla['time'] <= to_date)].copy()

        if for_bt and not rates_frame.empty:
            col_map = {'open': 'Open', 'high': 'High', 'low': 'Low',
                       'close': 'Close', 'volume': 'Volume'}
            rates_frame = rates_frame.rename(columns=col_map)
            rates_frame['OpenInterest'] = 0
            rates_frame = rates_frame.set_index('time')

        return rates_frame

    # ─────────────────────────────────────────────────────────────────────────
    # Información de cuenta
    # ─────────────────────────────────────────────────────────────────────────

    def info_account(self) -> tuple:
        """
        Retorna una tupla con (balance, profit_actual, equity, margen_libre).
        Consulta los datos de la cuenta via ATI.
        """
        try:
            response = self._send_command(f"ACCOUNTDATA;{self.account}")
            # Respuesta esperada: campo=valor separados por '|' o ';'
            data = {}
            for item in response.split('|'):
                if '=' in item:
                    key, val = item.split('=', 1)
                    data[key.strip()] = val.strip()

            balance     = float(data.get('CashValue',      data.get('Balance',   0)))
            equity      = float(data.get('NetLiquidation', data.get('Equity',    balance)))
            profit      = float(data.get('UnrealizedPnL',  data.get('OpenPnL',   0)))
            free_margin = float(data.get('BuyingPower',    data.get('Available', equity)))

            return balance, profit, equity, free_margin

        except Exception as e:
            print(f"Error obteniendo info de cuenta: {e}")
            return 0.0, 0.0, 0.0, 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # Money Management
    # ─────────────────────────────────────────────────────────────────────────

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

    def calculate_position_size(self, symbol: str, capital: float,
                                  per_to_risk: float) -> float:
        """
        Calcula el tamaño de posición óptimo.

        # Parámetros

        - symbol: Símbolo
        - capital: Capital total de la cuenta (o diferencia precio apertura - SL)
        - per_to_risk: Porcentaje de la cuenta a arriesgar
        """
        print(f"Total Account Capital: {capital}")
        amount_to_risk = capital * per_to_risk
        print(f"Amount to risk: {amount_to_risk}")

        # NinjaTrader no expone leverage vía ATI directamente;
        # se asume leverage 1:1 para futuros/acciones (ajusta según instrumento)
        lot_size = amount_to_risk / capital if capital > 0 else 0

        print(f"Lot size weighted by risk: {lot_size}")
        return round(lot_size, 2)

    # ─────────────────────────────────────────────────────────────────────────
    # Calendario económico
    # ─────────────────────────────────────────────────────────────────────────

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
                _true = intence.find_all(class_="grayFullBullishIcon")
                if   len(_true) == 1: intencity = 1
                elif len(_true) == 2: intencity = 2
                elif len(_true) == 3: intencity = 3

            base[id_hour].update({'intensity': intencity})

        for b in base:
            result.append(base[b])

        return pd.DataFrame.from_records(result)
