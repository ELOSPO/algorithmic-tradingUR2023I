from Easy_Trading import Basic_funcs
import pandas_ta as ta
import MetaTrader5 as mt5

class Bot_bollinger():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path

        self.bfs = Basic_funcs(nombre,clave,servidor,path)
        
    def bb_bot(self,symbol,vol,timeframe,bb_window,sigma,rr_ratio,margen_sl):
        data = self.bfs.extract_data(symbol,timeframe,9999)
        bb_df = ta.bbands(data['close'],bb_window,sigma)
        ultimo_precio = data['close'].iloc[-1]
        penultimo_precio = data['close'].iloc[-2]
        diferencia_precio = ultimo_precio - penultimo_precio
        ultimo_piso = bb_df.iloc[-1,0]
        penultimo_piso = bb_df.iloc[-2,0]
        ultimo_techo = bb_df.iloc[-1,1]
        penultimo_techo = bb_df.iloc[-2,1]
        precio_medio = bb_df.iloc[-1,2]

        if (penultimo_precio < penultimo_piso) and (ultimo_precio > ultimo_piso):
            sl_price = ultimo_precio - (precio_medio-ultimo_precio)/rr_ratio
            self.bfs.buy(symbol,vol,'BB05',sl = sl_price, tp=precio_medio)

        elif (penultimo_precio > penultimo_techo) and (ultimo_precio < ultimo_techo):
            sl_price = ultimo_precio + (ultimo_precio - precio_medio)/rr_ratio
            self.bfs.sell(symbol,vol,'BB05',sl = sl_price, tp=precio_medio)

        open_trades = self.bfs.get_all_positions()

        if len(open_trades) > 0:
            try:
                open_trades_symbol = open_trades.copy()
                open_trades_symbol = open_trades_symbol[open_trades_symbol['symbol'] == symbol]
                open_trades4symbol = len(open_trades_symbol)
            except:
                open_trades4symbol = 0

            if open_trades4symbol > 0:
                ultimo_open = data['open'].iloc[-1]
                ultimo_sl = open_trades_symbol['sl']
                ultimo_tp = open_trades_symbol['tp']
                tipo_operacion = open_trades_symbol['type'].iloc[-1]
                ultimo_ticket = open_trades_symbol['ticket'].iloc[-1]

                # Lógica del margen

                numero_decimales = str(ultimo_open)[::-1].find('.')
                pip_unit = 10**(-numero_decimales + 1)

                margen = margen_sl*pip_unit

                # Logica del Trailling_stop

                if (tipo_operacion == 0) and (ultimo_open > ultimo_sl):
                    nuevo_sl = ultimo_open - margen
                    self.bfs.modify_orders(symbol,ultimo_ticket,nuevo_sl,ultimo_tp,mt5.ORDER_TYPE_BUY)
                elif (tipo_operacion == 1) and (ultimo_open < ultimo_sl):
                    nuevo_sl = ultimo_open + margen
                    self.bfs.modify_orders(symbol,ultimo_ticket,ultimo_open,ultimo_tp,mt5.ORDER_TYPE_SELL)