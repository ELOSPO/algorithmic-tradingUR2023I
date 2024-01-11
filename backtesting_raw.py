import pandas as pd
import numpy as np
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'


def backtrader_funct(symbol,periodo,atr_multiplier,name,serv,key,timeframe = mt5.TIMEFRAME_M15):

    mt5.initialize(login = name, server = serv, password = key, path = path)
    tasas_m1 = mt5.copy_rates_from_pos(symbol,timeframe,0,9000)
    tabla_tasas_m1 = pd.DataFrame(tasas_m1)

    dfst = st.supertrend(tabla_tasas_m1, period = periodo, atr_multiplier = atr_multiplier )

    dfst['previous_trend'] = dfst['in_uptrend'].shift()
    dfst['signal'] = np.where( (dfst['previous_trend'] == True) & (dfst['in_uptrend'] == False),'sell',
    np.where((dfst['previous_trend'] == False) & (dfst['in_uptrend'] == True),'buy','')
    )
    dfst['time'] = pd.to_datetime(dfst['time'],unit = 's')

    dfst[dfst['previous_trend'] != dfst['in_uptrend']]


    buys = dfst[dfst['signal'] == 'buy']
    sells = dfst[dfst['signal'] == 'sell']

    buys_time = buys['time'].tolist()
    buys_time = buys_time[:-1]
    resultados_compras = pd.DataFrame()

    for i in buys_time:
        temp_buys = buys[buys['time'] == i]
        temp_sells = sells[sells['time'] > i]
        current_sell = temp_sells[temp_sells['time'] == temp_sells['time'].min()]
        temp_buys['exit_price'] = current_sell['close'].item()
        temp_buys['exit_time'] = current_sell['time'].item()
        resultados_compras = resultados_compras.append(temp_buys)

    resultados_compras['diff_price'] = resultados_compras['exit_price'] - resultados_compras['close']
    resultados_compras['aciertos'] = np.where(resultados_compras['diff_price'] > 0,1,0)

    sells_time = sells['time'].tolist()
    sells_time = sells_time[:-1]
    resultados_ventas = pd.DataFrame()

    for i in sells_time:
        temp_sells = sells[sells['time'] == i]
        temp_buys = sells[sells['time'] > i]
        current_sell = temp_buys[temp_buys['time'] == temp_buys['time'].min()]
        temp_sells['exit_price'] = current_sell['close'].item()
        temp_sells['exit_time'] = current_sell['time'].item()
        resultados_ventas = resultados_ventas.append(temp_sells)

    resultados_ventas['diff_price'] = resultados_ventas['exit_price'] - resultados_ventas['close']
    resultados_ventas['aciertos'] = np.where(resultados_ventas['diff_price'] > 0,1,0)

    full_results = resultados_compras.append(resultados_ventas)
    full_results = full_results.sort_values('time',ascending = True)

    accuracy = resultados_ventas['aciertos'].mean()

    return accuracy


periodos = [2,6,8,9,10,15,16]
atrs = [1,2,3,4,5,6,7,8,9,10]
acc_res = []

symbol = []
for p in periodos:
    for a in atrs:
        acc_p = backtrader_funct(symbol,p,atr_multiplier = a,timeframe = mt5.TIMEFRAME_M5)
        acc_res.append(acc_p)

# Crear una función que nos permita crear las señales de compra o venta

def creacion_de_señales(name,serv,key,path,symbol,sigma,timeframe = mt5.TIMEFRAME_H1,periodo = 14):
    '''
    Función para crear la lógica de sus estrategias. 
    Se recomiendo utilizar mucho el exec().
    '''
    mt5.initialize(login = name, server = serv, password = key, path = path)
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,99000)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'],unit = 's')
    rates_frame['RSI'] = RSI(np.array(rates_frame['close']), timeperiod = periodo)
    sigma_4_rsi = sigma*rates_frame['RSI'].std()
    banda_sup = rates_frame['RSI'].mean() + sigma_4_rsi 
    banda_inf = rates_frame['RSI'].mean() - sigma_4_rsi
    rates_frame['signal'] = np.where(rates_frame['RSI'] > banda_sup, 'sell',
    np.where(rates_frame['RSI'] < banda_inf,'buy',''))

    return rates_frame

# Crear una función que me cree un SL y TP para cada señal


def crear_sl_tp(rates_frame,sl,tp):
    rates_frame['SL'] = np.where(rates_frame['signal'] == 'sell', rates_frame['close'] + sl, np.where(rates_frame['signal'] == 'buy',rates_frame['close'] - sl,0)) 
    rates_frame['TP'] = np.where(rates_frame['signal'] == 'sell', rates_frame['close'] - tp, np.where(rates_frame['signal'] == 'buy',rates_frame['close'] + tp,0))

    shorts = rates_frame[rates_frame['signal'] == 'sell']
    longs =rates_frame[rates_frame['signal'] == 'buy']

    return shorts, longs

