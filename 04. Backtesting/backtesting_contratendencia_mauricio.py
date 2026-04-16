# =============================================================================
# BACKTESTING - ESTRATEGIA CONTRATENDENCIA MAURICIO
# =============================================================================
# Este archivo replica la lógica del bot productivo "botMauro" y la somete a
# un backtesting usando la librería backtesting.py para evaluar su desempeño
# histórico antes de operar con dinero real.
# =============================================================================

# --- IMPORTACIÓN DE LIBRERÍAS ---

import pandas as pd                          # Manipulación de DataFrames
import numpy as np                           # Operaciones numéricas
import pandas_ta as ta                       # Indicadores técnicos (RSI, EMA)
from backtesting import Backtest, Strategy   # Framework principal de backtesting
import MetaTrader5 as mt5                    # Conexión con MetaTrader 5 para obtener datos
from Easy_Trading import Basic_funcs         # Clase utilitaria del curso para conectar y extraer datos

# =============================================================================
# PARÁMETROS DE CONEXIÓN A METATRADER 5
# =============================================================================
# Estos datos se usan para inicializar la sesión de MT5 y poder descargar
# la data histórica de precios mediante Easy_Trading.

nombre   = 67106046                                              # Número de cuenta MT5
clave    = 'Sebas.123'                                           # Contraseña de la cuenta MT5
servidor = 'RoboForex-ECN'                                       # Servidor del broker
path     = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'  # Ruta al ejecutable de MT5

# Creamos la instancia de Basic_funcs que se encarga de inicializar MT5
# y provee métodos para descargar datos, abrir/cerrar operaciones, etc.
bfs = Basic_funcs(nombre, clave, servidor, path)

# =============================================================================
# PARÁMETROS DE LA ESTRATEGIA
# =============================================================================
# Estos valores replican exactamente los usados en el bot productivo.
# Pueden modificarse para experimentar y ver cómo cambian los resultados.

SIMBOLO      = 'EURUSD'   # Par de divisas sobre el que se hace el backtesting
TIMEFRAME    = mt5.TIMEFRAME_H1  # Marco temporal: velas de 1 hora
SL_PCT       = 0.02        # Stop Loss como porcentaje del precio de entrada (2%)
RSI_PERIOD   = 14          # Número de períodos para calcular el RSI
EMA_PERIOD   = 200         # Número de períodos para calcular la EMA
LIM_SUP_RSI  = 70          # Nivel superior del RSI: si supera este valor hay sobrecompra
LIM_INF_RSI  = 30          # Nivel inferior del RSI: si baja de este valor hay sobreventa
CAPITAL_INI  = 10_000      # Capital inicial de la cuenta en la simulación (en USD)

# Fechas del período que se desea backtestear
YEAR_INI, MES_INI, DIA_INI = 2023, 1, 1   # Fecha de inicio: 1 de enero de 2023
YEAR_FIN, MES_FIN, DIA_FIN = 2026, 4, 1   # Fecha de fin:    1 de abril de 2026

# =============================================================================
# DESCARGA DE DATOS HISTÓRICOS
# =============================================================================
# Usamos el método get_data_from_dates de Easy_Trading para descargar velas
# históricas del par y timeframe elegidos directamente desde MT5.
# El parámetro for_bt=True formatea el DataFrame con las columnas que espera
# la librería backtesting.py: Open, High, Low, Close, Volume con índice de tiempo.

datos = bfs.get_data_from_dates(
    YEAR_INI, MES_INI, DIA_INI,   # Fecha de inicio
    YEAR_FIN, MES_FIN, DIA_FIN,   # Fecha de fin
    SIMBOLO,                       # Símbolo a descargar
    TIMEFRAME,                     # Timeframe (H1 en este caso)
    True                           # for_bt=True → columnas en formato backtesting.py
)

# =============================================================================
# DEFINICIÓN DE LA ESTRATEGIA
# =============================================================================
# Para usar backtesting.py debemos crear una clase que herede de Strategy.
# Dentro de ella se implementan dos métodos obligatorios:
#   - init()  → se ejecuta UNA VEZ al inicio para preparar indicadores
#   - next()  → se ejecuta en CADA VELA para evaluar las señales de entrada/salida

