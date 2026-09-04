# LAYCAN — Master Plan

**A freight decision engine for bulk cargo importers.**
SIH 2026 · Problem Statement 26006 · Ministry of Steel / SAIL · Theme: Transportation & Logistics

---

## 0. How to read this document

This is the single source of truth for what we are building, why, how, and in what order. It is written for six people who need to start committing code on day one.

Three reading paths:

- **Building it?** Read §2 (what we solve), §5 (architecture), §6–§7 (the engine), §13 (stack and repo), §14 (your sprint).
- **Pitching it?** Read §1 (the reframe), §3 (why we win), §12 (the numbers we will quote), §15 (the demo script).
- **Selling it?** Read §1, §3, §17, and the separate investor one-pager.

### An honesty note you must not skip

This plan was written without live internet access. Every factual claim in it comes from model knowledge, not from a verified page. That matters enormously for one category in particular: **port drafts, LOA limits, handling rates, sailing distances, market sizes and competitor pricing are all APPROXIMATE and UNVERIFIED.**

Do not put a single one of those numbers in the deck, the UI, or a customer conversation until someone has checked it against a primary source. `docs/VERIFY-FIRST.md` is the prioritised checklist. It is roughly two days of work for one person and it is the highest-value two days on the whole project, because a judge who catches one wrong port draft will discount everything else you say.

The *design* in this document does not depend on those numbers. The architecture, the maths, the sprint plan and the business logic stand on their own. Verify the facts, keep the design.

---

## 1. The reframe: we are not building a forecasting model

The problem statement asks for "an Intelligent Freight Forecasting Model." Read literally, that produces a project that loses.

Here is why. Ocean freight rates are close to a random walk at the horizons that matter. Thirty years of maritime economics literature says roughly the same thing: dry bulk rates are volatile, mean-reverting over long horizons, subject to jumps, and genuinely hard to beat a naive random-walk forecast on at 30–90 days. Worse, where a liquid forward market exists — and it does, in Forward Freight Agreements on the Capesize, Panamax, Supramax and Handysize timecharter baskets — the forward curve already aggregates the informed opinion of every trading desk on earth. A six-person student team is not going to out-forecast the FFA curve, and any team claiming an R² that implies they have should be disbelieved.

So a hundred teams will build an LSTM, show a chart where the orange line hugs the blue line, quote a 4% MAPE that is really just the persistence of a slow-moving series, and lose.

**The actual problem is not prediction. It is decision-making under irreducible uncertainty.**

Reread the problem statement with that lens and it says something much more interesting. SAIL's pain is not "we don't know next month's rate." It is:

> We buy freight reactively, one spot voyage at a time, on whatever day the plant tells us it needs coal. We have no policy. We have no way to know whether today's offer is good or bad relative to what our own options are. We can't tell which vessel class is actually cheapest per landed tonne once port limits, lightering and demurrage are priced in. And we carry 100% of the freight price risk with no hedge, because we have no chartering desk and have never touched a derivative.

That is a *decision* problem, an *optimisation* problem and a *risk management* problem wearing a forecasting costume.

### What we build instead

> **LAYCAN turns freight from a daily purchase into a managed position.**

Every day, for every cargo it must move, LAYCAN answers four coupled questions and shows its work:

| Question | What a forecasting model gives you | What LAYCAN gives you |
|---|---|---|
| **Fix today, or wait?** | "Rates may fall ~5%" | "Fix if the market prints at or below **$21.40/t** today. It's at $23.10. Wait. Your reservation rate rises to $22.60 by the 14th as your laycan closes." |
| **Which vessel class?** | "Capesize is cheaper per tonne" | "Kamsarmax. Capesize is $1.80/t cheaper on paper but Paradip's draft caps intake, forcing part-cargo lightering at Sandheads that costs $2.90/t and adds 4.1 waiting days." |
| **Which instrument?** | *silent* | "Cover 60% of Q3 volume on a 4-voyage COA, leave 40% spot. Full COA cover looks $0.70/t cheaper but your Q3 tonnage forecast has a ±18% error band and short-lifting a COA is expensive." |
| **How much risk are we carrying?** | *silent* | "Unhedged Q3 freight exposure is $14.2M with a 95% CVaR of $2.1M. Selling 45 Panamax 5TC FFA lots cuts tail risk 38% for $0 premium. Residual basis risk vs your actual route: ±$1.10/t." |

The right-hand column is a product a company pays for. The left-hand column is a homework assignment.

### The one-sentence version

**LAYCAN is the freight procurement desk that a mid-sized bulk importer can't afford to hire: it sets a price discipline, enforces port-physics reality, chooses the right contract instrument, and hedges the residual risk — and it backtests every one of those decisions against what you would otherwise have paid.**

---

## 2. Problem decomposition: exactly what we solve

The problem statement is enormous. Trying to build all of it is the most common way good teams fail. Below is the definitive scope. **P** items are in scope for SIH. **X** items are explicitly out of scope and we will say so on a slide, because naming what you deliberately excluded is a credibility signal, not a weakness.

### In scope

**P0 — Canonical domain model.**
A rigorous, machine-readable representation of the physical world: ports (with draft, LOA, beam, DWT, berth count, handling rate, tidal windows, gear availability, lightering practice), vessel classes and representative particulars, cargo types with stowage factors, routes with graph-derived distances, and the calendar of monsoon, cyclone and seasonal effects. Everything else depends on this being right. Owner: the domain person, week 1, non-negotiable.

**P1 — Rate state estimation.** Where is the market *right now*, per vessel class and per route, with an honest uncertainty band. Includes the basis problem (§6.2): there is no published index for Newcastle→Paradip, so we model it as a hedgeable index plus a basis spread we estimate and report separately.

**P2 — Calibrated probabilistic forecasting.** Not a point forecast. A distribution, with intervals whose coverage has been *validated* (conformal prediction), benchmarked honestly against a random walk and against the forward curve. We will report where we beat the benchmark and where we do not.

**P3 — Optimal market entry timing.** The reservation-rate policy: solve the optimal stopping problem over the laycan window and emit a daily fix-or-wait threshold. This is PS requirement (a), answered with actual decision theory instead of an arrow.

**P4 — Draft-constrained cargo intake.** Given a port's permissible draft, a vessel's particulars, a cargo's stowage factor, water density and load line zone, compute the maximum liftable tonnes. Real naval-architecture arithmetic (TPC, FWA/DWA). This is the single most credibility-dense feature in the product and almost no competing team will attempt it.

**P5 — Vessel class and port pairing optimisation.** A mixed-integer program that assigns cargoes to vessel classes and discharge ports subject to hard feasibility, minimising expected total landed cost with a tail-risk penalty. Answers PS requirement (b) properly — as an optimisation, not a lookup table.

**P6 — Full voyage economics.** Freight ↔ TCE conversion, ballast and laden legs, bunkers at sea and in port, port disbursements, cargo dues, canal fees, commissions, laytime, demurrage and despatch, lightering cost. If the voyage calculator is wrong, everything above it is decoration.

**P7 — Congestion and waiting-time nowcast.** Expected pre-berthing detention per port, from official Indian port statistics plus daily port-call data, feeding directly into P5 and P6 as expected demurrage days. Answers PS requirement (c) in its most valuable form.

**P8 — Idle and repositioning strategy.** Given a predicted waiting profile, compare: wait at anchorage, slow-steam to arrive later (with the cube-law bunker saving), divert to an alternate discharge port, or lighter. Choose on expected cost. This is PS requirement (c).

**P9 — Instrument portfolio selection.** Spot vs trip timecharter vs COA vs FFA, chosen as a portfolio on an expected-cost / CVaR efficient frontier, given a volume forecast with an explicit error band. This is the piece the problem statement's *Objective* line actually asks for — moving from many single spot fixtures to term multi-voyage cover — and it is the piece every other team will skip.

**P10 — Freight hedge sizing.** Minimum-variance hedge ratio against the nearest liquid FFA contract, with basis risk quantified and margin implications stated. Nobody sells this to Indian physical importers. It is our commercial wedge.

**P11 — Risk and disruption early warning.** Cyclone tracks in the Bay of Bengal, port labour and infrastructure events from a global news-event feed, chokepoint status, coal stock draw at destination. Converted into a *quantified* adjustment — a jump-intensity bump in the rate model or an added waiting-day distribution — not just a red banner. This is PS requirement (d).

**P12 — Decision memo and audit trail.** A one-page, human-readable recommendation with every number traceable to its source, its licence, its timestamp, and its status as observed, derived or simulated. Procurement is an auditable function; a black box cannot be used even if it is right.

**P13 — Decision backtest.** Replay history. What would our policy have paid per tonne versus what a naive "fix on the day the plant asked" buyer paid? This is the killer slide and §12 explains why it beats any forecast-accuracy metric.

### Explicitly out of scope

**X1 — Real-time global satellite AIS.** Open-ocean tracking in the Bay of Bengal requires commercial satellite AIS. We use free coastal AIS and free daily port-call data and we say so. We do not pretend to track every vessel on earth.
**X2 — Licensed Baltic route assessments.** Paywalled, aggressively enforced, and we will not scrape them. §8 explains our legal substitutes.
**X3 — Executing trades.** No broker integration, no FFA execution, no clearing. We advise; a human and a broker execute. Post-SIH partnership, not an MVP feature.
**X4 — Charter party drafting, laytime dispute resolution, document workflow.** Adjacent, valuable, a different product. Marcura and Veson live here.
**X5 — Bunker procurement optimisation.** We price bunkers; we do not buy them.
**X6 — Container, tanker, gas, breakbulk, project cargo.** Dry bulk only. Focus is the point.
**X7 — Anything requiring SAIL's confidential internal data.** We design the ERP integration surface (§10) and demo with synthetic cargo programmes.

