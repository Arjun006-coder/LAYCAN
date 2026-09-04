"""
Voyage Economics Engine: TCE (Time Charter Equivalent), Admiralty Cube Law, Laytime & Demurrage.
"""
from typing import Dict, Any

def calculate_voyage_economics(
    freight_rate_usd_per_mt: float,
    cargo_intake_mt: float,
    ballast_dist_nm: float,
    laden_dist_nm: float,
    speed_ballast_kn: float,
    speed_laden_kn: float,
    consumption_sea_mtpd: float,
    consumption_port_mtpd: float,
    fuel_price_usd_per_mt: float,
    port_disbursements_usd: float,
    canal_tolls_usd: float = 0.0,
    cargo_dues_usd: float = 0.0,
    address_commission_pct: float = 2.5,
    brokerage_commission_pct: float = 1.25,
    load_rate_mtpd: float = 25000.0,
    discharge_rate_mtpd: float = 20000.0,
    port_waiting_days: float = 2.0,
    weather_delay_days: float = 0.5,
    demurrage_rate_usd_per_day: float = 25000.0,
    despatch_ratio: float = 0.5
) -> Dict[str, Any]:
    """
    Computes true Time Charter Equivalent (TCE) and voyage operational economics.
    Formula:
      Gross Freight = Freight * Q
      Commissions = Gross Freight * (addr% + brok%)
      Net Freight Revenue = Gross Freight - Commissions
      Bunkers = Sea Bunkers + Port Bunkers
      Total Voyage Cost = Bunkers + Port Disbursements + Canal Tolls + Extra Dues
      Days = Sea Days + Cargo Operations Days + Waiting/Weather Delays
      TCE = (Net Revenue - Voyage Cost + Net Demurrage/Despatch) / Total Voyage Days
    """
    # 1. Voyage Duration (Days)
    sea_days_ballast = ballast_dist_nm / (24.0 * speed_ballast_kn) if speed_ballast_kn > 0 else 0.0
    sea_days_laden = laden_dist_nm / (24.0 * speed_laden_kn) if speed_laden_kn > 0 else 0.0
    total_sea_days = sea_days_ballast + sea_days_laden
    
    cargo_days_load = cargo_intake_mt / load_rate_mtpd if load_rate_mtpd > 0 else 0.0
    cargo_days_disch = cargo_intake_mt / discharge_rate_mtpd if discharge_rate_mtpd > 0 else 0.0
    total_port_working_days = cargo_days_load + cargo_days_disch
    
    total_voyage_days = total_sea_days + total_port_working_days + port_waiting_days + weather_delay_days
    
    # 2. Fuel Consumption & Cost (Cube law application at sea)
    sea_fuel_mt = total_sea_days * consumption_sea_mtpd
    port_fuel_mt = (total_port_working_days + port_waiting_days) * consumption_port_mtpd
    total_bunkers_mt = sea_fuel_mt + port_fuel_mt
    total_bunkers_cost_usd = total_bunkers_mt * fuel_price_usd_per_mt
    
    # 3. Revenue & Commissions
    gross_freight_usd = freight_rate_usd_per_mt * cargo_intake_mt
    total_commission_pct = (address_commission_pct + brokerage_commission_pct) / 100.0
    commissions_usd = gross_freight_usd * total_commission_pct
    net_revenue_usd = gross_freight_usd - commissions_usd
    
    # 4. Laytime & Demurrage / Despatch
    # Agreed working laytime allowed (SHINC)
    laytime_allowed_days = (cargo_intake_mt / load_rate_mtpd) + (cargo_intake_mt / discharge_rate_mtpd)
    actual_time_used_days = total_port_working_days + port_waiting_days
    
    if actual_time_used_days > laytime_allowed_days:
        demurrage_days = actual_time_used_days - laytime_allowed_days
        demurrage_usd = demurrage_days * demurrage_rate_usd_per_day
        despatch_usd = 0.0
        net_demurrage_balance = demurrage_usd
    else:
        despatch_days = laytime_allowed_days - actual_time_used_days
        despatch_usd = despatch_days * (demurrage_rate_usd_per_day * despatch_ratio)
        demurrage_usd = 0.0
        net_demurrage_balance = -despatch_usd
        
    # 5. Total Voyage Cost to Owner
    total_voyage_costs_usd = (
        total_bunkers_cost_usd +
        port_disbursements_usd +
        canal_tolls_usd +
        cargo_dues_usd
    )
    
    # 6. Time Charter Equivalent (TCE)
    # Net earnings divided by duration
    net_voyage_pnl = net_revenue_usd - total_voyage_costs_usd + net_demurrage_balance
    tce_usd_per_day = net_voyage_pnl / total_voyage_days if total_voyage_days > 0 else 0.0
    cost_per_mt = (total_voyage_costs_usd + commissions_usd - net_demurrage_balance) / cargo_intake_mt if cargo_intake_mt > 0 else 0.0

    return {
        "freight_rate_usd_per_mt": freight_rate_usd_per_mt,
        "cargo_intake_mt": round(cargo_intake_mt, 1),
        "gross_freight_usd": round(gross_freight_usd, 2),
        "commissions_usd": round(commissions_usd, 2),
        "net_revenue_usd": round(net_revenue_usd, 2),
        "total_voyage_days": round(total_voyage_days, 2),
        "sea_days": round(total_sea_days, 2),
        "port_days": round(total_port_working_days + port_waiting_days, 2),
        "total_bunkers_mt": round(total_bunkers_mt, 1),
        "bunkers_cost_usd": round(total_bunkers_cost_usd, 2),
        "total_voyage_costs_usd": round(total_voyage_costs_usd, 2),
        "demurrage_usd": round(demurrage_usd, 2),
        "despatch_usd": round(despatch_usd, 2),
        "net_demurrage_usd": round(net_demurrage_balance, 2),
        "tce_usd_per_day": round(tce_usd_per_day, 2),
        "total_landed_cost_per_mt": round(freight_rate_usd_per_mt + (net_demurrage_balance / cargo_intake_mt), 2)
    }
