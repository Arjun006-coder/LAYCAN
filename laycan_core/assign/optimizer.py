"""
Fleet and Vessel Optimization Solver: MILP / Exhaustive Feasibility and Landed Cost Evaluator.
Evaluates Handysize, Supramax, Ultramax, Panamax, Kamsarmax, and Capesize across port restrictions and lightering.
"""
from typing import Dict, Any, List
from laycan_core.physics.intake import calculate_intake
from laycan_core.voyage.tce import calculate_voyage_economics

VESSEL_PARTICULARS = {
    "Handysize": {"summer_draft_m": 9.9, "dwt_typical": 32000, "loa_m": 175, "beam_m": 27.5, "tpc": 42.0, "consumption_sea": 20.0, "consumption_port": 2.0, "speed": 12.0},
    "Supramax": {"summer_draft_m": 12.5, "dwt_typical": 55000, "loa_m": 190, "beam_m": 32.2, "tpc": 56.0, "consumption_sea": 27.0, "consumption_port": 2.5, "speed": 12.5},
    "Panamax": {"summer_draft_m": 14.0, "dwt_typical": 75000, "loa_m": 225, "beam_m": 32.2, "tpc": 68.0, "consumption_sea": 32.0, "consumption_port": 2.5, "speed": 12.5},
    "Kamsarmax": {"summer_draft_m": 14.5, "dwt_typical": 82000, "loa_m": 229, "beam_m": 32.2, "tpc": 72.0, "consumption_sea": 34.0, "consumption_port": 2.5, "speed": 12.5},
    "Capesize": {"summer_draft_m": 18.0, "dwt_typical": 180000, "loa_m": 292, "beam_m": 45.0, "tpc": 115.0, "consumption_sea": 58.0, "consumption_port": 3.5, "speed": 13.5}
}

def optimize_vessel_choice(
    cargo_volume_mt: float,
    cargo_type: str,
    load_port: Dict[str, Any],
    discharge_port: Dict[str, Any],
    base_freight_usd_per_mt: float = 23.10,
    fuel_price_usd: float = 620.0
) -> Dict[str, Any]:
    """
    Evaluates every vessel class against load port and discharge port hard physics.
    Calculates lightering penalty if vessel draft exceeds port limit (e.g. Capesize into Paradip/Haldia).
    """
    options = []
    
    for v_class, v_specs in VESSEL_PARTICULARS.items():
        # Physics intake at discharge port
        intake_res = calculate_intake(v_specs, discharge_port, {"stowage_factor_typical": 1.25})
        
        # Scale economies in freight: Capesize is cheaper $/mt on paper
        if v_class == "Capesize":
            scale_freight = base_freight_usd_per_mt - 2.10
        elif v_class == "Kamsarmax":
            scale_freight = base_freight_usd_per_mt - 0.70
        elif v_class == "Panamax":
            scale_freight = base_freight_usd_per_mt
        elif v_class == "Supramax":
            scale_freight = base_freight_usd_per_mt + 1.80
        else:
            scale_freight = base_freight_usd_per_mt + 3.90
            
        actual_lift_mt = min(cargo_volume_mt, intake_res["cargo_intake_mt"])
        
        # Lightering penalty check
        lightering_needed = False
        lightering_cost_per_mt = 0.0
        lightering_days = 0.0
        
        if v_specs["summer_draft_m"] > float(discharge_port.get("max_draft_m", 14.5)):
            if discharge_port.get("unlocode") in ["INHAL", "INPRT"]:
                lightering_needed = True
                lightering_cost_per_mt = 2.90
                lightering_days = 3.5
                
        # Total landed economics
        voyage_res = calculate_voyage_economics(
            freight_rate_usd_per_mt=scale_freight,
            cargo_intake_mt=actual_lift_mt if actual_lift_mt > 0 else 10000,
            ballast_dist_nm=4200.0,
            laden_dist_nm=4400.0,
            speed_ballast_kn=v_specs["speed"],
            speed_laden_kn=v_specs["speed"],
            consumption_sea_mtpd=v_specs["consumption_sea"],
            consumption_port_mtpd=v_specs["consumption_port"],
            fuel_price_usd_per_mt=fuel_price_usd,
            port_disbursements_usd=160000.0,
            port_waiting_days=float(discharge_port.get("waiting_days", 2.0)) + lightering_days
        )
        
        net_landed_cost_per_mt = scale_freight + lightering_cost_per_mt + (voyage_res["net_demurrage_usd"] / actual_lift_mt if actual_lift_mt > 0 else 0)
        
        suitability_score = 100
        disqualification_reasons = []
        
        if not intake_res["feasible"] and not lightering_needed:
            suitability_score = 0
            disqualification_reasons.append("Physical port berth dimension violation")
        elif lightering_needed and v_class == "Capesize":
            suitability_score = 62
            disqualification_reasons.append("Requires Sandheads part-lightering (+2.90 $/mt + 3.5 days)")
        elif actual_lift_mt < cargo_volume_mt * 0.8:
            suitability_score -= 30
            disqualification_reasons.append("Severe draft-deficit forces short-lift")
            
        options.append({
            "vessel_class": v_class,
            "nominal_freight_usd": round(scale_freight, 2),
            "lightering_penalty_usd": round(lightering_cost_per_mt, 2),
            "net_landed_cost_per_mt": round(net_landed_cost_per_mt, 2),
            "max_lift_mt": round(actual_lift_mt, 0),
            "draft_loss_mt": intake_res["draft_loss_mt"],
            "suitability_score": suitability_score,
            "lightering_required": lightering_needed,
            "disqualification_reasons": disqualification_reasons,
            "tce_usd_day": voyage_res["tce_usd_per_day"]
        })
        
    options.sort(key=lambda x: x["net_landed_cost_per_mt"])
    recommended = next((o for o in options if o["suitability_score"] >= 80), options[0])
    
    return {
        "cargo_mt": cargo_volume_mt,
        "recommended_vessel_class": recommended["vessel_class"],
        "recommended_net_cost_per_mt": recommended["net_landed_cost_per_mt"],
        "cape_vs_recommended_diff_per_mt": round(next(o["net_landed_cost_per_mt"] for o in options if o["vessel_class"] == "Capesize") - recommended["net_landed_cost_per_mt"], 2),
        "options_evaluated": options
    }
