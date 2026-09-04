"""
Comprehensive AI Context, Domain Rules, and Agent Guidelines for LAYCAN.
Every AI agent, subagent, or developer working on this codebase MUST read and follow these rules.
"""

# ==============================================================================
# 1. CORE MISSION & PROBLEM STATEMENT
# ==============================================================================
# - Project: LAYCAN (Autonomous Bulk Freight Decision Intelligence & Vessel Chartering Desk)
# - Problem Statement: SIH 2026 #26006 | Ministry of Steel / SAIL
# - Primary Commodity: Coking Coal (~57 MT/yr imported into India; SAIL imports ~16 MT)
# - Key Origins: Australia (Hay Point, DBCT, Newcastle), Indonesia, Mozambique, S. Africa
# - Discharge Ports: East Coast India (Paradip, Vizag Outer, Vizag Inner, Gangavaram, Dhamra, Haldia)
# - Core Objective: Optimize the chartering decision: WHEN to buy, WHICH vessel class, WHICH port,
#   and HOW to hedge against freight rate spikes.

# ==============================================================================
# 2. THE TWO INVIOLABLE ARCHITECTURAL RULES
# ==============================================================================
# RULE 1: LLMs NEVER EMIT NUMERALS DIRECTLY.
#   - LLMs (e.g. Gemini) are used strictly for qualitative reasoning, scenario synthesis,
#     adversarial critique, and executive communication.
#   - Every dollar amount ($/mt), percentage, deadweight tonnage (DWT), draft (m), duration (days),
#     and demurrage value MUST be computed by deterministic, versioned Python solvers in `laycan_core/`.
#   - CI and test suites verify that agents consume typed solver outputs rather than generating math.
#
# RULE 2: THE CRITIC MUST AUDIT EVERY RECOMMENDATION.
#   - No chartering memo or trade recommendation is shown to the user without passing through
#     the Adversarial Critic Agent (`agents/supervisor.py`).
#   - The Critic actively checks:
#       1. Physical feasibility (draft, LOA, beam, lightering necessity).
#       2. Environmental risks (cyclones, swell height > 2.5m via Open-Meteo).
#       3. Forward momentum alignment (BDRY proxy direction vs optimal stopping decision).
#       4. Model calibration drift and single-source dependency.
#   - If confidence is degraded, the Critic forces "HUMAN_ESCALATION" instead of pretending certainty.

# ==============================================================================
# 3. CRITICAL MARITIME & PORT PHYSICS GROUND TRUTHS
# ==============================================================================
# Visakhapatnam (Vizag) is TWO DISTINCT PORTS:
#   - Outer Harbour (INVTZ-OH): 18.1m draft, 390m LOA. Capesize/Super-Cape capable.
#   - Inner Harbour (INVTZ-IH): 14.5m draft, 260m LOA. Panamax maximum. LOA > 195m requires 2 pilots.
#   - NEVER treat Vizag as a single draft port.
#
# Paradip (INPRT) Coal Berth Restrictions:
#   - Channel depth is 17.1m - 18.7m, BUT dedicated coal berths #2 and #3 cap at 16.0m draft.
#   - A fully laden Capesize (18.0m draft) CANNOT discharge at Paradip coal berths without lightering.
#
# Haldia (INHAL) & Sandheads (INSAG) Lightering:
#   - Haldia is riverine (Hooghly river) with max permissible draft of ~8.5m and brackish density (1010 kg/m3).
#   - Any Capesize/Panamax destined for Haldia MUST lighter into barges at Sandheads anchorage.
#   - Lightering formula: Cost = (Tonnes Lightered * Barge Rate) + (Delay Days * [Hire + Port Bunkers]).
#
# Gangavaram (INGAW):
#   - 17.7m standard draft (18.3m dynamic). Capesize capable.
#   - NOTE: Not present in IMF PortWatch ArcGIS layer. Congestion is proxied via Vizag Outer Anchorage.
#
# Newcastle (AUNEW - Australia Load Port):
#   - Channel depth ~15.2m; sailing draft ~16.1m under SAUCS dynamic UKC.
#   - Newcastle CANNOT sail a fully laden 180,000 DWT Capesize drawing 18.0m. Must account for partial loading.

# ==============================================================================
# 4. QUANTITATIVE & FINANCIAL MARKET RULES
# ==============================================================================
# BDRY (Breakwave Dry Bulk Shipping ETF) Handling:
#   - BDRY holds rolling near-dated FFA contracts (Capesize 5TC, Panamax 4TC, Supramax 10TC).
#   - It suffers from structural roll decay (contango drag) and management fee attrition.
#   - NEVER use the nominal dollar price of BDRY as an absolute freight rate index.
#   - USE BDRY DAILY LOG-RETURNS (ln(P_t / P_{t-1})) as an exogenous momentum & volatility factor.
#   - Anchor baseline rate levels to SEC EDGAR quarterly disclosures (SBLK, GNK, GOGL) and CIF-FOB parity.
#
# Optimal Stopping Math (Least-Squares Monte Carlo / LSMC):
#   - Problem: American option structure on commodity procurement.
#   - Reservation Rate R*(t) is the expected continuation value of waiting.
#   - Invariant: R*(t) rises monotonically as deadline t -> T (charterer becomes less picky).
#   - Action: FIX if Market Rate <= R*(t), else WAIT.
#
# Evaluation Metric:
#   - Primary metric is CAPTURE RATIO: (Cost_Naive - Cost_LAYCAN) / (Cost_Naive - Cost_Oracle).
#   - Never report mean savings without reporting the WORST QUARTER performance.

# ==============================================================================
# 5. DATA INGESTION ARCHITECTURE (100% FREE & AUTOMATED)
# ==============================================================================
# 1. IMF PortWatch REST: `https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Ports_Data/FeatureServer/0/query`
#    - Free ArcGIS REST API. Tracks daily portcalls, portcalls_dry_bulk, import/export tonnage.
#    - IDs: Paradip (port883), Vizag (port1367), Dhamra (port290), Gopalpur (port2299), Krishnapatnam (port599), Haldia (port442).
# 2. Open-Meteo Marine: `https://marine-api.open-meteo.com/v1/marine`
#    - Free public REST API. Wave height, swell wave height, wind waves for Bay of Bengal coordinates.
# 3. yfinance: BDRY, SBLK, GNK, GOGL historical and intraday closes.
# 4. Graceful Degradation: All ingestion clients implement robust fallback caches to guarantee zero crashes during live demos.