### The scope discipline rule

If a feature does not change what appears in the decision memo, it does not get built before SIH. Write that on a wall.

---

## 3. Why this wins: eight things nobody else will have

Ranked by how much they will move a judge.

**3.1 A backtest of decisions, not of forecasts.**
Everyone shows forecast error. We show money. Replay five years: the naive buyer fixed on day-of-need and paid an average of *N* $/t; our reservation-rate policy paid *N − Δ*; a perfect-hindsight oracle paid *N − Δ\**. We captured Δ/Δ\* of the theoretically available saving. That single table is unarguable, is what a CFO buys, and converts a student project into a business case. Build the backtest harness in week 2, before the UI. If it works, everything else is presentation.

**3.2 Optimal stopping instead of an opinion.**
The fix-or-wait decision is a finite-horizon optimal stopping problem — structurally the same as exercising an American option. We solve it with Least-Squares Monte Carlo and emit a *reservation rate curve*: a hard threshold per day that tightens as the laycan closes, exactly as a real charterer's resolve weakens as they run out of runway. It is elegant, it is correct, and any judge with an operations research, quantitative finance or actuarial background will recognise it immediately and take the rest of your project seriously.

**3.3 Calibrated uncertainty.**
"84% confidence" with no stated method is theatre and a sharp judge will ask how it was computed. We use conformal prediction and quantile regression, and we *prove* coverage on held-out data: "our nominal 80% interval contained the realised rate 79.4% of the time across 1,240 out-of-sample days." Then we go further and say plainly where our model fails to beat a random walk. Admitting a limitation you have measured is the strongest possible signal that the numbers you *do* claim are real.

**3.4 Port physics as a hard constraint.**
Draft-limited intake via TPC and fresh-water allowance, load line zones, tidal windows, geared versus gearless vessels, and the Haldia/Sandheads lightering economics. This is the layer that makes a shipping person lean forward, because it is the part outsiders always get wrong. A Capesize is cheaper per tonne right up until the moment it physically cannot berth, and then it is catastrophically more expensive. Modelling that is the difference between a dashboard and a tool.

**3.5 The instrument layer, and the hedge.**
Recommending *when* to buy is table stakes for a good project. Recommending *what to buy* — spot, TCT, COA, or a partial FFA overlay — chosen on a cost/tail-risk frontier, is a different category of product. Indian industrial importers are structurally unhedged on freight while their counterparties on the other side of every trade hedge routinely. Being the software that closes that gap for the physical buyer is a genuine, defensible, unoccupied commercial position, and it is exactly what the PS's stated objective is reaching toward.

**3.6 A real graph, doing real work.**
Sea routing over an actual marine network graph with Dijkstra/A*, where edge weights are distance plus significant wave height plus cyclone proximity plus canal cost plus emissions-zone fuel penalty plus a draft-feasibility mask from bathymetry. Then validate the output against industry-accepted distance tables and show the error. That is "graph AI" that is technically real rather than a buzzword, and it produces a beautiful map.

**3.7 An LLM that is forbidden from producing numbers.**
Hard architectural rule, stated on a slide: **every numeral in the product comes from a deterministic, unit-tested, versioned solver. The language models orchestrate, retrieve, interpret and explain. They never compute and never invent a figure.** Numbers are injected into memo templates from typed tool outputs. This is the single line that separates us from the AI-slop projects, it is the reason a procurement head could actually sign off on our output, and it will be the most quoted sentence in our pitch.

**3.8 A Critic agent whose job is to attack the recommendation.**
Before any memo ships, a red-team agent tries to break it: is the market in a regime the model has not seen? Are we extrapolating beyond training support? Is the forward curve disagreeing with us and if so why do we think we're right? Is a single data source driving the whole answer? Has calibration drifted this month? When it objects, the product says **"low confidence — here is why, escalate to a human broker."** A system that knows when to shut up is more trustworthy than one that is always sure, and no other team will build this.
---

## 4. Product definition

### 4.1 Who uses it

**Primary — the Chartering / Import Logistics Manager** at a steel, power or cement company. Moves 0.5–10 million tonnes a year. Talks to three or four brokers. Works in email and Excel. Judged on landed cost per tonne and on not stopping the plant. Has never traded a derivative and has no mandate to. **This is who we build for.** Every screen must answer "what do I do today."

**Secondary — the Head of Procurement / Supply Chain.** Wants the portfolio view: total exposure, how much is covered, what the cost trajectory looks like against budget, and a defensible paper trail for why each decision was made.

**Tertiary — the CFO / Treasury.** Cares about one thing: the variance of the freight bill. This is the person who eventually buys the hedging module, and the reason the risk numbers must be expressed in currency and CVaR rather than in $/t.

**Not our user (yet)** — shipowners, operators, brokers, trading desks. They charter constantly, they already pay for terminals, and they are where every incumbent competes. We deliberately go where they aren't.

### 4.2 The core artifact: the Decision Memo

Everything the system does converges on one object. If we build nothing else well, build this.

```
┌────────────────────────────────────────────────────────────────────┐
│ DECISION MEMO · CARGO REF SAIL-COK-2026-118          02 Sep 2026   │
│ 75,000 mt (±10% MOLOO) Coking Coal · Hay Point → Paradip           │
│ Laycan 05–15 Oct 2026 · 43 days to window open                     │
├────────────────────────────────────────────────────────────────────┤
│  RECOMMENDATION                                          WAIT      │
│                                                                    │
│  Reservation rate today ............ $21.40 /mt                    │
│  Market indication today ........... $23.10 /mt   (+7.9% above)    │
│  Threshold on 14 Sep ............... $22.60 /mt   (tightening)     │
│  Latest advisable fixing date ...... 21 Sep 2026                   │
│                                                                    │
│  Vessel class ...................... KAMSARMAX      [why not Cape] │
│  Instrument ........................ 4-voyage COA, 60% of Q4 vol   │
│  Hedge ............................. sell 45 lots P5TC Q4          │
│                                                                    │
│  Expected landed freight ........... $22.05 /mt   (P10 19.8 / P90 25.1) │
│  vs fix-today ...................... −$1.05 /mt   = −$78,750       │
│  Confidence ........................ MEDIUM-HIGH                   │
│  Critic flags ...................... 1 (cyclone watch, Bay of Bengal) │
├────────────────────────────────────────────────────────────────────┤
│  WHY                                                               │
│  Panamax tonnage open in the Pacific ballast radius rose 14% w/w   │
│  while Australian east-coast loadings eased; both push the front   │
│  of the curve down. Paradip pre-berthing detention has fallen to   │
│  1.8 days from a 3.1-day trailing mean. Your laycan is 43 days out │
│  so the option value of waiting still exceeds the risk of a spike. │
│                                                                    │
│  WHY NOT CAPESIZE                                                  │
│  Cape freight is $1.80/mt cheaper but Paradip's permissible draft  │
│  caps intake at ~XX,XXX mt against a 180,000 dwt vessel, forcing   │
│  a part discharge at Sandheads: +$2.90/mt lightering, +4.1 days.   │
│  Net Cape penalty $2.34/mt.                          [full working]│
├────────────────────────────────────────────────────────────────────┤
│  CRITIC · Cyclone watch active in the Bay of Bengal (IBTrACS       │
│  analogue season). Waiting-day distribution widened; if a system   │
│  forms within 400 nm of Paradip the wait-value collapses. Re-run   │
│  daily. Do not extend the wait past 21 Sep without a human call.   │
├────────────────────────────────────────────────────────────────────┤
│  Every figure is traceable · 14 sources · 3 simulated  [provenance]│
└────────────────────────────────────────────────────────────────────┘
```

Note the properties that make this a product rather than a dashboard: a single unambiguous action, a *number* that makes the action falsifiable, the counterfactual cost of ignoring it, a stated confidence with a named objection, an explicit rejected alternative with its arithmetic, a decision expiry date, and full provenance. A procurement head can forward this to their director. That is the test.

### 4.3 Screens

1. **Today** — every live cargo as a card with its action, sorted by urgency. The home screen. If a manager only ever opens one screen, this is it.
2. **Cargo detail** — the memo above, with every figure expandable into its working.
3. **Market** — rate state per class and route, forward curve, our distribution against it, the reservation-rate curve, and the calibration record. Honest and quantitative.
4. **Feasibility explorer** — pick a port, see which vessel classes fit and where intake is capped, with the draft arithmetic shown. The domain-credibility screen.
5. **Voyage map** — the graph-routed track, weather and cyclone overlay, congestion at both ends, ETA distribution.
6. **Portfolio & risk** — total exposure, covered vs open, CVaR, hedge position and mark-to-market, budget variance.
7. **What-if** — change tonnage, origin, port, laycan, instrument mix; everything re-solves. The demo weapon.
8. **Backtest** — the policy-versus-naive-buyer evidence, per route and per class. The slide that closes the sale.
9. **Provenance** — every source, licence, last refresh, and observed/derived/simulated status. The trust screen.

---

## 5. System architecture

### 5.1 The governing principle

Two layers with a hard, enforced boundary:

