"""
Least-Squares Monte Carlo (Longstaff-Schwartz) Optimal Stopping Engine.
Determines daily reservation rate R*(t): Fix today if Market Rate <= R*(t), else WAIT.
"""
import numpy as np
from typing import Dict, Any, List

def solve_optimal_stopping(
    current_market_rate: float,
    days_to_laycan_close: int,
    mean_rate: float = 22.5,
    kappa_mean_reversion: float = 0.08,
    volatility: float = 0.28,
    num_simulated_paths: int = 2000,
    late_penalty_per_day: float = 0.75
) -> Dict[str, Any]:
    """
    Solves optimal stopping backward induction across M simulated future rate paths.
    At step t:
      Continuation Value C_t = E[ V_{t+1} | State_t ] estimated via polynomial regression.
      Action: FIX if R_t <= C_t, else WAIT.
      Reservation rate R*(t) is the exact continuation value threshold.
    """
    dt = 1.0 / 365.0
    T = max(1, days_to_laycan_close)
    
    # 1. Simulate Ornstein-Uhlenbeck paths for market rate
    paths = np.zeros((num_simulated_paths, T + 1))
    paths[:, 0] = current_market_rate
    
    for t in range(T):
        dw = np.random.normal(0, np.sqrt(dt), num_simulated_paths)
        # d ln(R) = kappa * (ln(mean) - ln(R)) dt + sigma * dW
        log_rates = np.log(paths[:, t])
        d_log = kappa_mean_reversion * (np.log(mean_rate) - log_rates) * dt + volatility * dw
        paths[:, t + 1] = np.exp(log_rates + d_log)
        
    # 2. Terminal value at day T (Must fix + penalty if too late)
    # Goal is to MINIMIZE freight purchase cost
    cash_flows = paths[:, -1] + late_penalty_per_day * 2.0
    
    reservation_curve = []
    
    # 3. Backward induction (Longstaff-Schwartz for American Option / Optimal Stopping)
    for t in range(T - 1, 0, -1):
        rates_t = paths[:, t]
        
        # Basis functions for regression: 1, R_t, R_t^2
        poly_matrix = np.column_stack([np.ones_like(rates_t), rates_t, rates_t ** 2])
        coeffs, _, _, _ = np.linalg.lstsq(poly_matrix, cash_flows, rcond=None)
        
        # Estimated continuation value (expected future cost of waiting)
        continuation_value = poly_matrix @ coeffs
        
        # Policy: If fixing now is cheaper than expected waiting cost, exercise/fix
        fix_now = rates_t <= continuation_value
        cash_flows[fix_now] = rates_t[fix_now]
        
        # Mean threshold at day t
        reservation_curve.append(float(np.mean(continuation_value)))
        
    reservation_curve.reverse()
    
    # Today's reservation rate threshold
    poly_today = np.array([1.0, current_market_rate, current_market_rate ** 2])
    # Baseline regression against day 1 continuation
    today_threshold = float(mean_rate * (1.0 - 0.04 * (days_to_laycan_close / 30.0)))
    if reservation_curve:
        today_threshold = round(float(reservation_curve[0]), 2)
    else:
        today_threshold = round(current_market_rate * 0.96, 2)
        
    # Action decision
    recommended_action = "FIX_TODAY" if current_market_rate <= today_threshold else "WAIT"
    expected_savings_usd = max(0.0, current_market_rate - today_threshold) * 75000.0  # standard cargo size
    
    return {
        "current_market_rate": round(current_market_rate, 2),
        "reservation_rate_today": round(today_threshold, 2),
        "recommended_action": recommended_action,
        "days_to_deadline": days_to_laycan_close,
        "spread_pct": round(((current_market_rate - today_threshold) / current_market_rate) * 100.0, 2),
        "expected_timing_saving_usd": round(expected_savings_usd, 2),
        "reservation_curve_next_14d": [round(x, 2) for x in reservation_curve[:14]]
    }
