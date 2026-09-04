"""
Physics Engine: Draft-limited cargo intake solver with Hydrostatics (TPC, FWA, DWA) and Load Lines.
"""
from typing import Dict, Any, Optional
import math

def calculate_intake(
    vessel: Dict[str, Any],
    port: Dict[str, Any],
    cargo: Dict[str, Any],
    ukc_required_m: float = 1.5,
    bunkers_on_board_mt: float = 1200.0,
    fresh_water_stores_mt: float = 300.0,
    constants_mt: float = 400.0,
    water_density_kg_m3: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes maximum permissible cargo intake based on:
    1. Maximum permissible draft at berth minus under-keel clearance (UKC)
    2. Fresh Water Allowance (FWA) and Dock Water Allowance (DWA) density corrections
    3. Tonnes Per Centimetre immersion (TPC) deadweight reduction
    4. Summer DWT capacity minus operational weights (bunkers, stores, water, constants)
    5. Cargo hold cubic volume vs stowage factor (SF in m3/mt)
    """
    summer_draft = float(vessel.get("summer_draft_m", 14.5))
    summer_dwt = float(vessel.get("dwt_typical", 75000.0))
    tpc = float(vessel.get("tpc", 65.0))
    grain_cap_m3 = float(vessel.get("grain_capacity_m3", 95000.0))
    stowage_factor = float(cargo.get("stowage_factor_typical", 1.25))
    
    port_max_draft = float(port.get("max_draft_m", 14.5))
    port_max_loa = float(port.get("max_loa_m", 300.0))
    port_max_beam = float(port.get("max_beam_m", 45.0) if port.get("max_beam_m") != "unknown" else 45.0)
    
    vessel_loa = float(vessel.get("loa_m", 225.0))
    vessel_beam = float(vessel.get("beam_m", 32.2))
    
    # 1. Physical dimensions feasibility check
    feasibility_reasons = []
    is_physically_feasible = True
    
    if vessel_loa > port_max_loa:
        is_physically_feasible = False
        feasibility_reasons.append(f"LOA violation: Vessel {vessel_loa}m > Port max {port_max_loa}m")
        
    if vessel_beam > port_max_beam:
        is_physically_feasible = False
        feasibility_reasons.append(f"Beam violation: Vessel {vessel_beam}m > Port max {port_max_beam}m")
        
    # 2. Water density correction (FWA / DWA)
    rho_dock = water_density_kg_m3 if water_density_kg_m3 is not None else float(port.get("water_density", 1025.0))
    displacement_mt = summer_dwt * 1.15  # approx displacement = DWT * 1.15 for bulkers
    fwa_mm = (displacement_mt) / (4.0 * tpc) if tpc > 0 else 0.0
    dwa_mm = fwa_mm * (1025.0 - rho_dock) / 25.0
    dwa_m = dwa_mm / 1000.0
    
    # 3. Permissible laden draft in dock water
    effective_max_draft = port_max_draft - ukc_required_m + dwa_m
    
    # 4. Draft-limited DWT
    if effective_max_draft < summer_draft:
        draft_deficit_m = summer_draft - effective_max_draft
        draft_deficit_cm = draft_deficit_m * 100.0
        dwt_loss_mt = draft_deficit_cm * tpc
        available_dwt = max(0.0, summer_dwt - dwt_loss_mt)
        is_draft_limited = True
    else:
        available_dwt = summer_dwt
        is_draft_limited = False
        
    # 5. Weight-limited cargo capacity
    operational_deductions = bunkers_on_board_mt + fresh_water_stores_mt + constants_mt
    cargo_weight_limit = max(0.0, available_dwt - operational_deductions)
    
    # 6. Volume-limited cargo capacity
    cargo_volume_limit = grain_cap_m3 / stowage_factor if stowage_factor > 0 else cargo_weight_limit
    
    # 7. Final Intake
    if cargo_volume_limit < cargo_weight_limit:
        final_intake = cargo_volume_limit
        governing_constraint = "CUBIC_VOLUME_LIMITED"
    else:
        final_intake = cargo_weight_limit
        governing_constraint = "DRAFT_WEIGHT_LIMITED" if is_draft_limited else "SUMMER_DEADWEIGHT_LIMITED"
        
    if final_intake <= 0:
        is_physically_feasible = False
        feasibility_reasons.append("Zero cargo intake possible under current draft restriction.")

    return {
        "feasible": is_physically_feasible,
        "governing_constraint": governing_constraint,
        "reasons": feasibility_reasons,
        "cargo_intake_mt": round(final_intake, 1),
        "available_dwt_mt": round(available_dwt, 1),
        "summer_dwt_mt": round(summer_dwt, 1),
        "effective_max_draft_m": round(effective_max_draft, 2),
        "summer_draft_m": round(summer_draft, 2),
        "draft_loss_mt": round(max(0.0, summer_dwt - available_dwt), 1),
        "dwa_correction_m": round(dwa_m, 3),
        "water_density_kg_m3": rho_dock
    }