class EstrategiaContratendenciaMauricio(Strategy):
    """
    Estrategia contratendencia de Mauricio:
    - COMPRA  cuando el precio está DEBAJO de la EMA200 Y el RSI está en sobreventa (<30)
      → Se espera un rebote alcista dentro de una tendencia bajista
    - VENDE   cuando el precio está ENCIMA de la EMA200 Y el RSI está en sobrecompra (>70)
      → Se espera una caída dentro de una tendencia alcista
    - CIERRE DINÁMICO: la posición se cierra cuando el precio cruza la EMA200
      (igual a la lógica del bot productivo que usa la EMA como SL dinámico)
    - STOP LOSS FIJO: se coloca a un 2% del precio de entrada como protección adicional
    """

    # Parámetros que se pueden optimizar con bt.optimize()
    # (deben declararse como atributos de clase para que backtesting.py los reconozca)
    rsi_period  = RSI_PERIOD   # Período del RSI (por defecto 14)
    ema_period  = EMA_PERIOD   # Período de la EMA (por defecto 200)
    lim_sup_rsi = LIM_SUP_RSI  # Límite superior RSI para señal de venta (por defecto 70)
    lim_inf_rsi = LIM_INF_RSI  # Límite inferior RSI para señal de compra (por defecto 30)
    sl_pct      = SL_PCT       # Porcentaje del Stop Loss (por defecto 0.02 = 2%)

    def init(self):
        """
        Método init: se llama una sola vez antes de comenzar el backtesting.
        Aquí calculamos y registramos los indicadores técnicos que usaremos.
        self.I() es el método de backtesting.py para registrar indicadores;
        garantiza que los valores estén correctamente alineados con las velas.
        """

        # Calculamos la EMA de 200 períodos sobre los precios de cierre.
        # ta.ema() devuelve una Serie de pandas con el valor de la EMA para cada vela.
        # self.I() la registra como un indicador trazable en el gráfico final.
        self.ema_200 = self.I(
            ta.ema,               # Función a aplicar
            self.data.Close,      # Serie de precios de cierre
            self.ema_period       # Período de la EMA (200)
        )

        # Calculamos el RSI de 14 períodos sobre los precios de cierre.
        # El RSI oscila entre 0 y 100; valores <30 indican sobreventa, >70 sobrecompra.
        self.rsi = self.I(
            ta.rsi,               # Función a aplicar
            self.data.Close,      # Serie de precios de cierre
            self.rsi_period       # Período del RSI (14)
        )

    def next(self):
        """
        Método next: se llama en CADA vela del período de backtesting.
        Aquí evaluamos las condiciones de entrada y salida, igual que en el bot productivo.
        self.data.Close[-1] → precio de cierre de la vela más reciente (la actual)
        self.ema_200[-1]    → valor actual de la EMA200
        self.rsi[-1]        → valor actual del RSI
        """

        # Obtenemos los valores más recientes de los indicadores y del precio
        precio_actual = self.data.Close[-1]   # Precio de cierre de la vela actual
        ema_actual    = self.ema_200[-1]      # Valor actual de la EMA de 200 períodos
        rsi_actual    = self.rsi[-1]          # Valor actual del RSI

        # Si algún indicador aún no tiene valor (período de calentamiento), salimos
        # Esto ocurre en las primeras 200 velas donde la EMA aún no está calculada
        if np.isnan(ema_actual) or np.isnan(rsi_actual):
            return  # No hacemos nada hasta que los indicadores estén disponibles

        # -----------------------------------------------------------------------
        # LÓGICA DE CIERRE DINÁMICO (igual al bot productivo)
        # -----------------------------------------------------------------------
        # El bot original cierra las operaciones cuando el precio cruza la EMA200.
        # Esto actúa como un Stop Loss dinámico que protege las ganancias.

        if self.position.is_long:
            # Si tenemos una posición de compra abierta y el precio supera la EMA200,
            # cerramos la operación (el rebote esperado se completó o se invirtió)
            if precio_actual >= ema_actual:
                self.position.close()  # Cerramos la posición de compra

        elif self.position.is_short:
            # Si tenemos una posición de venta abierta y el precio cae por debajo de la EMA200,
            # cerramos la operación (la caída esperada se completó o se invirtió)
            if precio_actual <= ema_actual:
                self.position.close()  # Cerramos la posición de venta

        # -----------------------------------------------------------------------
        # LÓGICA DE ENTRADA (señales de la estrategia contratendencia)
        # -----------------------------------------------------------------------
        # Solo abrimos una nueva operación si NO hay posición abierta actualmente
        # (equivalente a max_trades=1 en el bot productivo)

        if not self.position:  # Si no hay posición abierta

            # --- SEÑAL DE COMPRA (BUY) ---
            # Condición: precio por DEBAJO de la EMA200 (tendencia bajista)
            #            Y RSI en zona de SOBREVENTA (< 30)
            # Interpretación contratendencia: el mercado está cayendo y sobrevendido,
            # se espera un rebote alcista (comprar barato en tendencia bajista)
            if (precio_actual < ema_actual) and (rsi_actual < self.lim_inf_rsi):

                # Calculamos el Stop Loss: 2% por debajo del precio de entrada
                # (igual a: sl_price = last_close - last_close * sl_pct del bot original)
                sl_precio_compra = precio_actual * (1 - self.sl_pct)

                # Ejecutamos la orden de compra con el Stop Loss calculado
                # backtesting.py gestiona automáticamente el tamaño de la posición
                self.buy(sl=sl_precio_compra)

            # --- SEÑAL DE VENTA (SELL) ---
            # Condición: precio por ENCIMA de la EMA200 (tendencia alcista)
            #            Y RSI en zona de SOBRECOMPRA (> 70)
            # Interpretación contratendencia: el mercado está subiendo y sobrecomprado,
            # se espera una corrección a la baja (vender caro en tendencia alcista)
            elif (precio_actual > ema_actual) and (rsi_actual > self.lim_sup_rsi):

                # Calculamos el Stop Loss: 2% por encima del precio de entrada
                # (igual a: sl_price = last_close + last_close * sl_pct del bot original)
                sl_precio_venta = precio_actual * (1 + self.sl_pct)

                # Ejecutamos la orden de venta con el Stop Loss calculado
                self.sell(sl=sl_precio_venta)