```
   ┌────────────────────────────────────────────────────────────┐
   │  REASONING LAYER  ·  LLM agents (LangGraph)                │
   │  Gathers · interprets · challenges · explains · narrates    │
   │  MAY NOT compute. MAY NOT emit a numeral.                  │
   └────────────────────────────┬───────────────────────────────┘
                    typed tool calls │ typed structured results
   ┌────────────────────────────┴───────────────────────────────┐
   │  DETERMINISTIC CORE  ·  pure Python, no LLM                │
   │  Voyage calculator · intake solver · rate model · LSMC      │
   │  MILP · routing graph · hedge maths · backtester            │
   │  Unit-tested · property-tested · versioned · reproducible   │
   └────────────────────────────────────────────────────────────┘
```

Enforced mechanically, not by convention: agent outputs are Pydantic models whose numeric fields can only be populated by reference to a tool-result ID. A CI test asserts that no free-form numeral appears in generated memo prose. Violations fail the build. Say this on a slide.

### 5.2 Full topology

```
 EXTERNAL SOURCES                INGESTION              STORAGE
 ─────────────────               ─────────              ───────
 IMF PortWatch (port calls)  ┐
 Indian Ports Assoc (TRT)    │
 CEA daily coal stocks       │   Prefect flows        ┌─────────────┐
 World Bank / IMF commodities│   + Pydantic          │ TimescaleDB │
 EIA energy prices           ├──►validation ────────►│ time series │
 Open-Meteo marine           │   + provenance        ├─────────────┤
 IBTrACS cyclones            │   stamping            │ Postgres    │
 GDELT events                │                       │ reference   │
 yfinance (BDRY, equities)   │                       ├─────────────┤
 SEC EDGAR (TCE by class)    │                       │ DuckDB      │
 NGA World Port Index        │                       │ backtest    │
 MARNET graph, UN/LOCODE     ┘                       └──────┬──────┘
                                                            │
 ┌──────────────────────────────────────────────────────────┴────────┐
 │ FEATURE STORE — point-in-time correct, no leakage                 │
 └──────────────────────────────────┬────────────────────────────────┘
                                    │
 ┌──────────────────────────────────┴────────────────────────────────┐
 │ DETERMINISTIC CORE                                                │
 │                                                                   │
 │  rates/      OU-jump simulator · calibration · conformal bands    │
 │  timing/     LSMC optimal stopping → reservation rate curve       │
 │  physics/    draft-limited intake · TPC/FWA · load lines          │
 │  voyage/     TCE · bunkers (cube law) · DA · laytime · demurrage  │
 │  routing/    MARNET networkx graph · A* · weather-weighted edges  │
 │  assign/     MILP: cargo × class × port × window (CP-SAT/HiGHS)   │
 │  risk/       CVaR · scenario trees · jump intensity from events   │
 │  hedge/      min-variance ratio · basis risk · margin             │
 │  backtest/   policy replay vs naive vs oracle                     │
 └──────────────────────────────────┬────────────────────────────────┘
                                    │  typed tools
 ┌──────────────────────────────────┴────────────────────────────────┐
 │ AGENT LAYER (LangGraph supervisor + 9 specialists)                │
 │  Market · Supply · Demand · PortFeasibility · VoyageEconomist ·   │
 │  Risk · InstrumentStrategist · HedgeDesk · CRITIC                 │
 └──────────────────────────────────┬────────────────────────────────┘
                                    │  FastAPI + SSE
 ┌──────────────────────────────────┴────────────────────────────────┐
 │ Next.js dashboard · decision memos · maps · what-if · provenance  │
 └───────────────────────────────────────────────────────────────────┘
```

### 5.3 Two execution modes

**Live mode** hits real sources on schedule. **Demo mode** runs entirely from a frozen, seeded snapshot committed to the repo — same code path, byte-identical output every time. Build demo mode in week one and demo *only* from it. Hackathon venue wifi has ended more good projects than bad code has.

---

## 6. The deterministic core

This section is the engineering specification for the quant work. Formulas are given so they can be implemented and tested directly.

### 6.1 Voyage economics

The unit of truth. Freight quoted in $/mt is not comparable across vessel classes or routes; **Time Charter Equivalent** is.

```
Net Revenue ($) = Gross Freight − Commissions
                = ( F · Q ) · ( 1 − c_addr − c_brok )
TCE ($/day)     = ( Net Revenue − V ) / D
```

where:
- `F` = freight rate in $/mt
- `Q` = bill of lading cargo intake in mt
- `c_addr` = address commission to charterer (typically 1.25% to 2.50%)
- `c_brok` = brokerage commission to broker (typically 1.25%)
- `V` = total voyage costs paid by owner (bunkers at sea/port, port disbursements, cargo dues, canal fees, war risk)
- `D` = total round-voyage duration in days (laden leg + ballast leg + port time + weather margin + waiting time)

```
V = B_sea + B_port + DA_load + DA_disch + cargo_dues + canal + war_risk + extras
D = d_ballast/(24·v_b) + d_laden/(24·v_l) + Q/R_load + Q/R_disch + t_wait + t_wx
```

Bunkers follow the admiralty cube law — the most important non-obvious relationship in the model, because it is what makes slow-steaming a real lever:

```
FC(v) = FC_ref · (v / v_ref)^3      mt/day, main engine
fuel_leg = FC(v) · distance / (24·v)   →  scales with v²
```

So a 10% speed reduction cuts main-engine fuel for a fixed distance by roughly 19%, at the cost of ~11% more days. Whether that trade is worth taking depends on the hire rate and on whether the extra days are absorbed by waiting time you were going to incur anyway — which is precisely the calculation in P8.

Laytime and demurrage (stipulating SHINC vs SHEX terms):

```
laytime_allowed (days) = Q / R_agreed     (WWD SHINC: Weather Working Days, Sundays/Holidays Included)
time_used = actual_working_time + unexcused_delays
if time_used > laytime_allowed:
    demurrage = (time_used − laytime_allowed) · rate_dem   ("once on demurrage, always on demurrage")
else:
    despatch  = (laytime_allowed − time_used) · rate_dem · 0.5   (customarily 50% of demurrage rate)
```

**Property-test this module with Hypothesis.** Invariants: TCE must be monotone decreasing in voyage cost, monotone increasing in freight, and invariant to unit round-trips; total days must equal the sum of its parts; a zero-distance voyage must not divide by zero. Voyage maths bugs are silent and they poison every downstream number.

### 6.2 Rate state and the basis problem

**There is no published index for Hay Point → Paradip.** Pretending otherwise is the most likely way to get caught. We handle it the way practitioners do — decompose:

```
R_route(t) = I_hedgeable(t) + b_route(t)
```

`I` is a liquid, hedgeable reference (a Capesize/Panamax/Supramax TC basket or a published voyage route). `b` is the basis spread: the persistent, slowly-varying, route-specific difference driven by distance, port efficiency, cargo type and local tonnage balance.

This decomposition is doing real work. It means we forecast the *liquid* thing (where data and a forward curve exist), estimate the *basis* separately with far less noise (it is much more stable than the level), and — critically — it makes the hedging module honest: you can hedge `I`, you cannot hedge `b`, and residual basis risk is exactly `σ_b`. **Reporting basis risk as a separate line item is a mark of seriousness.** Everyone else will imply a perfect hedge.

#### Critical Quant Correction: Handling BDRY Properly (Factor Returns, NOT Price Level)
> ⚠️ **DO NOT USE BDRY PRICE LEVEL AS A FREIGHT RATE.**
> BDRY is an ETF holding rolling near-dated FFA contracts (Capesize 5TC, Panamax 4TC, Supramax 10TC). Like USO or UNG, **BDRY suffers from structural roll decay (contango drag)** and expense ratio drag. Its price level over 1–3 years drifts downward and is **NOT** equal to physical spot freight rates.
> 
> **The Correct Formulation:**
> Use BDRY daily **log-returns** as an exogenous market momentum and volatility factor:
> $$r_{\text{BDRY}, t} = \ln(P_{\text{BDRY}, t} / P_{\text{BDRY}, t-1})$$
> Anchor the baseline price level $\theta_t$ to **SEC EDGAR quarterly realized TCE filings** from listed owners (Star Bulk, Genco, Golden Ocean) and commodity spread arbitrage ($\text{CIF} - \text{FOB}$), while using $r_{\text{BDRY}, t}$ to drive the high-frequency daily shocks.

Model log-rate as mean-reverting with jumps and seasonality:

```
d ln I_t = κ (θ_t − ln I_t) dt + σ dW_t + J dN_t
```

Calibrate each parameter to a free, citable anchor:

| Parameter | Meaning | Calibration anchor |
|---|---|---|
| `θ_t` | long-run level per class, with seasonality | Quarterly TCE-by-vessel-class disclosed in listed dry bulk owners' SEC filings; seasonal shape from official port traffic and the monsoon/cyclone calendar |
| `σ` | volatility | Daily log-return volatility of BDRY ($\sigma_{r_{\text{BDRY}}}$); volatility statistics published in the academic literature |
| `κ` | mean-reversion speed | Published half-life estimates for dry bulk indices (typically 20–45 days) |
| `λ, J` | jump intensity and size | Frequency of port disruption events in GDELT database and historical cyclone frequency in the Bay of Bengal |

Two things make this defensible rather than hand-waved. First, **citing a published statistic is legal even when the underlying series is not free** — we can calibrate to a mean-reversion half-life reported in a journal article without licensing the data behind it. Second, we **validate the simulator against free observables** and publish the result: correlation with the freight-linked ETP, reproduction of reported quarterly TCEs within a stated tolerance, and consistency with commodity CIF−FOB spread moves. A judge shown "our simulated Capesize series reproduces reported quarterly TCE within 7% and correlates ρ=0.8 with the freight ETP" treats it as real work. A judge shown an unexplained curve does not.

### 6.3 Probabilistic forecasting, honestly benchmarked

