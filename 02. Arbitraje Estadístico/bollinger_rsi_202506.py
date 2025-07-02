import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

df = pd.DataFrame()

# Help about this, 'ta', extension
help(df.ta)

# List of all indicators
df.ta.indicators()


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

def enviar_operaciones(symbol,tipo_trade,volume, take_profit, stop_loss,comentario):

    trade = {'action': mt5.TRADE_ACTION_DEAL,
         'type': tipo_trade,
         'tp': take_profit,

         'symbol' : symbol,
         'volume': volume,
         'comment': comentario,
         'type_filling': mt5.ORDER_FILLING_FOK}

    return mt5.order_send(trade)

data = extraer_datos('USDJPY',9999,mt5.TIMEFRAME_D1)

data['rsi'] = ta.rsi(data['close'],14)

data['adx'] = ta.adx(data['high'],data['low'],data['close'],14).iloc[:,0]

data['stoch_k'] = ta.stoch(data['high'],data['low'],data['close'],14,3).iloc[:,0]
data['stoch_d'] = ta.stoch(data['high'],data['low'],data['close'],14,3).iloc[:,1]
data['ema'] = ta.ema(data['close'],14)
data['bbband_l'] = ta.bbands(data['close'],25,2).iloc[:,0]
data['bbband_u'] = ta.bbands(data['close'],25,2).iloc[:,2]
data['bbband_m'] = ta.bbands(data['close'],25,2).iloc[:,1]

ultimo_precio = data['close'].iloc[-1]

count_decimals = str(ultimo_precio)[::-1].find('.')
valor_pip = 10**(-count_decimals)*10

data['critical_value_up'] = data['bbband_u'] + valor_pip*10
data['critical_value_down'] = data['bbband_u'] - valor_pip*10

data['previous_close'] = data['close'].shift()
data['senal_stoch_buy'] = np.where( data['stoch_k'] < data['stoch_d'],1, 0)
data['senal_stoch_sell'] = np.where( data['stoch_k'] > data['stoch_d'],1, 0)

data['sum_stoch_sell_lag'] = data['senal_stoch_sell'].shift(-5).rolling(5).sum()
data['sum_stoch_buy_lag'] = data['senal_stoch_buy'].shift(-5).rolling(5).sum()

data['senal_compra'] = np.where( (data['previous_close'] > data['critical_value_down'] ) &
                                 (data['close'] < data['critical_value_down']) & (data['rsi'] < 30) & (data['sum_stoch_buy_lag']  > 0),1,0)

data['senal_venta'] = np.where( (data['previous_close'] <  data['critical_value_up'] ) &
                                 (data['close'] > data['critical_value_up']) & (data['rsi'] > 70) & (data['sum_stoch_sell_lag'] > 0),1,0)


data['precio_salida'] = data['close'].shift(-5)

data['profit_buy'] = (data['precio_salida'] - data['close'])*data['senal_compra']
data['profit_sell'] = (data['close'] - data['precio_salida'])*data['senal_venta']

print(data['profit_buy'].sum()/0.01)
print(data['profit_sell'].sum()/0.01)

data['stoch_k'][-200:].plot()
data['stoch_d'][-200:].plot()

# ###############################################################################################

#  Automatización de la Estrategia

def bollinger_bot(symbol,timeframe,num_minutes,bb_period,vol,bb_std,rsi_period,stoch_k,stoch_d,cr_value_bb,rsi_cr_value_up,rsi_cr_value_down,take_profit_pips,num_iterations):

    data = extraer_datos(symbol,9999,timeframe)

    data['rsi'] = ta.rsi(data['close'],rsi_period)
    data['stoch_k'] = ta.stoch(data['high'],data['low'],data['close'],stoch_k,stoch_d).iloc[:,0]
    data['stoch_d'] = ta.stoch(data['high'],data['low'],data['close'],stoch_k,stoch_d).iloc[:,1]

    data['bbband_l'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,0]
    data['bbband_u'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,2]
    data['bbband_m'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,1]

    ultimo_precio = data['close'].iloc[-1]

    count_decimals = str(ultimo_precio)[::-1].find('.')
    valor_pip = 10**(-count_decimals)*10

    data['critical_value_up'] = data['bbband_u'] + valor_pip*cr_value_bb
    data['critical_value_down'] = data['bbband_u'] - valor_pip*cr_value_bb

    data['previous_close'] = data['close'].shift()
    data['senal_stoch_buy'] = np.where( data['stoch_k'] < data['stoch_d'],1, 0)
    data['senal_stoch_sell'] = np.where( data['stoch_k'] > data['stoch_d'],1, 0)


    data['senal_compra'] = np.where( (data['previous_close'] > data['critical_value_down'] ) &
                                     (data['close'] < data['critical_value_down']) & (data['rsi'] < rsi_cr_value_down) ,1,0)

    data['senal_venta'] = np.where( (data['previous_close'] <  data['critical_value_up'] ) &
                                     (data['close'] > data['critical_value_up']) & (data['rsi'] > rsi_cr_value_up) ,1,0)


    senal_buy = data['senal_compra'].iloc[-1]
    senal_sell = data['senal_venta'].iloc[-1]

    if senal_buy == 1:
        iteracion = 0

        # While para esperar a que después de que se cumpla la señal de compra me valide 
        #  5 velas después que se cumpla otra condición.
        while iteracion < num_iterations:
            data1 = extraer_datos(symbol,100,timeframe)
            data1['stoch_k'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,0]
            data1['stoch_d'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,1]
            data1['senal_stoch_buy'] = np.where( data1['stoch_k'] < data1['stoch_d'],1, 0)
            last_close = data1['close'].iloc[-1]
            last_stoch = data1['senal_stoch_buy'].iloc[-1]

            if last_stoch == 1:
                trade = enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,vol,last_close + take_profit_pips*valor_pip,None,'BBands')
                break
            else:
                iteracion +=1

            time.sleep(num_minutes*60)

    elif senal_sell == 1:
        iteracion = 0

        # While para esperar a que después de que se cumpla la señal de compra me valide 
        #  5 velas después que se cumpla otra condición.
        while iteracion < num_iterations:
            data1 = extraer_datos(symbol,100,timeframe)
            data1['stoch_k'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,0]
            data1['stoch_d'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,1]
            data1['senal_stoch_sell'] = np.where( data1['stoch_k'] > data1['stoch_d'],1, 0)
            last_close = data1['close'].iloc[-1]
            last_stoch = data1['senal_stoch_sell'].iloc[-1]

            if last_stoch == 1:
                trade = enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,vol,last_close - take_profit_pips*valor_pip,None,'BBands')
                break
            else:
                iteracion +=1

            time.sleep(num_minutes*60)

    else:
        print('No se cumplen las condiciones')



while True:
    for symb in ['XAUUSD','USDCHF','.USTECHCash','USDJPY','NZDUSD']:
        bollinger_bot(symb,mt5.TIMEFRAME_M5,5,14,0.01,1.5,14,24,12,10,70,30,40,5)
    time.sleep(5*60)
