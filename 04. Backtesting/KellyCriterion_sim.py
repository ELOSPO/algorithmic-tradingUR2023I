import numpy as np
import matplotlib.pyplot as plt
import pandas as pd




def kelly_fraction(win_rate: float, risk_reward: float) -> float:
    """Calcula la fracción de Kelly"""
    p = win_rate
    q = 1 - p
    b = risk_reward
    f = (b * p - q) / b
    return max(f, 0) # Nunca negativo




def simulate_equity(win_rate: float, risk_reward: float, n_trades: int = 100, initial_bankroll: float = 1000):
    """Simula la evolución del equity usando Kelly"""
    f = kelly_fraction(win_rate, risk_reward)
    bankroll = [initial_bankroll]
    for _ in range(n_trades):
        bet_size = bankroll[-1] * f
        if np.random.rand() < win_rate:
            bankroll.append(bankroll[-1] + bet_size * risk_reward)
        else:
            bankroll.append(bankroll[-1] - bet_size)


    return bankroll, f




def multiple_simulations(win_rate: float, risk_reward: float, n_trades: int = 100, initial_bankroll: float = 1000, n_sims: int = 20):
    """Corre múltiples simulaciones y grafica los resultados"""
    all_runs = []
    for _ in range(n_sims):
        run, _ = simulate_equity(win_rate, risk_reward, n_trades, initial_bankroll)
        all_runs.append(run)
    return all_runs


win_rate = 0.5 # probabilidad de ganar 40%
profit_factor = 1.3 # ratio riesgo/beneficio 3:1
n_trades = 5 # número de operaciones
n_sims = 10 # número de simulaciones


# Simulación múltiple
simulations = multiple_simulations(win_rate, profit_factor, n_trades, n_sims=n_sims)
f = kelly_fraction(win_rate, profit_factor)


print(f"Fracción de Kelly: {f:.2%}")


# Plot
plt.figure(figsize=(10,6))
last_results = []
for run in simulations:
    last_results.append(run[-1])
    plt.plot(run, alpha=0.6)


plt.title(f"Evolución del Equity con Kelly (WR={win_rate*100:.1f}%, RR={profit_factor}:1, {n_sims} simulaciones)")
plt.xlabel("Número de trades")
plt.ylabel("Equity")
plt.grid(True)
plt.show()