Ensemble of a random-walk benchmark, SARIMAX with exogenous features, a GARCH volatility model, gradient boosting on engineered features, and a small temporal neural model — but **the point is not the ensemble.** The point is calibration and honest benchmarking.

Feature families: rate momentum and term structure; fleet supply proxies (open tonnage in ballast radius, congestion as an effective-supply sink, scrapping and orderbook); demand proxies (destination coal stocks and days-of-cover, steel production, port call volumes at load ports); cost floor (bunker prices); seasonality (monsoon, cyclone season, Chinese New Year, Australian cyclone closures, South American grain season); event intensity from the news feed.

Calibration via **split conformal prediction**: fit on train, compute absolute residuals on a held-out calibration set, take the ⌈(n+1)(1−α)⌉-th smallest as the interval half-width. For heteroskedastic rates, use **conformalized quantile regression** so intervals widen in volatile regimes. Then report empirical coverage against nominal. Metrics: MAE, RMSE, MAPE, directional accuracy, pinball loss, CRPS, and interval coverage — each against *both* a random walk and the forward curve.

**Report the failures.** State the horizon beyond which you do not beat a random walk. This costs nothing and buys everything, because it tells the judge your other numbers were not chosen for flattery.

### 6.4 Optimal stopping: the reservation rate

The heart of the product. Cargo must be fixed by day `T`. Each day `t` the market shows `R_t`. Fix now and pay `R_t`, or wait and face uncertainty. Minimise expected cost:

```
V_t(state) = min{ R_t ,  E[ V_{t+1}(state') | F_t ] }
V_T        = R_T + penalty_late
```

The **reservation rate** is the continuation value:

```
R*_t = E[ V_{t+1} | F_t ]        →     FIX  iff  R_t ≤ R*_t
```

Solve by **Least-Squares Monte Carlo** (Longstaff–Schwartz): simulate `M` paths from §6.2, work backwards, and at each step regress the realised continuation cost on basis functions of the state (current rate, days remaining, forward-curve slope, congestion, volatility) to approximate `E[V_{t+1}|F_t]`. Fit on in-the-money paths only.

Two structural properties to verify in tests and then put on a slide, because they show the maths is behaving like a real charterer: `R*_t` **rises monotonically as `t → T`** (you become less choosy as you run out of time), and it **widens with volatility** (more uncertainty means more option value in waiting). Also add a **must-move constraint** so the policy cannot strand a plant, and a **liquidity constraint** so it cannot assume tonnage is always available at the threshold.

Extension worth building if time allows: partial fixing. Fix 40% now, keep 60% open — a dollar-cost-averaging policy that is usually what a sensible desk does and which a pure binary stopping rule cannot express.

### 6.5 Port physics: draft-limited cargo intake

The credibility centrepiece. Convert a port's draft restriction into a hard tonnage cap.

```
d_max      = d_permissible − UKC_required
ΔDWT       = TPC · 100 · (d_summer − d_max)         [TPC in mt/cm, drafts in m]
DWT_avail  = DWT_summer − ΔDWT
cargo_wt   = DWT_avail − (bunkers + fresh water + stores + constants + retained ballast)
cargo_vol  = min(grain_capacity, hold_capacity) / stowage_factor
INTAKE     = min(cargo_wt, cargo_vol)
```

with the density correction, because ports are not all seawater — Haldia in particular sits up a river:

```
FWA (mm) = Displacement / (4 · TPC)
DWA (mm) = FWA · (1025 − ρ_dock) / 25
```

and load line zone applied by season and latitude (summer / tropical / monsoon — the Bay of Bengal has a seasonal zone that genuinely matters for an October laycan).

Coal stowage factor is roughly 1.20–1.25 m³/mt for coking and 1.25–1.40 for thermal (**verify**), so coal is usually weight-limited, not volume-limited — but iron ore at ~0.40 m³/mt is emphatically weight-limited and fertiliser can be volume-limited, so keep both branches.

Then the **lightering economics**, which is where East Coast India gets interesting. A Capesize cannot enter several of the target ports. The practical answer is part discharge at a deepwater anchorage into smaller vessels or barges. That costs money and days:

```
cost_light = Q_light · rate_light + days_light · (hire + bunkers_port)
```

The whole point: a Capesize's lower $/mt can be entirely consumed by lightering plus waiting, and the optimiser must be able to discover that. When it does, on stage, that is the moment the audience understands the product.

### 6.6 Routing as a graph problem

Load the marine network graph into `networkx`. Weight each edge:

```
w(e) = length(e) · [ 1 + α·Hs(e,t) + β·cyclone_proximity(e,t) + γ·ECA(e) ]
       + canal_toll(e) + piracy_premium(e)
```

Mask edges where charted depth minus required under-keel clearance is less than the vessel's laden draft — a **vessel-class-specific navigable graph**, which is both correct and a nice thing to show. Run A* with a great-circle heuristic. Validate against industry-accepted distance tables for a dozen real routes and **publish the mean absolute error**; a few percent is credible and admitting it is stronger than claiming zero.

### 6.7 Assignment as a mixed-integer program

Cargo programme → vessel classes → discharge ports → laycan windows.

```
minimise   Σ_{c,v,p,w}  x[c,v,p,w] · E[landed_cost(c,v,p,w)]  +  λ · CVaR_0.95(total)
subject to Σ_{v,p,w} x[c,v,p,w] = 1                       every cargo moves
           x[c,v,p,w] = 0  where infeasible(v,p)          hard port physics
           Σ_c x[c,·,p,w] ≤ berth_capacity[p,w]           berth contention
           Σ_c x[c,v,·,w] ≤ tonnage_available[v,w]        fleet liquidity
           intake(v,p) ≥ parcel_min(c)   or   allow split
           arrival(c,v,p,w) ∈ [required_from, required_by]
```

Solve with CP-SAT or HiGHS. Expected landed cost comes from §6.1 evaluated over the §6.2 scenario set; CVaR enters linearly via the Rockafellar–Uryasev formulation so the whole thing stays a MILP.

**Feasibility is a hard constraint, never a penalty.** A recommendation that cannot physically berth is not a slightly worse answer, it is a wrong answer, and the difference matters to the people we are selling to.

### 6.8 Instrument portfolio and CVaR

Allocate volume across spot, trip timecharter, COA and FFA overlay. Let `a_i` be the fraction on instrument `i`:

```
minimise  Σ a_i · E[cost_i]  +  λ · CVaR_α( Σ a_i · cost_i )
s.t.      Σ a_i = 1,  a_i ≥ 0,  a_COA ≤ volume_confidence_floor
```

That last constraint is where domain judgement lives. A COA is only cheap if you can actually lift it; short-lifting is expensive. So COA coverage is capped by the *lower* confidence bound of the volume forecast, not the mean. Sweep `λ` to trace the efficient frontier and show it — "here is the cost of buying certainty" is a chart a CFO understands instantly.

### 6.9 Hedging and basis risk

Minimum-variance hedge ratio against the nearest liquid FFA:

```
h* = Cov(ΔS, ΔF) / Var(ΔF) = ρ · σ_S / σ_F
lots = h* · exposure_days_or_tonnes / contract_size
effectiveness = ρ²          (variance reduction achieved)
residual basis risk = σ(S − h*·F)
```

Estimate with OLS as the baseline and a dynamic conditional correlation GARCH model as the upgrade, since freight correlations are time-varying. Always report three things together: the ratio, the effectiveness, and **the residual basis risk in $/mt**. A hedge sold as perfect is a hedge that will eventually embarrass you.

Also surface the operational reality — initial and variation margin, mark-to-market volatility, and the fact that a hedge that works can still produce an uncomfortable quarterly P&L line. That candour is what makes a treasury team trust the tool.
---

## 7. The agent layer

### 7.1 Why agents at all

Multi-agent architecture is the most abused phrase in hackathons. The honest justification is specific and narrow: the numerical work belongs in solvers, but the work *around* the solvers is genuinely heterogeneous, judgement-laden and poorly suited to a fixed pipeline. Deciding which sources are relevant today, noticing that a news event should raise jump intensity, reconciling two sources that disagree, deciding a recommendation is not trustworthy, and writing a paragraph a human will actually read — those are language tasks over unstructured input.

So: **agents at the edges, solvers in the middle.** If you cannot explain what an agent does that a function call could not, delete the agent.

### 7.2 The roster

Orchestrated by a LangGraph supervisor with typed state.

| Agent | Owns | Calls | Emits |
|---|---|---|---|
| **Market Analyst** | rate state, curve, calibration | `rates.*` | state estimate + bands + regime label |
| **Fleet Supply** | tonnage tightness in ballast radius | port-call and AIS tools | supply index + tightness narrative |
| **Demand** | cargo pull at destination | coal stocks, steel output, port traffic | demand index + volume forecast band |
| **Port Feasibility** | hard physics | `physics.intake`, `ports.constraints` | feasible class set + intake caps + reasons |
| **Voyage Economist** | landed cost | `voyage.*`, `routing.*` | TCE and cost breakdown per option |
| **Risk & Disruption** | events → quantified adjustment | news events, cyclone tracks, chokepoints | jump-intensity delta + waiting-day distribution shift |
| **Instrument Strategist** | spot / TCT / COA / FFA mix | `risk.cvar`, `portfolio.optimise` | allocation + frontier |
| **Hedge Desk** | hedge sizing | `hedge.*` | ratio, lots, effectiveness, basis risk, margin |
| **CRITIC** | attacking the answer | all validators | objections + confidence downgrade + escalation flag |
| **Chief Chartering Officer** | synthesis | all of the above | the Decision Memo |