# =============================================================================
# EJECUCIÓN DEL BACKTESTING
# =============================================================================
# Creamos el objeto Backtest pasándole los datos descargados y la clase de estrategia.
# cash        → capital inicial de la simulación
# commission  → comisión por operación (0.0002 = 2 pips, típico para EURUSD ECN)
# exclusive_orders → si True, cierra la posición anterior antes de abrir una nueva

bt = Backtest(
    datos,                                   # DataFrame con datos OHLCV descargados de MT5
    EstrategiaContratendenciaMauricio,       # Clase con la lógica de la estrategia
    cash=CAPITAL_INI,                        # Capital inicial: $10,000
    commission=0.0002,                       # Comisión ECN aproximada para EURUSD (2 pips ida y vuelta)
    exclusive_orders=True                    # No permite dos posiciones abiertas simultáneamente
)

# Ejecutamos el backtesting y guardamos todos los resultados en la variable 'resultados'
# El objeto resultados contiene: Return%, Sharpe Ratio, Max Drawdown, # Trades, Win Rate, etc.
resultados = bt.run()

# Imprimimos en consola el resumen completo de las métricas del backtesting
print("=" * 60)
print(f"RESULTADOS BACKTESTING - Estrategia Contratendencia Mauricio")
print(f"Símbolo: {SIMBOLO} | Timeframe: H1 | Período: {YEAR_INI}/{MES_INI}/{DIA_INI} → {YEAR_FIN}/{MES_FIN}/{DIA_FIN}")
print("=" * 60)
print(resultados)  # Muestra todas las métricas: retorno, drawdown, sharpe, etc.

# =============================================================================
# VISUALIZACIÓN
# =============================================================================
# Genera el gráfico interactivo en el navegador con:
# - El precio (velas OHLC)
# - Los indicadores (EMA200 y RSI)
# - Las entradas y salidas de cada operación (triángulos verdes/rojos)
# - El equity curve (evolución del capital a lo largo del tiempo)

bt.plot()  # Abre el gráfico en el navegador web por defecto
