"""
LAYCAN Enterprise FastAPI Engine: Exposes decision memos, what-if simulations, live market state, and backtest results.
"""
import os
import sys
sys.path.append("d:/sih/SIH2026")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from agents.supervisor import run_decision_agents
from laycan_core.backtest.harness import run_decision_backtest
from laycan_core.timing.lsmc import solve_optimal_stopping
from laycan_core.assign.optimizer import optimize_vessel_choice
from ingest.portwatch import fetch_portwatch_data
from ingest.weather import fetch_marine_weather
from ingest.market import fetch_market_proxies

app = FastAPI(
    title="LAYCAN Freight Decision Engine",
    description="Intelligent Bulk Shipping Decision Intelligence & Vessel Chartering System for SAIL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CargoRequirement(BaseModel):
    cargo_ref: str = "SAIL-COK-2026-118"
    commodity: str = "Coking Coal"
    volume_mt: float = 75000.0
    origin_port: str = "Hay Point (DBCT)"
    destination_port: str = "Paradip"
    destination_unlocode: str = "INPRT"
    laycan_days: int = 14
    current_market_quote_usd: float = 23.10

class WhatIfSimulation(BaseModel):
    cargo_volume_mt: float = 75000.0
    discharge_port_unlocode: str = "INPRT"
    freight_rate_shock_pct: float = 0.0
    port_delay_days: float = 2.0

@app.get("/")
def health_check():
    return {
        "status": "ONLINE",
        "system": "LAYCAN Freight Decision Engine",
        "organization": "Steel Authority of India Limited (SAIL)",
        "version": "1.0.0"
    }

@app.get("/v1/market/state")
def get_market_state():
    market = fetch_market_proxies()
    return {
        "status": "SUCCESS",
        "market": market
    }

@app.get("/v1/port/status/{unlocode}")
def get_port_status(unlocode: str = "INPRT"):
    calls = fetch_portwatch_data(unlocode, 5)
    wx = fetch_marine_weather(unlocode)
    return {
        "port_unlocode": unlocode,
        "recent_calls": calls,
        "weather": wx
    }

@app.post("/v1/cargo/optimize")
def optimize_cargo(req: CargoRequirement):
    try:
        memo = run_decision_agents(
            cargo_ref=req.cargo_ref,
            cargo_type=req.commodity,
            cargo_volume_mt=req.volume_mt,
            origin_port=req.origin_port,
            destination_port=req.destination_port,
            destination_unlocode=req.destination_unlocode,
            laycan_days=req.laycan_days,
            current_market_quote_usd=req.current_market_quote_usd
        )
        return {"status": "SUCCESS", "decision_memo": memo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/simulation/whatif")
def simulate_whatif(sim: WhatIfSimulation):
    base_rate = 23.10 * (1.0 + sim.freight_rate_shock_pct / 100.0)
    res = optimize_vessel_choice(
        cargo_volume_mt=sim.cargo_volume_mt,
        cargo_type="Coking Coal",
        load_port={"unlocode": "AUHAY", "max_draft_m": 18.0},
        discharge_port={"unlocode": sim.discharge_port_unlocode, "max_draft_m": 16.0 if sim.discharge_port_unlocode=="INPRT" else 18.1, "waiting_days": sim.port_delay_days},
        base_freight_usd_per_mt=base_rate
    )
    return {"status": "SUCCESS", "simulation_result": res}

@app.get("/v1/backtest/results")
def get_backtest_evidence():
    backtest = run_decision_backtest()
    return {"status": "SUCCESS", "evidence": backtest}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