### 7.3 The Critic, in detail

This is the agent worth building carefully, because it is the differentiator and it is cheap.

Its checklist runs before any memo ships:

- **Out-of-distribution check.** Is today's state vector inside the convex hull of training support? If not, say so and widen bands.
- **Regime change.** Has volatility, mean level or correlation structure broken from the calibration window? Statistical tests, not vibes.
- **Curve disagreement.** Does the forward market disagree with our forecast direction? If yes, the burden of proof is on *us*, and the memo must state why we think the market is wrong. Usually we should defer.
- **Single-source dependency.** Would the recommendation flip if one source were removed? Run the ablation. If yes, flag fragility.
- **Calibration drift.** Rolling empirical coverage versus nominal. Drifting means the bands are lying.
- **Feasibility sanity.** Re-verify the chosen option against port constraints independently of the optimiser. Belt and braces on the constraint that must never be violated.
- **Magnitude plausibility.** Is the claimed saving within historical achievable range, or absurd? Absurd savings mean a bug, and it is better for us to find it than a judge.

Output is a confidence label and, when warranted, `ESCALATE_TO_HUMAN`. **A product that sometimes says "I don't know, call your broker" is more valuable than one that never does** — and it is a genuinely differentiated thing to demo. Show it firing.

### 7.4 The no-numbers rule, mechanically enforced

```python
class MemoSection(BaseModel):
    prose: str                        # LLM-written, numerals forbidden
    figures: list[FigureRef]          # each must resolve to a tool result id

    @field_validator("prose")
    def no_bare_numerals(cls, v):
        if re.search(r"(?<!\{)\b\d[\d,.]*\b(?!\})", v):
            raise ValueError("LLM prose may not contain literal numerals")
        return v
```

Prose carries `{fig:tce_kmx}` placeholders; the renderer substitutes values from typed tool results carrying provenance. Result: the narrative is generated, the numbers are computed, and a hallucinated figure is structurally impossible rather than merely unlikely. This is also how the provenance screen gets built for free.

### 7.5 Model choice

Use LiteLLM so the provider is a config value. Cheap, fast model for extraction and routing; a stronger model only for the Critic and the final synthesis. Cache aggressively; agent runs must be reproducible in demo mode, which means seeded prompts and cached completions committed to the repo.

---

## 8. Data layer

### 8.1 Source register

Verdicts below come from the research pass in `docs/research/data-sources-raw.md`. **Every one carries an unverified flag** — see `VERIFY-FIRST.md`. Confidence is the researcher's own tagging.

**Tier 1 — build on these immediately**

| Source | Gives us | Auth | Notes |
|---|---|---|---|
| IMF PortWatch | daily port calls + trade estimates, ~1,400 ports, 2019→now, possible dry-bulk split | none | **Verify Indian East Coast coverage first — architecture leans on this more than anything else. Private ports are the doubtful ones.** |
| Indian Ports Association statistics | monthly traffic, **average turnaround time, pre-berthing detention, output per ship-berth-day** | none | Official Indian congestion data with history. India-specific credibility. |
| CEA daily coal stock report | daily stock and days-of-cover at Indian power plants, domestic vs imported | none | A real leading demand indicator almost no competing team will think of. |
| World Bank commodity price data | monthly coal FOB benchmarks, iron ore, crude | none | Clean licence. |
| US EIA API | energy and fuel price series | free key | Public domain. |
| Open-Meteo marine + archive | wave/wind forecast and reanalysis history | none | No key, permissive licence. |
| IBTrACS | historical global cyclone tracks | none | Filter to North Indian Ocean. Public domain. |
| GDELT | global news event volume, tone, event codes, geocoded | none | Free, huge, explicitly reusable. Right answer for the risk agent. |
| NGA World Port Index | machine-readable port specs worldwide | none | Public domain baseline; override for our key ports. |
| Marine network graph + `searoute` | routable sea graph for our own A* | none | The honest basis for the routing story. |
| UN/LOCODE | port code join key | none | Unglamorous and essential. |
| Freight-linked exchange-traded product + dry bulk owner equities via `yfinance` | daily freight-correlated price series | none | Legal daily proxy. |
| SEC EDGAR company filings API | **quarterly TCE by vessel class**, 10–15 years | UA header | Official, citable, redistributable. Our ground truth. |

**Tier 2 — week two:** coastal AIS free tier; bulk historical AIS archives for training and vessel dimensions; EU MRV per-ship fuel consumption (excellent for real consumption curves); Copernicus Marine; exchange freight-derivative settlement pages (verify licence); FFA broker free daily newsletters (underrated — real forward curve levels, intended for circulation, free signup); Indian trade statistics for coal imports by origin; UN Comtrade; vessel particulars lookups; Indian port daily vessel-position PDFs; `data.gov.in`.

**Tier 3 — do not plan around:** licensed Baltic route assessments, and the major commercial shipping intelligence terminals. All hard paywalls. **One exception worth ten minutes: email the college library and ask whether the institution holds a shipping intelligence subscription. It is the only realistic free door to licensed-grade data and it costs one email.**

### 8.2 The two real gaps, and what we do about them

**Gap 1 — licensed daily route-level freight assessments.** Not obtainable. Not partially, not with effort. So: model the hedgeable reference from free proxies (§6.2), estimate route basis separately, calibrate to official quarterly TCE disclosures, validate against free observables, and **badge every simulated series in the UI.** Then put the licensing cost in the business plan as a real line item, because a funded company simply buys it. Turning the constraint into a roadmap item is the correct answer to "your data isn't real."

**Gap 2 — open-ocean satellite AIS in the Bay of Bengal.** Free AIS is coastal only. So use free daily port-call data for congestion, coastal AIS for approach and berth events, and be explicit that mid-ocean position tracking is a paid upgrade. Do not fake a vessel crossing the Indian Ocean and call it live.

### 8.3 Provenance as a first-class citizen

Every value carries lineage:

```python
class Provenance(BaseModel):
    source_id: str
    source_name: str
    licence: str
    retrieved_at: datetime
    valid_at: datetime
    status: Literal["observed", "derived", "simulated"]
    transform_chain: list[str]
    confidence: Literal["high", "medium", "low"]
```

Enforced at ingestion. The UI badges `simulated` values distinctly and every figure is clickable through to its chain. This is simultaneously good engineering, our honest answer to the data gap, an audit requirement for real procurement, and a slide. Four wins from one abstraction — build it in week one, not week four.

### 8.4 Point-in-time correctness

The backtest is our headline claim, so leakage would be fatal. Every table is bitemporal: `valid_at` (when the fact was true) and `retrieved_at` (when we learned it). Feature queries take an `as_of` and may only read rows with `retrieved_at ≤ as_of`. Monthly statistics published with a lag must be visible only after their real publication date. Write a test that fails if any feature query returns a row violating this. Do it in week two, before the backtest is built, because retrofitting it later means rerunning everything and not believing the results.

---

## 9. Data model

Postgres for reference and transactional, TimescaleDB hypertables for series, DuckDB for backtest scans.

```sql
-- reference
ports(port_id PK, unlocode, name, country, lat, lon, port_type,
      max_draft_m, max_loa_m, max_beam_m, max_dwt,
      dry_bulk_berths, handling_rate_mtpd, gear_required,
      tidal_window_hrs, lightering_available, water_density,
      load_line_zone, source_ref, confidence)

vessel_classes(class_id PK, name, dwt_min, dwt_max, dwt_typical,
      loa_m, beam_m, summer_draft_m, tpc, grain_capacity_m3,
      holds, geared, speed_ballast_kn, speed_laden_kn,
      consumption_ballast_mtpd, consumption_laden_mtpd,
      consumption_port_mtpd, constants_mt)

cargo_types(cargo_id PK, name, stowage_factor_m3_mt, imsbc_group, hazards)
routes(route_id PK, load_port, disch_port, distance_nm, via_canal,
       graph_version, validated_against, error_pct)

-- series (hypertables)
rate_observations(ts, series_id, vessel_class, route_id, value,
                  unit, provenance_id)
forward_curve(ts, contract, tenor, settlement, provenance_id)
bunker_prices(ts, port_id, grade, price_usd_mt, provenance_id)
commodity_prices(ts, commodity, basis, price, provenance_id)
port_calls(ts, port_id, calls_total, calls_dry_bulk, import_est,
           export_est, provenance_id)
port_performance(month, port_id, turnaround_days, preberthing_days,
                 output_per_shipberthday, provenance_id)
weather(ts, grid_cell, hs_m, wind_kn, provenance_id)
cyclone_tracks(ts, storm_id, lat, lon, wind_kn, pressure)
events(ts, event_id, geo, cameo_code, tone, volume, url, provenance_id)
coal_stocks(date, plant_id, stock_mt, days_cover, is_imported)

-- operational
cargo_programme(cargo_ref PK, org_id, cargo_id, qty_mt, tolerance_pct,
                load_port, disch_port_pref, laycan_from, laycan_to,
                required_by, status, created_at)
decisions(decision_id PK, cargo_ref, as_of, action, reservation_rate,
          market_rate, vessel_class, instrument, hedge_lots,
          expected_cost, p10, p90, confidence, critic_flags jsonb,
          memo_json jsonb, model_version, git_sha)
outcomes(cargo_ref PK, fixed_at, fixed_rate, actual_vessel, actual_port,
         actual_wait_days, demurrage_usd, actual_landed_cost)
provenance(provenance_id PK, source_id, licence, retrieved_at,
           valid_at, status, transform_chain, confidence)
```

