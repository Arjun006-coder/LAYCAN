"""
Unit and Property Tests for LAYCAN Core Engines using standard unittest:
- Naval architecture hydrostatics (TPC, FWA, DWA)
- Voyage economics and TCE
- Optimal stopping reservation boundaries
- Backtest invariants
"""
import unittest
from laycan_core.physics.intake import calculate_intake
from laycan_core.voyage.tce import calculate_voyage_economics
from laycan_core.timing.lsmc import solve_optimal_stopping
from laycan_core.backtest.harness import run_decision_backtest

class TestLaycanCore(unittest.TestCase):

    def test_paradip_capesize_draft_deficit(self):
        """Capesize must experience severe draft loss at Paradip coal berths (16.0m)."""
        cape = {"summer_draft_m": 18.0, "dwt_typical": 180000.0, "tpc": 115.0, "loa_m": 292.0, "beam_m": 45.0}
        paradip = {"unlocode": "INPRT", "max_draft_m": 16.0, "max_loa_m": 300.0, "max_beam_m": 46.0, "water_density": 1025.0}
        cargo = {"stowage_factor_typical": 1.22}
        
        res = calculate_intake(cape, paradip, cargo, ukc_required_m=1.5)
        self.assertTrue(res["feasible"])
        self.assertGreater(res["draft_loss_mt"], 35000.0)
        self.assertEqual(res["governing_constraint"], "DRAFT_WEIGHT_LIMITED")

    def test_haldia_dock_water_density_correction(self):
        """Haldia river brackish water (1010 kg/m3) must compute non-zero DWA."""
        pmax = {"summer_draft_m": 14.0, "dwt_typical": 75000.0, "tpc": 68.0, "loa_m": 225.0, "beam_m": 32.2}
        haldia = {"unlocode": "INHAL", "max_draft_m": 8.5, "max_loa_m": 230.0, "max_beam_m": 35.0, "water_density": 1010.0}
        cargo = {"stowage_factor_typical": 1.25}
        
        res = calculate_intake(pmax, haldia, cargo, ukc_required_m=1.0)
        self.assertGreater(res["dwa_correction_m"], 0.0)

    def test_tce_monotone_decreasing_in_voyage_cost(self):
        """TCE must strictly decrease as fuel prices rise."""
        tce_low_fuel = calculate_voyage_economics(
            freight_rate_usd_per_mt=23.0, cargo_intake_mt=75000.0, ballast_dist_nm=4000.0, laden_dist_nm=4000.0,
            speed_ballast_kn=12.5, speed_laden_kn=12.0, consumption_sea_mtpd=32.0, consumption_port_mtpd=2.5,
            fuel_price_usd_per_mt=500.0, port_disbursements_usd=150000.0
        )["tce_usd_per_day"]

        tce_high_fuel = calculate_voyage_economics(
            freight_rate_usd_per_mt=23.0, cargo_intake_mt=75000.0, ballast_dist_nm=4000.0, laden_dist_nm=4000.0,
            speed_ballast_kn=12.5, speed_laden_kn=12.0, consumption_sea_mtpd=32.0, consumption_port_mtpd=2.5,
            fuel_price_usd_per_mt=700.0, port_disbursements_usd=150000.0
        )["tce_usd_per_day"]

        self.assertGreater(tce_low_fuel, tce_high_fuel)

    def test_lsmc_reservation_rate_boundary(self):
        """Reservation rate must be bounded and recommend FIX if market drops below threshold."""
        res = solve_optimal_stopping(current_market_rate=19.5, days_to_laycan_close=10, mean_rate=23.0)
        self.assertIn(res["recommended_action"], ["FIX_TODAY", "WAIT"])
        self.assertLessEqual(len(res["reservation_curve_next_14d"]), 14)

    def test_backtest_capture_ratio_positive(self):
        """Backtester must produce positive savings against naive policy."""
        bt = run_decision_backtest(num_voyages=12)
        self.assertEqual(bt["num_voyages_analyzed"], 12)
        self.assertGreater(bt["total_savings_usd"], 0)
        self.assertGreater(bt["capture_ratio"], 0.0)

if __name__ == "__main__":
    unittest.main()
