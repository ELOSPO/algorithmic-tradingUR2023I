import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime
                                                        
class Basic_funcs():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
    
    def modify_orders(self, symb: str,ticket:int,stop_loss:float = None,take_profit:float = None,type_order = mt5.ORDER_TYPE_BUY,type_fill=mt5.ORDER_FILLING_FOK) -> None:

        if (stop_loss != None) and (take_profit == None): 
            modify_order_request = {

                'action': mt5.TRADE_ACTION_SLTP,
                'symbol':  symb,
                'position': ticket ,
                'type': type_order,
                'sl': stop_loss,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)

        elif (stop_loss == None) and (take_profit != None): 
            modify_order_request = {

            'action': mt5.TRADE_ACTION_SLTP,
            'symbol':  symb,
            'position': ticket ,
            'type': type_order,
            'tp': take_profit,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)
        
        else:
            modify_order_request = {

            'action': mt5.TRADE_ACTION_SLTP,
            'symbol':  symb,
            'position': ticket ,
            'type': type_order,
            'tp': take_profit,
            'sl': stop_loss,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)
    
    def extract_data(self,par:str,periodo:mt5,cantidad:int) -> pd.DataFrame:
        '''
        Función para extraer los datos de MT5 y convertitlos en un DataFrame

        # Parámetros 
        
        - par: Símbolo
        - periodo: M1, M5...etc
        - cantidad: Entero con el número de registros a extraer

        '''
        mt5.initialize(login = self.nombre, password = self.clave, server = self.servidor, path = self.path)
        rates = mt5.copy_rates_from_pos(par, periodo, 0, cantidad)  
        tabla = pd.DataFrame(rates)
        tabla['time']=pd.to_datetime(tabla['time'], unit='s')

        return tabla
    
    def obtener_ordenes_pendientes(self) -> pd.DataFrame:
        '''
        Función para obtener órdenes pendientes.

        '''
        try:
            ordenes = mt5.orders_get()
            df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())
        except:
            df = pd.DataFrame()

        return df
    
    def remover_operacion_pendiente(self,nom_est:str,type_fill:mt5) -> None:
        '''
        Función para remover las órdenes pendientes de una estrategia particular
        '''
        df = self.obtener_ordenes_pendientes()
        df_estrategia = df[df['comment'] == nom_est]
        ticket_list = df_estrategia['ticket'].unique().tolist()
        for ticket in ticket_list:
            close_pend_request = {
                                    "action": mt5.TRADE_ACTION_REMOVE,
                                    "order": ticket,
                                    "type_filling": type_fill
            }

            mt5.order_send(close_pend_request)

    def open_operations(self,par:str,volumen: float,tipo_operacion:mt5,nombre_bot:str,sl:float= None,tp:float = None,type_fill= mt5.ORDER_FILLING_FOK) -> None:
        '''
        Función para abrir operaciones en mt5. Esta funciónpuede abrir operaciones sin Stop Loss y sin Take Profit, solo con stop loss, solo con 
        take profit o con ámbos parámetros.

        # Parámetros

        - par: Símbolo a extraer
        - volumen: Lotaje de la operación
        - tipo_operacion: mt5.ORDER_TYPE_BUY o mt5.ORDER_TYPE_BUY
        - nombre_bot: Nombre de la estrategia que abre la operación
        - type_fill: Política de ejecución de las órdenes FILLING_FOK o FILLING_IOC

        '''
        if (sl == None) and (tp == None):

            orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": par,
            "volume": volumen,
            "type": tipo_operacion,
            "magic": 202204,
            "comment": nombre_bot,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_fill

            }

            mt5.order_send(orden)

            print('Se ejecutó una',tipo_operacion, 'con un volumen de', volumen)
        
        elif (sl == None) and (tp != None):
            orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": par,
            "tp": tp,
            "volume": volumen,
            "type": tipo_operacion,
            "magic": 202204,
            "comment": nombre_bot,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_fill

            }

            mt5.order_send(orden)
            print('Se ejecutó una',tipo_operacion, 'con un volumen de', volumen)

        elif (sl != None) and (tp == None):
            orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": par,
            "sl": sl,
            "volume": volumen,
            "type": tipo_operacion,
            "magic": 202204,
            "comment": nombre_bot,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_fill

            }

            mt5.order_send(orden)
        
        elif (sl != None) and (tp != None):
            orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": par,
            "sl": sl,
            "tp": tp,
            "volume": volumen,
            "type": tipo_operacion,
            "magic": 202204,
            "comment": nombre_bot,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_fill

            }

            mt5.order_send(orden)
            print('Se ejecutó una',tipo_operacion, 'con un volumen de', volumen)
   
    def close_all_open_operations(self,data:pd.DataFrame) -> None:
        '''
        Cierra todas las operaciones que estén contenidas en un dataframe.

        # Parámetros

        - par: Símbolo 
        '''
        
        df_open_positions = data.copy()
        lista_ops = df_open_positions['ticket'].unique().tolist()
            

        for operacion in lista_ops:
            df_operacion = df_open_positions[df_open_positions['ticket'] == operacion]
            price_close = df_operacion['price_current']
            tipo_operacion = df_operacion['type'].item()
            simbolo_operacion = df_operacion['symbol'].item()
            volumen_operacion = df_operacion['volume'].item() 
            # 1 Sell / 0 Buy
            if tipo_operacion == 1:
                tip_op = mt5.ORDER_TYPE_BUY
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)
            if tipo_operacion == 0:
                tip_op = mt5.ORDER_TYPE_SELL
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)
   
    def get_opened_positions(self,par:str = None) -> tuple:
        '''
        Función para obtener las posiciones abiertas para cada uno de los pares
        en cada timeframe
        
        '''
         
        try:
            #mt5.initialize( login = name, server = serv, password = key, path = path)
            o_pos = mt5.positions_get()
            df_pos = pd.DataFrame (list(o_pos), columns=o_pos[0]._asdict().keys())
            if par == None:
                df_pos_temp = df_pos
            else:
                df_pos_temp = df_pos[df_pos['symbol'] == par ]

            len_d_pos = len(df_pos_temp)
            print("Se logró obtener la historia correctamente")
                
                
        except :
            len_d_pos = 0
            df_pos_temp = pd.DataFrame()
            print("No se logró obtener la historia correctamente")
                

        return len_d_pos, df_pos_temp

    def get_all_positions(self) -> pd.DataFrame:
        '''
        Función para obtener las posiciones abiertas para cada uno de los pares en cada timeframe
        '''
        try:
            mt5.initialize( login = self.nombre, server = self.servidor, password = self.clave, path = self.path)
            o_pos = mt5.positions_get()
            df_pos = pd.DataFrame (list(o_pos), columns=o_pos[0]._asdict().keys())
            print("Se logró obtener la historia correctamente")
                
        except :
            df_pos = pd.DataFrame()
            print("No se logró obtener la historia correctamente")
        
        return df_pos

    def send_to_breakeven(self,df_pos:pd.DataFrame, perc_rec:float) -> None:
        '''
        Función para enviar a Break Even todas las posiciones de un dataframe

        # Parámetros

        - df_pos_temp : Dataframe con las operaciones que se desean llevar a break_even
        - perc_recorrido: porcentaje de recorrido entre el precio de apertura y el TP para llevar la operación a BreakEven


        '''
        if df_pos.empty:
            print('No hay operaciones abiertas')
        else:
            lista_operaciones = df_pos['ticket'].tolist()
            for op in lista_operaciones:
                df_temp = df_pos[df_pos['ticket'] == op]
                symb = df_temp['symbol'].iloc[0]
                ticket = op
                stop_loss = df_temp['price_open'].iloc[0] #Esta variable es el precio de apertura stop_loss
                take_profit = df_temp['tp'].iloc[0]
                precio_actual = df_temp['price_current'].iloc[0]
                tipo_operacion = df_temp['type'].iloc[0]

                if (tipo_operacion == 1) and (precio_actual < stop_loss):
                    type_order = mt5.ORDER_TYPE_BUY
                    self.modify_orders(symb,ticket,stop_loss,take_profit,type_order)
                if (tipo_operacion == 0) and (precio_actual > stop_loss):
                    type_order = mt5.ORDER_TYPE_SELL
                    self.modify_orders(symb,ticket,stop_loss,take_profit,type_order)

    def calculate_position_size(self,symbol:str, tradeinfo:float, per_to_risk:float) -> float:
        '''
        Función para calcular el lotaje óptimo dado un símbolo, una pérdida y un porcentaje de la cuenta que se desea arriesgar.

        # Parámetros

        - symbol: Simbolo
        - tradeinfo: diferencia entre el precio de apertura y el sl en valor absoluto
        - per_to_risk: Porcentaje de la cuenta a arriesgar en cada trade

        '''
        print(symbol)

        mt5.symbol_select(symbol, True)
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)

        current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
        sl = tradeinfo
        tick_size = symbol_info.trade_tick_size

        balance = mt5.account_info().balance
        risk_per_trade = per_to_risk
        ticks_at_risk = abs(current_price - sl) / tick_size
        tick_value = symbol_info.trade_tick_value

        position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value),2)

        return position_size
    
    def get_today_calendar(self) -> pd.DataFrame:
        """Regresa un Dataframe con la información de las noticias del día contiene las columnas del simbolo y la intensidad"""
        
        r = Request('https://es.investing.com/economic-calendar/', headers={'User-Agent': 'Mozilla/5.0'})
        #r = Request('https://br.investing.com/economic-calendar/')
        response = urlopen(r).read()
        soup = BeautifulSoup(response, "html.parser")
        table = soup.find_all(class_ = "js-event-item")

        result = []
        base = {}

        for bl in table:
            time = bl.find(class_ ="first left time js-time").text
            # evento = bl.find(class_ ="left event").text
            currency = bl.find(class_ ="left flagCur noWrap").text.split(' ')
            intensity = bl.find_all(class_="left textNum sentiment noWrap")
            id_hour = currency[1] + '_' + time

            if not id_hour in base:
                #base.update({id_hour : {'currency' : currency[1], 'time' : time,'intensity' : { "1": 0,"2": 0,"3": 0} } })
                base.update({id_hour : {'currency' : currency[1], 'time' : time,'intensity' : 0 }})

            #intencity = base[id_hour]['intensity']
            intencity = 0


            for intence in intensity:
                _true = intence.find_all(class_="grayFullBullishIcon")
                _false = intence.find_all(class_="grayEmptyBullishIcon")

                if len(_true) == 1:
                    #intencity['1'] += 1
                    intencity = 1

                elif len(_true) == 2:
                    # intencity['2'] += 1
                    intencity = 2

                elif len(_true) == 3:
                    #intencity['3'] += 1
                    intencity = 3

            base[id_hour].update({'intensity' : intencity})

        for b in base:
            result.append(base[b])

        news = pd.DataFrame.from_records(result)

        return news
    
    def get_data_for_bt(self,timeframe,symbol,cantidad):

        mt5.initialize( login = self.nombre, server = self.servidor, password = self.clave, path = self.path)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, cantidad)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        data = rates_frame.copy()
        data = data.iloc[:,[0,1,2,3,4,5,7]]
        data.columns = ['time','Open','High','Low','Close','Volume','OpenInterest']
        data = data.set_index('time')

        return data
    
    def info_account(self) -> tuple:

        '''Función que retorna una tupla con el balance, el profit actual, la equidad y el margen libre de la cuenta'''

        mt5.initialize(path = self.path, login = self.nombre,password = self.clave, server= self.servidor)
        cuentaDict = mt5.account_info()._asdict()
        balance = cuentaDict["balance"]
        profit_account = cuentaDict["profit"]
        equity = cuentaDict["equity"]
        free_margin = cuentaDict["margin_free"]

        return balance, profit_account, equity, free_margin

    def get_data_from_dates(self,year_ini,month_ini,day_ini,year_fin,month_fin,day_fin,symbol,timeframe, for_bt = False) -> pd.DataFrame():
        from_date = datetime(year_ini, month_ini, day_ini)
        to_date = datetime(year_fin, month_fin, day_fin)
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')

        if for_bt == True:
            rates_frame = rates_frame.iloc[:,[0,1,2,3,4,5,7]]
            rates_frame.columns = ['time','Open','High','Low','Close','Volume','OpenInterest']
            rates_frame = rates_frame.set_index('time')
        
        return rates_frame
    
    def send_pending_order(self,symbol:str,volume:float,price:float,type_op:mt5,expirationdate,type_fill:mt5,sl:float=None,tp:float = None):

        '''Función apra enviar órdenes pendientes. Esta función siempre debe ser usada con un expiration date'''

        if (sl != None ) and (tp != None):
            
            pending_order = {
                            "action":mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "volume": volume,
                            "price": price,
                            "type": type_op,
                            "sl": sl,
                            "tp": tp,
                            "type_time":mt5.ORDER_TIME_SPECIFIED, 
                            "expiration": expirationdate, 
                            "comment": "Pivot",
                            "type_filling": type_fill

                            }

            mt5.order_send(pending_order)

        elif (sl != None) and ( tp == None):

            pending_order = {
                            "action":mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "volume": volume,
                            "price": price,
                            "type": type_op,
                            "sl": sl,
                            "type_time":mt5.ORDER_TIME_SPECIFIED, 
                            "expiration": expirationdate, 
                            "comment": "Pivot",
                            "type_filling": type_fill

                            }

            mt5.order_send(pending_order)

        elif (sl == None) and ( tp != None):

            pending_order = {
                            "action":mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "volume": volume,
                            "price": price,
                            "type": type_op,
                            "tp": tp,
                            "type_time":mt5.ORDER_TIME_SPECIFIED, 
                            "expiration": expirationdate, 
                            "comment": "Pivot",
                            "type_filling": type_fill

                            }

            mt5.order_send(pending_order)
        
        elif (sl == None) and ( tp == None):
            pending_order = {
                            "action":mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "volume": volume,
                            "price": price,
                            "type": type_op,
                            "type_time":mt5.ORDER_TIME_SPECIFIED, 
                            "expiration": expirationdate, 
                            "comment": "Pivot",
                            "type_filling": type_fill

                            }

            mt5.order_send(pending_order)