`decisions` and `outcomes` together are the asset. Every recommendation is stored immutably with the model version and git SHA that produced it, and every realised outcome is joined back. That is what makes the backtest honest, what makes the product improve with use, and — long term — what makes the company valuable (§17).

---

## 10. API surface

FastAPI, versioned, OpenAPI-documented, typed end to end.

```
POST /v1/cargo                          register a cargo requirement
GET  /v1/cargo/{ref}/decision           the Decision Memo (cached)
POST /v1/cargo/{ref}/decision:refresh    re-run the agent graph (SSE stream)
GET  /v1/cargo/{ref}/reservation-curve   thresholds by day to laycan

POST /v1/whatif                         perturb inputs, re-solve, diff
GET  /v1/market/state                   rate state per class/route + bands
GET  /v1/market/curve                   forward curve snapshot
GET  /v1/market/calibration             coverage record — the honesty endpoint

POST /v1/feasibility                    {port, class, cargo} → intake + reasons
POST /v1/voyage/estimate                full TCE breakdown
POST /v1/routing/route                  A* path + geometry + weather overlay

POST /v1/portfolio/optimise             instrument allocation + frontier
POST /v1/hedge/size                     ratio, lots, effectiveness, basis risk

POST /v1/backtest/run                   policy vs naive vs oracle
GET  /v1/provenance/{id}                lineage chain
GET  /v1/health, /v1/freshness          per-source staleness
```

Two design notes. `:refresh` streams over SSE so the UI can show agents working — this is worth real demo points, because watching the Critic raise an objection in real time communicates the architecture better than any diagram. And `/market/calibration` exists deliberately as a public endpoint: a product that ships its own accuracy record is making a statement.

Machine-readable ERP integration is designed but not built: cargo programmes in, decisions out, over the same typed contracts. Say this when asked how it plugs into SAP.

---

## 11. Frontend specification

Next.js App Router, TypeScript, Tailwind, shadcn/ui, TanStack Query, Recharts for series, MapLibre GL with a free tile source plus deck.gl for the route layer.

**Design direction.** Reject the purple-gradient AI-dashboard look; it signals demo. Aim for the visual language of a trading terminal built by people with taste: dense, calm, information-first. Near-black or paper-white base, one restrained accent, a real typeface pairing (a grotesque for UI, a proper mono for figures), tabular numerals everywhere numbers align, generous whitespace around the single recommendation so it dominates. Colour carries meaning only — action state, simulated-data badges, critic severity — never decoration. A judge should feel they are looking at something a company paid for.

**The three screens that must be flawless:** *Today* (the action list), *Cargo detail* (the memo with expandable working), *Backtest* (the evidence). Build these three to a high finish before starting the others. A polished three-screen product beats a rough nine-screen one every single time in front of judges, and it is also the truth about what users need.

**Interaction details that carry weight:** every figure has a hover showing source, licence, timestamp and observed/derived/simulated status; the reservation-rate chart plots today's market against the threshold curve so the decision is visible at a glance; what-if updates diff against the base case with deltas rather than replacing numbers; the agent-run stream shows each specialist reporting in, with the Critic's objection appearing last.

---

## 12. Evaluation protocol

### 12.1 The primary metric — decision quality, in money

Define three policies over historical windows:

- **Naive** — fix on the day the plant asked. Our proxy for the status quo the PS describes.
- **LAYCAN** — the reservation-rate policy from §6.4, with the must-move constraint.
- **Oracle** — perfect hindsight, best available day in the window. Not achievable; it defines the ceiling.

Report per route and vessel class:

| Metric | Definition |
|---|---|
| Mean cost | $/mt paid under each policy |
| Saving vs naive | absolute and % |
| **Capture ratio** | (naive − laycan) / (naive − oracle) — share of the theoretically available saving we got |
| Regret | mean shortfall against oracle |
| Hit rate | fraction of "wait" calls that were correct ex post |
| Tail | 95th percentile cost, and CVaR reduction from the hedge overlay |
| Robustness | performance in the worst quarter, not just on average |

**Capture ratio is the number to lead with.** It is honest — it concedes the oracle is unreachable — and it is interpretable: "we capture about half of the timing value that was theoretically on the table" is a claim a CFO can act on and a judge cannot dismiss. Never present a saving without also presenting the worst quarter.

Protocol discipline: walk-forward only, no peeking, point-in-time features (§8.4), transaction realism (you cannot fix at the index — add a spread), liquidity realism (tonnage is not always available), and results reported net of all frictions. Also run the policy on a period the model was never tuned on and report that separately as the true out-of-sample result.

### 12.2 Secondary metrics

*Forecasting:* MAE, RMSE, MAPE, directional accuracy, pinball loss, CRPS, and conformal coverage versus nominal — each benchmarked against a random walk **and** the forward curve, with failures stated.

*Optimisation:* 100% port-constraint compliance (a hard gate, never a percentage we are proud of), intake utilisation versus theoretical maximum, MILP solve time at realistic problem size, and solution stability under small input perturbations.

*Routing:* mean absolute error versus industry distance tables across a dozen validation routes.

*System:* p95 API latency, agent-graph wall time, per-source data freshness, and reproducibility — same inputs and seed must give byte-identical output.

### 12.3 What we will refuse to claim

Written down in advance so nobody is tempted under pitch pressure: we will not claim to beat the forward curve at long horizons; we will not quote a savings figure without its worst-case counterpart; we will not present simulated series as observed; we will not report a confidence number whose calibration we have not measured. Judges at international level probe exactly these four points. Having pre-committed answers is worth more than any extra feature.

---

## 13. Stack and repository

### 13.1 Choices, with reasons

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11 | The quant, optimisation and agent ecosystems are all here |
| API | FastAPI + Pydantic v2 | Typed contracts are the mechanism that enforces §7.4 |
| Series store | Postgres 16 + TimescaleDB | One database, hypertables for series, no second system to operate |
| Analytics | DuckDB + Polars | Backtests scan fast, locally, with no server |
| Forecasting | statsmodels, `arch`, LightGBM, scikit-learn, MAPIE | Conformal support matters more than model exotica |
| Optimisation | OR-Tools CP-SAT, HiGHS via PuLP | Free, fast, no licence |
| Graph | networkx + `searoute` + marine network GeoJSON | Real graph, real algorithm |
| Agents | LangGraph + LiteLLM | Typed graph state; provider-agnostic |
| Orchestration | Prefect | Readable flows, retries, observable |
| Cache/queue | Redis | Also backs demo-mode replay |
| Frontend | Next.js + TS + Tailwind + shadcn/ui + Recharts + MapLibre + deck.gl | Fast to a high finish; no paid map token |
| Testing | pytest, Hypothesis, Schemathesis | Property tests on voyage maths; fuzz the API |
| Repro | Docker Compose, `uv`, MLflow, DVC | `docker compose up` must produce the demo |
| CI | GitHub Actions | Lint, type-check, test, no-numerals check, seed-reproducibility check |

Deliberately **not** used: Kafka, Kubernetes, a feature-store SaaS, a vector database (nothing here is a semantic search problem), microservices. Every one of those would cost days and buy nothing before SIH. Say so if asked — knowing what not to build is a senior signal.

### 13.2 Repository layout

```
laycan/
├─ README.md                      one-command demo, first
├─ docker-compose.yml
├─ docs/
│  ├─ MASTER-PLAN.md              this document
│  ├─ VERIFY-FIRST.md             ⚠ do this before anything ships
│  ├─ DOMAIN-PRIMER.md            shipping bible for the team
│  ├─ DEMO-SCRIPT.md
│  ├─ decisions/ADR-000x-*.md     architecture decision records
│  └─ research/
├─ data/
│  ├─ reference/                  ports.csv, vessel_classes.csv, cargo_types.csv
│  │                              — hand-curated, cited, reviewed
│  └─ snapshots/demo-2026-09-01/  frozen demo fixtures, committed
├─ packages/
│  ├─ core/laycan_core/
│  │  ├─ physics/    intake.py  loadlines.py  hydrostatics.py
│  │  ├─ voyage/     tce.py  bunkers.py  laytime.py  disbursements.py
│  │  ├─ rates/      simulate.py  calibrate.py  conformal.py  basis.py
│  │  ├─ timing/     lsmc.py  reservation.py
│  │  ├─ routing/    graph.py  astar.py  weights.py  validate.py
│  │  ├─ assign/     milp.py  feasibility.py
│  │  ├─ risk/       cvar.py  scenarios.py  jumps.py
│  │  ├─ hedge/      ratio.py  basis_risk.py  margin.py
│  │  ├─ backtest/   policies.py  harness.py  metrics.py
│  │  └─ provenance/
│  ├─ ingest/flows/               one Prefect flow per source
│  ├─ agents/                     graph.py, specialists/, critic.py, memo.py
│  └─ api/                        FastAPI routers, schemas, sse
├─ web/                           Next.js app
├─ tests/                         unit, property, integration, golden memos
└─ notebooks/                     exploration only, never imported
```

Two conventions worth enforcing from day one. **`core` never imports from `api`, `agents` or `ingest`** — it is pure, testable, and could be published as a library; this keeps the deterministic boundary real rather than aspirational. And **`data/reference/` rows require a `source_ref`**; a CI check fails the build on any row without one, which is how the port dataset stays honest under deadline pressure.
---

## 14. Build plan — 6 people, 5 weeks

### 14.1 Roles

