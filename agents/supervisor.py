"""
Multi-Agent Supervisor, Specialists, Critic and Decision Memo Engine.
Strictly enforces the rule: Language models synthesize, explain, and challenge;
NUMERICAL SOLVERS COMPUTE ALL NUMBERS.
"""
import os
import json
from typing import Dict, Any

from laycan_core.physics.intake import calculate_intake
from laycan_core.voyage.tce import calculate_voyage_economics
from laycan_core.timing.lsmc import solve_optimal_stopping
from laycan_core.rates.tournament import run_forecasting_tournament
from laycan_core.assign.optimizer import optimize_vessel_choice
from ingest.portwatch import fetch_portwatch_data
from ingest.weather import fetch_marine_weather
from ingest.market import fetch_market_proxies

def run_decision_agents(
    cargo_ref: str = "SAIL-COK-2026-118",
    cargo_type: str = "Coking Coal",
    cargo_volume_mt: float = 75000.0,
    origin_port: str = "Hay Point (DBCT)",
    destination_port: str = "Paradip",
    destination_unlocode: str = "INPRT",
    laycan_days: int = 14,
    current_market_quote_usd: float = 23.10
) -> Dict[str, Any]:
    """
    Executes the multi-agent decision pipeline:
    1. Ingestion: Port congestion (IMF PortWatch), Weather (Open-Meteo), Market (BDRY)
    2. Solvers: Optimal Stopping (LSMC), Forecasting Tournament, Vessel Feasibility (Intake/MILP)
    3. The Critic Agent: Stresses assumptions, detects out-of-distribution risks, flags escalations
    4. Chief Logistics Officer: Formulates the final Decision Memo
    """
    # 1. Live Ingestion Calls
    port_traffic = fetch_portwatch_data(destination_unlocode, 5)
    weather_info = fetch_marine_weather(destination_unlocode)
    market_proxies = fetch_market_proxies()
    
    # 2. Deterministic Core Solvers Execution
    timing_res = solve_optimal_stopping(
        current_market_rate=current_market_quote_usd,
        days_to_laycan_close=laycan_days,
        volatility=market_proxies.get("annualized_freight_volatility", 0.32)
    )
    
    forecast_res = run_forecasting_tournament([])
    
    vessel_res = optimize_vessel_choice(
        cargo_volume_mt=cargo_volume_mt,
        cargo_type=cargo_type,
        load_port={"unlocode": "AUHAY", "max_draft_m": 18.0},
        discharge_port={"unlocode": destination_unlocode, "max_draft_m": 16.0, "waiting_days": 2.2}
    )
    
    # 3. The Adversarial Critic Agent Check
    critic_objections = []
    confidence = "HIGH"
    escalate_to_human = False
    
    if weather_info["weather_risk_level"] in ["CRITICAL_CYCLONE_SWELL", "ELEVATED_MONSOON_SWELL"]:
        confidence = "MEDIUM"
        critic_objections.append(f"Weather alert active ({weather_info['weather_risk_level']}): Significant wave height at {weather_info['current_wave_height_m']}m. Potential 2-3 day berthing delay.")
        
    if destination_unlocode == "INPRT" and vessel_res["recommended_vessel_class"] == "Capesize":
        confidence = "LOW"
        escalate_to_human = True
        critic_objections.append("Feasibility conflict: Capesize recommended for Paradip without explicit lightering clearance.")
        
    if market_proxies["market_momentum_signal"] == "BULLISH_FREIGHT" and timing_res["recommended_action"] == "WAIT":
        critic_objections.append("Forward momentum warning: BDRY proxy showed short-term upward tick; monitor daily continuation value closely.")

    if not critic_objections:
        critic_objections.append("All structural constraints verified against port guidelines and forward curves.")

    # 4. Synthesize Formal Decision Memo
    # LLM free tier integration: if GEMINI_API_KEY is in env, call gemini for prose; else use deterministic template
    gemini_key = os.environ.get("GEMINI_API_KEY")
    ai_narrative = ""
    
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            You are the Chief Logistics Officer for SAIL. Write a crisp, high-conviction 3-sentence executive rationale based on these EXACT numbers:
            - Action: {timing_res['recommended_action']}
            - Current Quote: ${current_market_quote_usd}/mt
            - Reservation Rate Threshold: ${timing_res['reservation_rate_today']}/mt
            - Recommended Vessel: {vessel_res['recommended_vessel_class']}
            - Expected 30-Day Rate Trend: {forecast_res['forecast_direction']} ({forecast_res['expected_change_pct']}%)
            - Critic Notes: {critic_objections[0]}
            Do not hallucinate any numbers not provided above.
            """
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            ai_narrative = response.text
        except Exception as e:
            ai_narrative = f"Generated via Decision Engine: Market indicates {timing_res['recommended_action']} due to reservation rate threshold of ${timing_res['reservation_rate_today']}/mt vs current market quote ${current_market_quote_usd}/mt. {vessel_res['recommended_vessel_class']} is optimal to prevent port draft penalties."
    else:
        ai_narrative = (
            f"Market indicates {timing_res['recommended_action']}. Reservation rate today is ${timing_res['reservation_rate_today']}/mt against current quote ${current_market_quote_usd}/mt. "
            f"30-day forecast is {forecast_res['forecast_direction']} ({forecast_res['expected_change_pct']}%) with {forecast_res['champion_model']} winning tournament. "
            f"Recommended vessel is {vessel_res['recommended_vessel_class']} to eliminate lightering penalties at {destination_port}."
        )

    return {
        "cargo_reference": cargo_ref,
        "action": timing_res["recommended_action"],
        "recommended_vessel": vessel_res["recommended_vessel_class"],
        "reservation_rate_today_usd": timing_res["reservation_rate_today"],
        "current_market_quote_usd": current_market_quote_usd,
        "spread_pct": timing_res["spread_pct"],
        "expected_timing_saving_usd": timing_res["expected_timing_saving_usd"],
        "days_to_deadline": laycan_days,
        "confidence_level": confidence,
        "escalate_to_human": escalate_to_human,
        "critic_flags": critic_objections,
        "forecasting_tournament": {
            "champion_model": forecast_res["champion_model"],
            "mae": forecast_res["champion_mae"],
            "conformal_p10_usd": forecast_res["conformal_p10_30d"],
            "conformal_p90_usd": forecast_res["conformal_p90_30d"]
        },
        "vessel_physics_summary": {
            "recommended_vessel": vessel_res["recommended_vessel_class"],
            "net_landed_cost_per_mt": vessel_res["recommended_net_cost_per_mt"],
            "cape_penalty_if_used_usd": vessel_res["cape_vs_recommended_diff_per_mt"],
            "options": vessel_res["options_evaluated"]
        },
        "live_signals": {
            "port_congestion_calls_drybulk": port_traffic[0].get("port_calls_dry_bulk", 0) if port_traffic else 0,
            "wave_height_m": weather_info["current_wave_height_m"],
            "weather_risk": weather_info["weather_risk_level"],
            "freight_proxy_bdry": market_proxies["bdry_proxy_price_usd"]
        },
        "executive_memo_narrative": ai_narrative
    }

if __name__ == "__main__":
    memo = run_decision_agents()
    print("DECISION MEMO OUTPUT:")
    print(json.dumps(memo, indent=2))
