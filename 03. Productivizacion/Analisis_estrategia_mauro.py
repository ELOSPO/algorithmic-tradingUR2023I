import pandas as pd
import pandas_ta as ta
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)
def backtest_mauro(
    data: pd.DataFrame,   # DataFrame OHLCV con columna 'close'
    sl_pct: float,
    rsi_period: int,
    ema_period: int,
    lim_sup_rsi: float,
    lim_inf_rsi: float,
    lot_size: float = 1.0,
    output_file: str = 'backtest_mauro.xlsx'):
    """
    Backtesting de la estrategia botMauro.
    Genera un Excel con columnas: Entrada Buy, Entrada Sell, Precio Cierre, Profit.
    """

    # ── Indicadores ───────────────────────────────────────────────────────────
    data = data.copy().reset_index(drop=True)
    data['rsi']     = ta.rsi(data['close'], rsi_period)
    data['ema_200'] = ta.ema(data['close'], ema_period)
    data.dropna(inplace=True)
    data.reset_index(drop=True, inplace=True)

    # ── Simulación barra a barra ───────────────────────────────────────────────
    trades      = []
    in_position = False
    trade_type  = None   # 'buy' | 'sell'
    entry_price = None
    sl_price    = None

    for i in range(len(data)):
        close = data['close'].iloc[i]
        rsi   = data['rsi'].iloc[i]
        ema   = data['ema_200'].iloc[i]
        ts    = data['time'].iloc[i] if 'time' in data.columns else i

        # ── Gestión de posición abierta ───────────────────────────────────────
        if in_position:
            hit_sl = (trade_type == 'buy'  and close <= sl_price) or \
                     (trade_type == 'sell' and close >= sl_price)

            hit_tp = (trade_type == 'buy'  and close >= ema) or \
                     (trade_type == 'sell' and close <= ema)

            if hit_sl or hit_tp:
                profit = (close - entry_price) * lot_size if trade_type == 'buy' \
                    else (entry_price - close) * lot_size

                trades.append({
                    'Fecha Entrada': trade_open_time,
                    'Fecha Cierre':  ts,
                    'Tipo':          trade_type.upper(),
                    'Entrada Buy':   entry_price if trade_type == 'buy'  else None,
                    'Entrada Sell':  entry_price if trade_type == 'sell' else None,
                    'Precio Cierre': close,
                    'Motivo Cierre': 'SL' if hit_sl else 'EMA',
                    'Profit':        round(profit, 5),
                })
                in_position = False
                trade_type  = None
                entry_price = None

        # ── Señales de entrada (solo si no hay posición abierta) ──────────────
        if not in_position:
            if (close < ema) and (rsi < lim_inf_rsi):
                in_position     = True
                trade_type      = 'buy'
                entry_price     = close
                sl_price        = close - close * sl_pct
                trade_open_time = ts

            elif (close > ema) and (rsi > lim_sup_rsi):
                in_position     = True
                trade_type      = 'sell'
                entry_price     = close
                sl_price        = close + close * sl_pct
                trade_open_time = ts

    # ── Construir DataFrame de resultados ────────────────────────────────────
    df_trades = pd.DataFrame(trades, columns=[
        'Fecha Entrada', 'Fecha Cierre', 'Tipo',
        'Entrada Buy', 'Entrada Sell', 'Precio Cierre', 'Motivo Cierre', 'Profit'
    ])

    if df_trades.empty:
        print("No se generaron trades con los parámetros dados.")
        return df_trades

    df_trades['Profit Acumulado'] = df_trades['Profit'].cumsum().round(5)

    # ── Métricas resumen ─────────────────────────────────────────────────────
    total   = len(df_trades)
    winners = (df_trades['Profit'] > 0).sum()
    losers  = (df_trades['Profit'] < 0).sum()
    win_rate        = winners / total * 100
    profit_total    = df_trades['Profit'].sum()
    avg_win         = df_trades.loc[df_trades['Profit'] > 0, 'Profit'].mean()
    avg_loss        = df_trades.loc[df_trades['Profit'] < 0, 'Profit'].mean()
    profit_factor   = abs(avg_win / avg_loss) if avg_loss != 0 else np.inf
    max_drawdown    = (df_trades['Profit Acumulado'] - df_trades['Profit Acumulado'].cummax()).min()

    # ── Exportar a Excel ──────────────────────────────────────────────────────
    wb = Workbook()

    # ── Hoja 1: Trades ────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = 'Trades'

    thin   = Side(style='thin', color='CCCCCC')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    AZUL_OSC  = '1F4E79'
    AZUL_MED  = 'BDD7EE'
    VERDE     = '00B050'
    ROJO      = 'FF0000'
    GRIS_CLR  = 'F2F2F2'

    headers = ['Fecha Entrada', 'Fecha Cierre', 'Tipo',
               'Entrada Buy', 'Entrada Sell', 'Precio Cierre',
               'Motivo Cierre', 'Profit', 'Profit Acumulado']

    # Encabezados
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font      = Font(bold=True, color='FFFFFF', name='Arial', size=10)
        c.fill      = PatternFill('solid', start_color=AZUL_OSC)
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border    = border
    ws.row_dimensions[1].height = 22

    # Filas de datos
    for row_idx, row in df_trades.iterrows():
        excel_row = row_idx + 2
        bg = GRIS_CLR if excel_row % 2 == 0 else 'FFFFFF'

        vals = [
            row['Fecha Entrada'], row['Fecha Cierre'], row['Tipo'],
            row['Entrada Buy'],   row['Entrada Sell'], row['Precio Cierre'],
            row['Motivo Cierre'], row['Profit'],       row['Profit Acumulado']
        ]
        for col, val in enumerate(vals, 1):
            c = ws.cell(row=excel_row, column=col, value=val)
            c.font      = Font(name='Arial', size=10)
            c.alignment = Alignment(horizontal='center')
            c.border    = border
            c.fill      = PatternFill('solid', start_color=bg)

            # Color profit
            if col in (8, 9) and val is not None:
                c.font = Font(name='Arial', size=10, bold=(col == 8),
                              color=VERDE if val >= 0 else ROJO)

            # Color tipo
            if col == 3:
                c.font = Font(name='Arial', size=10, bold=True,
                              color='0070C0' if val == 'BUY' else 'FF0000')

    # Anchos de columna
    for col, w in enumerate([20, 20, 8, 14, 14, 14, 14, 12, 16], 1):
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.freeze_panes = 'A2'

    # ── Hoja 2: Resumen ───────────────────────────────────────────────────────
    ws2 = wb.create_sheet('Resumen')

    metricas = [
        ('Total Trades',      total),
        ('Trades Ganadores',  int(winners)),
        ('Trades Perdedores', int(losers)),
        ('Win Rate',          f'{win_rate:.1f}%'),
        ('Profit Total',      round(profit_total, 5)),
        ('Promedio Ganancia', round(avg_win,  5) if not np.isnan(avg_win)  else 'N/A'),
        ('Promedio Pérdida',  round(avg_loss, 5) if not np.isnan(avg_loss) else 'N/A'),
        ('Profit Factor',     round(profit_factor, 2) if profit_factor != np.inf else '∞'),
        ('Max Drawdown',      round(max_drawdown, 5)),
    ]

    ws2['A1'] = 'Resumen Backtesting - botMauro'
    ws2['A1'].font      = Font(bold=True, color='FFFFFF', name='Arial', size=13)
    ws2['A1'].fill      = PatternFill('solid', start_color=AZUL_OSC)
    ws2['A1'].alignment = Alignment(horizontal='center')
    ws2.merge_cells('A1:B1')
    ws2.row_dimensions[1].height = 28

    for r, (label, val) in enumerate(metricas, 2):
        cl = ws2.cell(row=r, column=1, value=label)
        cv = ws2.cell(row=r, column=2, value=val)
        bg = GRIS_CLR if r % 2 == 0 else 'FFFFFF'
        for c in (cl, cv):
            c.font      = Font(name='Arial', size=11)
            c.fill      = PatternFill('solid', start_color=bg)
            c.border    = border
            c.alignment = Alignment(horizontal='center' if c == cv else 'left',
                                    vertical='center')
        cl.font = Font(name='Arial', size=11, bold=True)

        # Color profit total
        if label == 'Profit Total':
            cv.font = Font(name='Arial', size=11, bold=True,
                           color=VERDE if profit_total >= 0 else ROJO)

    ws2.column_dimensions['A'].width = 22
    ws2.column_dimensions['B'].width = 18

    # Empezar en hoja Trades al abrir
    wb.active = wb['Trades']
    wb.save(output_file)
    print(f"✅ Excel guardado en: {output_file}")

    return df_trades

data = bfs.extract_data('EURUSD',mt5.TIMEFRAME_H1,9999)
trades = backtest_mauro(data,0.05,14,200,70,30,0.01)