| | Person | Owns | Must not be distracted by |
|---|---|---|---|
| **A** | Data & Platform | ingestion flows, schema, provenance, point-in-time correctness, demo snapshot, Docker | modelling |
| **B** | Quant | rate simulator, calibration, conformal bands, LSMC reservation policy, hedge maths | UI |
| **C** | Optimisation | intake solver, voyage calculator, routing graph, MILP, CVaR | data plumbing |
| **D** | Backend & Agents | FastAPI, LangGraph, tool contracts, the no-numerals enforcement, SSE | frontend styling |
| **E** | Frontend | the three critical screens to a high finish, then the rest | backend logic |
| **F** | Domain, Eval & Pitch | **the verification checklist**, reference datasets, backtest design and metrics, demo script, deck | writing production code |

F's role is the one teams get wrong. It is not "the person who makes slides." F owns factual correctness and the evidence base — the two things that decide whether the project is believed. Give it to someone rigorous.

### 14.2 Week 1 — foundations and the truth layer

The goal this week is that **nothing built later rests on an unverified number or a leaky feature.**

**Day 1.** Repo, Docker Compose (Postgres+Timescale, Redis, API, web), CI skeleton, ADR-0001 recording the deterministic-core boundary. Everyone gets `docker compose up` working before going home. F starts `VERIFY-FIRST.md` at the top of the list: does the port-call source actually cover our target ports, and does it break out dry bulk?

**Day 2.** A: provenance model and ingestion scaffold. B: pull the free freight-proxy series and the official quarterly TCE-by-class filings; first look at what calibration anchors actually exist. C: voyage calculator skeleton with the TCE formula and its property tests. D: FastAPI skeleton, health and freshness endpoints. E: design direction, component library, the *Today* screen shell with mock data. F: port constraint dataset — every row cited, every gap marked unknown rather than guessed.

**Day 3.** A: two ingestion flows landing real rows with provenance. B: OU-jump simulator with calibration hooks. C: draft-limited intake solver plus the hydrostatic corrections, with a worked example checked by hand. D: tool contract definitions — the typed interface between agents and core. E: *Today* screen against the real API. F: continue verification; start the domain primer for the team.

**Day 4.** A: **bitemporal `as_of` feature queries and the leakage test.** This is the most important single day of week one; the backtest is worthless without it. B: conformal interval implementation with a coverage report on synthetic data. C: marine graph loaded, A* running, first validation route. D: the no-numerals validator and its CI check. E: memo layout. F: reference data review — sit with C and confirm intake numbers are physically sensible.

**Day 5.** Integration: one cargo goes in, a crude landed-cost estimate comes out, end to end, through the API, on screen. It will be ugly. It must work. Then: freeze demo snapshot v0, write ADRs for the week's decisions, and hold a 30-minute review where F reports what verification has *disproved* so far.

**Week 1 exit criteria.** `docker compose up` gives a working stack; at least four real sources ingested with provenance; the leakage test passes; the voyage calculator passes property tests; the intake solver matches a hand-worked example; one cargo flows end to end; the port dataset has zero uncited rows.

### 14.3 Week 2 — the engine and the evidence

The week the project either becomes real or stays a demo.

B: calibrate the rate model to real anchors; publish the validation table (correlation with the freight proxy, reproduction of reported quarterly TCEs); implement LSMC and verify the two structural properties — threshold rising toward laycan, widening with volatility.
C: MILP assignment over the feasibility matrix; lightering economics; weather-weighted routing with distance validation and published error.
A: remaining Tier-1 sources; congestion nowcast; **the backtest data spine.**
D: agent graph skeleton with three specialists calling real tools; SSE streaming.
E: cargo detail screen with expandable working; provenance hovers.
F: **the backtest harness and the naive/oracle policies.** Design the metrics table before the results exist so nobody is tempted to pick metrics that flatter.

**Week 2 exit criterion, and the single most important gate on the project: a first honest backtest number exists.** Even if it is disappointing. If the policy is not beating naive buying, you need three weeks to understand why — not three days. Do not let this slip.

### 14.4 Week 3 — agents, integration, honesty

D: all nine specialists plus the Critic; memo synthesis under the no-numerals rule; escalation path.
B: hedge sizing with basis risk; instrument portfolio with the CVaR frontier.
C: idle/repositioning comparison (wait vs slow-steam vs divert vs lighter); what-if re-solve path.
A: live/demo mode switch; freshness monitoring; snapshot v1.
E: backtest screen, market screen with the calibration record, feasibility explorer.
F: full metric suite; **write down the four refusals from §12.3 and rehearse the answers**; first deck draft; begin pressure-testing the team with hostile questions.

**Exit criteria.** A complete memo generated by the agent graph with every number traced; the Critic demonstrably firing on a real case; the backtest table populated across routes and classes; what-if working.

### 14.5 Week 4 — finish, don't start

Feature freeze on Monday. Anything not working by then is roadmap, and saying "that's Phase 2" confidently is far better than demoing something broken.

E takes the three critical screens to a genuinely high finish. B and C harden edge cases and write the model cards. A guarantees demo-mode determinism — same seed, byte-identical output, ten runs in a row. D adds graceful degradation everywhere: if a source is stale the memo says so and still produces an answer. F finalises the deck, runs the demo five times looking for the moment it breaks, and drafts the one-pager.

**Exit criteria.** Demo mode reproducible ten times; every screen survives a hostile click-through; deck complete; every number in the deck traced to `VERIFY-FIRST.md` as verified.

### 14.6 Week 5 — rehearsal and margin

No new code except bug fixes. Rehearse the three-minute version until it is muscle memory, then the eight-minute version. Hold a red-team session where two team members do nothing but attack: "your data is fake," "you can't beat the forward curve," "this is just an LSTM," "Kpler already does this," "how does this survive if the model is wrong." Every one of those has an answer in this document; the team needs to deliver them without hesitation.

Reserve the final two days entirely as buffer. Something will break. Teams that plan to finish on the last day arrive broken.

### 14.7 Rules that protect the timeline

Trunk-based development, small PRs, no long-lived branches. Every merge keeps the demo working — if `main` is broken, that is the only priority. Daily fifteen-minute standup with one question each: what is blocking the demo? Feature freeze is real. And a standing rule: **anyone may cut any feature except the Decision Memo and the backtest.**

---

## 15. Demo script

### 15.1 The three-minute version

**0:00 — The reframe, said fast.** "Freight rates are close to a random walk, and a liquid forward market already prices them better than we can. So we didn't build a forecasting model. We built the thing a company actually needs: a policy for *when to buy*, *what to buy*, and *how much risk to carry* — and we backtested those decisions against what the buyer would otherwise have paid."

**0:25 — Today screen.** Four live cargoes, four actions. "Every morning, this is the whole job."

**0:45 — One memo.** Read the recommendation aloud, then the reservation rate. "Twenty-one forty is our threshold today. The market is at twenty-three ten. So: wait. And here's the number that makes this falsifiable — if it prints below twenty-one forty tomorrow, we fix tomorrow."

**1:15 — Why not Capesize.** Open the working. "Capesize is cheaper per tonne. It also can't berth here at full intake — so you lighter, and that costs more than you saved. This is the calculation that gets made wrong in the real world." *This is the credibility moment. Do not rush it.*

**1:45 — The Critic fires.** "Before any recommendation ships, an agent attacks it. Right now it's flagging cyclone season, so confidence is downgraded and there's a hard review date. When it can't get comfortable, the product tells you to call a human. That's deliberate."

**2:10 — The backtest.** "Five years replayed. The naive buyer — fix on the day the plant asks, which is the status quo in the problem statement — paid this. Our policy paid this. Perfect hindsight would have paid this. So we capture this share of the timing value that was actually available. And here's our worst quarter, because a savings number without a worst case isn't a number."

**2:40 — The honest slide.** "Licensed Baltic route data is paywalled, so our rate series is calibrated and simulated, and it's badged as simulated everywhere in the product. Here's the validation against free public data. With a licence, this is a config change."

**2:55 — Close.** "Freight stops being a daily purchase and becomes a managed position."

### 15.2 The eight-minute version

Same spine, with four additions: the what-if — change tonnage and destination live, watch the whole recommendation re-solve; the map — graph-routed track with weather and cyclone overlay, and the distance validation error; the hedge — CVaR reduction, hedge ratio, and residual basis risk stated honestly; and the provenance drill-down — click any number, see its source, licence, timestamp, and whether it is observed, derived or simulated.

### 15.3 Prepared answers

**"Isn't this just an LSTM?"** — No, and deliberately so. Forecasting is the least valuable layer; we treat rates as a stochastic process, not a curve to fit, and the product is the stopping policy, the constrained optimisation and the hedge. We do benchmark against a random walk and we report where we lose.

**"Your data isn't real."** — Rate assessments are licensed and we won't scrape them; everything else is real and cited. The rate process is calibrated to official quarterly TCE disclosures and validated against free market proxies — here is the table. It is badged as simulated in the UI. A funded company buys the licence; it is a line in the business plan, not an architectural problem.

**"Kpler and Signal Ocean already do this."** — They sell data terminals to people who charter every day: owners, operators, brokers, trading desks. We sell a decision to someone who charters occasionally, has no desk, and is completely unhedged on freight. Different buyer, different product, and the hedging piece isn't offered to this customer by anyone.

**"How do we know the AI didn't make the numbers up?"** — Structurally impossible. The language models cannot emit a numeral; a CI test fails the build if they do. Every figure comes from a unit-tested solver and carries provenance. Click any number on screen.

**"What if the model is wrong?"** — Then the Critic should catch it, and when it can't, the product says so and escalates. We also publish our own calibration record as an API endpoint. A tool that knows its limits is safer than one that doesn't.

**"Why should SAIL trust a student project?"** — Don't trust it; audit it. Every decision is stored immutably with its model version and git SHA, every number is traceable, and the backtest protocol is walk-forward with point-in-time features and a leakage test in CI. Run it in shadow mode alongside the existing desk for a quarter and compare.