def backtesting_shorts(rates_frame,shorts,winner_op , loser_op):
    result_values = []

    for i in range(len(shorts['time'])):
             
        data = rates_frame[rates_frame['time'] > shorts.iloc[i,0]]
        
        
        data_sl_shorts = data[(data['close'] >= shorts.iloc[i,10]) | (data['high'] >= shorts.iloc[i,10]) | (data['low'] >= shorts.iloc[i,10]) ]
        
        data_sl_shorts_min = data_sl_shorts[data_sl_shorts['time'] == data_sl_shorts['time'].min()]
        
        data_sl_shorts_min['result'] = 'loser'
        data_tp_shorts = data[(data['close'] <= shorts.iloc[i,11]) | (data['high'] <= shorts.iloc[i,11]) | (data['low'] <= shorts.iloc[i,11]) ]
        data_tp_shorts_min = data_tp_shorts[data_tp_shorts['time'] == data_tp_shorts['time'].min()]
        data_tp_shorts_min['result'] = 'winner'
        
        if len(data_tp_shorts_min) > 0 and len(data_sl_shorts_min) > 0:
            if data_tp_shorts_min.iloc[0,0] < data_sl_shorts_min.iloc[0,0]:
                resultado = 'winner'
            else:
                resultado = 'loser'
        elif len(data_tp_shorts_min) > 0 and len(data_sl_shorts_min) == 0:
            resultado = 'winner'
        else :
            resultado = 'loser'
        result_values.append(resultado)

        
            
    shorts['resultado'] = result_values
    shorts['profit'] = np.where(shorts['resultado']=='winner',winner_op , loser_op)


    return shorts

def backtesting_longs(rates_frame,longs,winner_op , loser_op):
    result_values_longs = []
    for i in range(len(longs['time'])):
        
        
        data = rates_frame[rates_frame['time'] > longs.iloc[i,0]]
        
        
        data_sl_longs = data[(data['close'] <= longs.iloc[i,10]) | (data['high'] <= longs.iloc[i,10]) | (data['low'] <= longs.iloc[i,10]) ]
        
        
        data_sl_longs_min = data_sl_longs[data_sl_longs['time'] == data_sl_longs['time'].min()]
        data_sl_longs_min['result'] = 'loser'
        data_tp_longs = data[(data['close'] >= longs.iloc[i,11]) | (data['high'] >= longs.iloc[i,11]) | (data['low'] >= longs.iloc[i,11]) ]
        data_tp_longs_min = data_tp_longs[data_tp_longs['time'] == data_tp_longs['time'].min()]
        data_tp_longs_min['result'] = 'winner'
        
        if len(data_tp_longs_min) > 0 and len(data_sl_longs_min) > 0:
            if data_tp_longs_min.iloc[0,0] < data_sl_longs_min.iloc[0,0]:
                resultado = 'winner'
            else:
                resultado = 'loser'
        elif len(data_tp_longs_min) > 0 and len(data_sl_longs_min) == 0:
            resultado = 'winner'
        else :
            resultado = 'loser'
        result_values_longs.append(resultado)

        

    longs['resultado'] = result_values_longs
    longs['profit'] = np.where(longs['resultado']=='winner',winner_op ,loser_op )

    return longs


def backtest_results_consolidated(shorts,longs):

    resultados_backtesting = pd.concat([shorts,longs])
    resultados_backtesting = resultados_backtesting.sort_values(by = ['time'])
    resultados_backtesting['ganancias'] = resultados_backtesting['profit'].cumsum()
    #resultados_backtesting['ganancias'].plot()
    profit = sum(resultados_backtesting['profit'])
    try:
        q_longs = len(longs)
    except:
        q_longs = 0
    try:
        q_shorts= len(shorts)
    except:
        q_shorts= 0
    try:
        effectiveness = len(resultados_backtesting[resultados_backtesting['resultado'] == 'winner'])/len(resultados_backtesting['resultado'])
    except:
        effectiveness = 0
    
    # av_pos_month = (q_longs + q_longs)/((datetime.now() - min(shorts['time'],longs['time']))/30.0)

    total_profit = sum(resultados_backtesting['profit'])
    minimun = resultados_backtesting['ganancias'].min()
    try:
        shorts_effectiveness = len(shorts[shorts['resultado'] == 'winner'])/len(shorts)
    except: 
        shorts_effectiveness = 0
    try:
        longs_effectiveness = len(longs[longs['resultado'] == 'winner'])/len(longs)
    except:
        longs_effectiveness = 0

    return resultados_backtesting, profit, effectiveness, total_profit, minimun, shorts_effectiveness, longs_effectiveness, q_longs, q_shorts

def handler_backtesting(symbol,sigma,sl,list_tp):
    '''
    Listas de los parámetros que queremos optimizar

    '''

    rates_frame = creacion_de_señales(name,serv,key,path,symbol,sigma)

    profits_list = []
    efec_list = []
    efe_shorts = []
    efe_longs = []
    winner_op =30
    loser_op = 30

    for i in list_tp:
        shorts, longs = crear_sl_tp(rates_frame,sl,i)
        shorts = backtesting_shorts(rates_frame,shorts,winner_op , loser_op)
        longs = backtesting_longs(rates_frame,longs,winner_op , loser_op)
        resultados_backtesting, profit, effectiveness, total_profit, minimun, shorts_effectiveness, longs_effectiveness, q_longs, q_shorts = backtest_results_consolidated(shorts,longs)

        profits_list.append(profit)
        efec_list.append(effectiveness)
        efe_shorts.append(shorts_effectiveness)
        efe_longs.append(longs_effectiveness)

        print('############## Se ejecutó un TP  ####################')

    df_resultados = pd.DataFrame(zip(list_tp,profits_list,efec_list,efe_shorts,efe_longs))
    df_resultados.columns = ['TP','profit','efect_total','efectividad_shorts','efectividad_longs']

    return df_resultados


list_tp = [0.004,0.005,0.006]
handler_backtesting('EURUSD',sigma = 2,sl = 0.008,list_tp = list_tp)