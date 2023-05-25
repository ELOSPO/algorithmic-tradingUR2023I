import pandas as pd
import numpy as np
import MetaTrader5 as mt5

                                                        
class Basic_funcs():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
    
    def modify_orders(self, symb: str,ticket:int,stop_loss:float = None,take_profit:float = None,type_order = mt5.ORDER_TYPE_BUY) -> None:

        if (stop_loss != None) and (take_profit == None): 
            modify_order_request = {

                'action': mt5.TRADE_ACTION_SLTP,
                'symbol':  symb,
                'position': ticket ,
                'type': type_order,
                'sl': stop_loss,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_FOK
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
            'type_filling': mt5.ORDER_FILLING_FOK
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
            'type_filling': mt5.ORDER_FILLING_FOK
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
    
    def remover_operacion_pendiente(self,nom_est:str) -> None:
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
                                    "type_filling": mt5.ORDER_FILLING_IOC
            }

            mt5.order_send(close_pend_request)

    def open_operations(self,par:str,volumen: float,tipo_operacion:mt5,nombre_bot:str,sl:float= None,tp:float = None) -> None:
        '''
        Función para abrir operaciones en mt5. Esta funciónpuede abrir operaciones sin Stop Loss y sin Take Profit, solo con stop loss, solo con 
        take profit o con ámbos parámetros.

        # Parámetros

        - par: Símbolo a extraer
        - volumen: Lotaje de la operación
        - tipo_operacion: mt5.ORDER_TYPE_BUY o mt5.ORDER_TYPE_BUY
        - nombre_bot: Nombre de la estrategia que abre la operación

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
            "type_filling": mt5.ORDER_FILLING_FOK

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
            "type_filling": mt5.ORDER_FILLING_FOK

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
            "type_filling": mt5.ORDER_FILLING_FOK

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
            "type_filling": mt5.ORDER_FILLING_FOK

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