---

## 16. Risk register

| # | Risk | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 | Port-call source doesn't cover our target ports or lacks a dry-bulk split | High — congestion nowcast weakens | **Verify day 1.** Fallback: official monthly port statistics plus port daily vessel-position reports | F |
| R2 | Our port drafts/LOA figures are wrong and a judge knows the real ones | **Severe — destroys credibility** | `VERIFY-FIRST.md` completed before anything ships; uncited rows fail CI; unknowns shown as unknown | F |
| R3 | Policy doesn't beat naive buying in backtest | High | Gate at end of week 2 to leave recovery time. If true, report it honestly and pivot the pitch to constrained optimisation and hedging, where the value doesn't depend on timing skill | B, F |
| R4 | Backtest looks great because of leakage | **Severe — invalidates the headline** | Bitemporal store, `as_of` queries, leakage test in CI, walk-forward only, a final untuned holdout period reported separately | A, F |
| R5 | Simulated rates read as fake | High | Provenance badges, published validation table, the honest slide delivered proactively before anyone asks | B, E |
| R6 | LLM invents a figure on stage | **Severe** | No-numerals rule enforced by validator and CI; numbers injected from typed tool results only | D |
| R7 | Scope creep | High — the classic killer | Feature freeze week 4; the §2 scope discipline rule; only the memo and the backtest are uncuttable | all |
| R8 | Live API fails at the venue | High | Demo mode from a committed frozen snapshot; demo *only* from it; never depend on venue wifi | A |
| R9 | MILP too slow at realistic size | Medium | Precompute the feasibility matrix, warm-start, cap the horizon, and keep a greedy fallback | C |
| R10 | Team knows ML but not shipping, and it shows | Medium-High | The domain primer read by everyone in week 1; correct vocabulary used consistently; F reviews all copy | F |
| R11 | Frontend eats the schedule | Medium | Three screens to high finish, rest to adequate. Component library day 2, not week 4 | E |
| R12 | Grand finale environment is offline or restricted | Medium | Everything runs locally via Docker Compose with zero external calls in demo mode. Test on a laptop with wifi off | A |
| R13 | Overfitting the demo to one cargo | Medium | Five prepared scenarios across origins, classes and ports; let judges pick | F |

---

## 17. After SIH: from project to company

### 17.1 The wedge

Indian industrial dry bulk importers moving roughly 0.5–10 million tonnes a year: steel, power and cement companies that have real freight exposure but no chartering desk, no quantitative rate policy and no hedge. They are big enough for the savings to matter and small enough not to have built the capability in-house. That gap is the business.

Do not start with public sector enterprises even though the problem statement came from one. PSU procurement runs through tender processes with lowest-price selection and long cycles; it is a fine second market and a superb credibility anchor, but it is a poor first customer for an unproven product. **Land in the private sector, cite the SIH win and any SAIL pilot as proof, then go to tender from a position of strength.**

### 17.2 Phasing

**Phase 1 (0–6 months) — one route, one customer, shadow mode.** Run alongside an existing desk for a quarter on a single origin-destination pair. Log every recommendation immutably. At the end, show what the policy would have paid versus what was actually paid. This is a paid pilot, priced low, sold as an evaluation. The deliverable is not software; it is a number.

**Phase 2 (6–18 months) — the product.** Full instrument layer, hedge advisory, ERP integration, multi-plant portfolio view. Three to five paying customers. This is where pricing normalises and the company becomes real.

**Phase 3 (18–36 months) — the data asset.** By now every customer's decisions and outcomes are flowing into the same store. Two things become possible that were not before: models trained on real fixture outcomes rather than proxies, and — the important one — **an authoritative benchmark for India-bound dry bulk freight, which does not currently exist publicly.**

### 17.3 The moat

Software features are copyable. Two things are not.

**The decision-outcome dataset.** Every recommendation, stored with its model version, joined to what actually happened: the rate fixed, the vessel taken, the days waited, the demurrage paid. Nobody else has this for India-bound bulk because nobody else is in the decision loop. It compounds, it improves the models, and it cannot be bought.

**The benchmark.** Baltic-grade assessments exist for the world's liquid routes, not for Newcastle→Paradip or Taboneo→Gangavaram. A platform sitting inside enough Indian importers' fixture flow can construct the reference nobody publishes. Index businesses are structurally excellent — recurring, high-margin, defensible, and they become infrastructure that brokers, traders and derivative desks pay for. That is the version of this company that is worth a great deal of money, and it is reachable only by starting as the tool that sits in the decision.

Sequence matters: **be the decision tool to earn the data, be the data to earn the index.** Do not try to start at the index.

### 17.4 Business model

Land with a low-priced pilot, expand to enterprise subscription, offer a gainshare alternative for buyers who want the risk shifted, and add data licensing later. Pricing anchors, competitive positioning, unit economics and the funding ask are in the separate investor one-pager — deliberately kept out of the engineering plan so the two can be updated independently.

**One caution on gainshare, since it is tempting:** attributing savings requires an agreed counterfactual, and counterfactuals are arguable. If you offer it, define the baseline contractually before the pilot starts, cap the fee, and be prepared for the conversation to be harder than a subscription. It is a good closing tool and a bad default.

### 17.5 The adjacent expansions, ranked

Same buyer, more commodities (iron ore, limestone, fertiliser, bauxite) is the easiest and should come first. Same commodity, more geographies (Southeast Asian and Middle Eastern importers with the same structural gap) is next. Execution partnership with an FFA broker, taking a share of flow we originate, is attractive but requires regulatory care and should wait. Selling back to owners and operators — the incumbents' turf — is last and possibly never.

---

## 18. Verification: the two days that decide everything

`docs/VERIFY-FIRST.md` is the companion to this document and is **blocking**. It lists, in priority order, every factual claim that must be checked against a primary source before it appears in code, the UI, the deck or a customer conversation.

Priority one is whether the daily port-call source covers the target East Coast ports with a dry-bulk breakdown, because more of the architecture depends on that than on anything else. Priority two is the port constraint dataset, because it is the layer that makes shipping people trust us and the layer where being wrong is most visible. Priority three is the competitive and market claims in the business material, since those are trivially fact-checked by anyone in the room.

Assign it to F on day one. Treat a disproved assumption as a good outcome — it is far cheaper to learn it in week one than on stage.

---

## Appendix A — Glossary

Use these terms correctly and consistently; the wrong word signals an outsider faster than a wrong number.

**Laycan** — the laydays/cancelling window: the agreed span during which the vessel must present for loading. Our product is named for it because it is the constraint the whole timing decision hangs on.
**Voyage charter** — hire a vessel for one voyage; freight paid per tonne; the owner bears voyage costs.
**Time charter (TC)** — hire the vessel for a period (or a single trip, TCT) at a daily hire rate; the charterer directs employment and pays bunkers.
**COA (Contract of Affreightment)** — an agreement to move a quantity of cargo over multiple voyages in a period; tonnage nominated against agreed laycan spreads. The instrument the problem statement's objective is reaching for.
**FFA (Forward Freight Agreement)** — a cash-settled derivative on a published freight index; the only practical way a physical buyer hedges freight price risk.
**TCE (Time Charter Equivalent)** — voyage earnings expressed as $/day, making a voyage charter comparable to a timecharter. The only honest way to compare options.
**Laytime** — time allowed for loading and discharging. **Demurrage** — liquidated damages when laytime is exceeded. **Despatch** — a credit when it is beaten, often at half the demurrage rate.
**NOR (Notice of Readiness)** — the notice that starts laytime running, subject to the charter party's terms.
**Pre-berthing detention** — waiting at anchorage before a berth is available. The number that makes congestion cost money.
**Ballast / laden** — sailing empty to load / sailing loaded.
**Lightering** — discharging part of a cargo into smaller vessels or barges at anchorage so the mother vessel can enter a draft-restricted port.
**Geared / gearless** — whether the vessel has its own cranes. Decisive at ports without adequate shore equipment.
**TPC** — tonnes per centimetre immersion; converts a draft restriction into a tonnage restriction.
**FWA / DWA** — fresh and dock water allowance; the draft correction for water less dense than seawater. Matters at river ports.
**Stowage factor** — cubic metres per tonne; decides whether a cargo is weight-limited or volume-limited.
**Vessel classes** — Handysize, Handymax, Supramax, Ultramax, Panamax, Kamsarmax, Post-Panamax, Capesize, Newcastlemax, VLOC, in ascending size. Get the boundaries right in `DOMAIN-PRIMER.md`; they are conventional, not legal.
**Basis** — the difference between the price of the thing you hold and the price of the thing you can hedge. The reason a hedge is never perfect, and a number we always report.

## Appendix B — Reference dataset schema

Every row in `data/reference/ports.csv` requires: identity (`port_id`, `unlocode`, `name`, `country`, `lat`, `lon`); physical limits (`max_draft_m`, `max_loa_m`, `max_beam_m`, `max_dwt`); operational fields (`dry_bulk_berths`, `handling_rate_mtpd`, `gear_required`, `tidal_window_hrs`, `lightering_available`); environmental fields (`water_density`, `load_line_zone`); and governance fields (`source_ref`, `retrieved_at`, `confidence`).

`source_ref` must be a URL or a document citation. **A build that finds an uncited row fails.** Where a value is genuinely unavailable, write `unknown` — never a guess. The UI must render `unknown` as unknown rather than substituting a default, because a silent default in a feasibility constraint is how a system recommends a vessel that cannot berth.
