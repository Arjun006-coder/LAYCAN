# Domain Primer — dry bulk shipping for engineers

**Read this in week 1. All of it.** You are building software for an industry with a hundred and fifty years of its own vocabulary, and the fastest way to lose a shipping audience is to use the wrong word confidently.

> ⚠️ **All numeric ranges here are approximate and unverified** (written without internet access). They are correct in order of magnitude and useful for building. They are not citable. `VERIFY-FIRST.md` items V3–V5 and V9 replace them with sourced figures. Use this to *understand*; use the verified dataset to *compute*.

---

## 1. The four ways to buy ocean transport

**Voyage charter.** You hire a ship for one voyage, A to B, and pay **freight** in dollars per tonne of cargo. The owner pays the voyage costs — bunkers, port dues, canal tolls. You pay for time you waste beyond the agreed allowance. This is the spot market and it is what SAIL does today, repeatedly.

**Time charter (TC).** You hire the ship itself for a period and pay **hire** in dollars per day. Now *you* pay the bunkers and *you* direct the ship, so you carry the fuel price risk and the speed decision, but you also capture the upside if you operate it well. A **trip time charter (TCT)** is the same thing for a single voyage — common when a charterer wants control of a specific trip.

**Contract of Affreightment (COA).** You agree to move a quantity of cargo — say six cargoes of 75,000 tonnes over a year — and the owner agrees to provide tonnage against agreed laycan spreads, nominated as each cargo comes up. You get rate certainty and guaranteed access to ships. You take on an obligation: if you fail to present the cargo, you pay for it (a "short-lift" or "deadfreight" claim). **This is the instrument the problem statement's stated objective is reaching for** — moving from many single spot fixtures to term multi-voyage cover.

**Bareboat charter.** You take the ship without crew and operate it yourself. Irrelevant to us; know the word exists.

### And the fifth thing, which is not transport at all

**Forward Freight Agreement (FFA).** A cash-settled derivative on a published freight index, cleared through an exchange. You never touch a ship. If you are going to buy freight in Q4 and you fear rates rising, you buy FFAs now; if rates rise, your physical cost goes up and your derivative pays out. It is the only practical way a physical buyer manages freight *price* risk separately from freight *procurement*.

Contracts exist on the timecharter baskets for each vessel class and on some voyage routes. Liquidity concentrates in the nearest quarters and the front calendar year, and thins fast beyond that. Settlement is against the average of the index over the contract month, which is why an FFA hedges an *average* exposure well and a *single voyage on a specific date* only approximately — the residual is basis risk.

**Why this matters commercially:** a trading house hedges routinely. An Indian steel plant's procurement team, in general, does not — no mandate, no desk, no familiarity. Meanwhile their counterparty on the other side of every negotiation often does. Closing that asymmetry is our wedge.

---

## 2. The vocabulary you must get right

**Laycan** — laydays/cancelling. The window during which the vessel must present for loading. Before laydays the charterer need not accept her; after cancelling the charterer may walk away. Every timing decision lives inside this window, which is why the product is named for it.

**Fixture** — a concluded deal. **On subs** — agreed subject to conditions still to be lifted. **Recap** — the summary of agreed terms circulated after fixing. **Charter party** — the contract; standard forms exist for dry bulk voyage and timecharter work.

**NOR (Notice of Readiness)** — the master's notice that the vessel is arrived and ready. It starts the laytime clock, subject to the charter party's terms. The abbreviations governing *when* NOR can validly be tendered — whether in berth or not, in port or not, in free pratique or not, customs cleared or not — matter enormously in real disputes, because they decide who pays for waiting.

**Laytime** — the time allowed for loading and discharging, usually derived from the cargo quantity and an agreed rate. **Demurrage** — liquidated damages, per day, when you exceed it. **Despatch** — a credit when you beat it, conventionally at half the demurrage rate. **Reversible laytime** — load and discharge allowances pooled, so time saved at one end offsets time lost at the other.

Laytime exclusions are where the money is: weather working days, and whether Sundays and holidays are excepted (SHEX) or included (SHINC).

**Pre-berthing detention** — waiting at anchorage for a berth. The metric that turns congestion into a bill.

**Ballast / laden** — sailing empty toward a load port / sailing with cargo. **Deadheading** — a long unpaid ballast leg. Ballast cost is why route geography drives rates.

**Geared / gearless** — whether the ship carries her own cranes. Decisive where shore equipment is inadequate; a gearless ship at a port with no shore cranes simply cannot work cargo.

**FIOST / gross terms / liner terms** — who pays for loading and discharge, and whether stowing and trimming are included. Changes the cost split materially; get it right in the voyage calculator.

**MOLOO / MOLCHOPT** — more or less in owner's / charterer's option. The tolerance on the cargo quantity, typically ±5% or ±10%. It sounds like a detail; it is actually an option with value, because it lets you flex intake against the draft constraint.

**Commissions** — address commission to the charterer and brokerage to the broker, deducted from gross freight. Together commonly in the low single-digit percent (*verify V9*).

---

## 3. The arithmetic

### Time Charter Equivalent — the only fair comparison

Freight in $/mt cannot be compared across vessel classes or route lengths. Convert everything to $/day:

```
TCE = ( freight × cargo_qty − commissions − voyage_costs ) / round_voyage_days
```

A Capesize at $18/mt and a Supramax at $26/mt on the same route may earn identical TCE. Any product that compares $/mt across classes without converting is wrong, and a shipping person spots it in seconds.

### Voyage costs

Bunkers (at sea on both legs, plus in-port consumption), port disbursements at both ends (dues, pilotage, towage, agency, mooring), cargo dues, canal tolls if applicable, war risk premium in exposed areas, and extras (holds cleaning, surveys, overtime). Bunkers usually dominate.

### Duration

```
days = ballast_nm/(24·v_ballast) + laden_nm/(24·v_laden)
     + qty/load_rate + qty/discharge_rate
     + waiting_days + weather_margin
```

Waiting days are where congestion enters the economics, and they are frequently the difference between two options.

### Fuel and the cube law

Main engine consumption scales roughly with the cube of speed:

```
consumption_per_day(v) = consumption_ref × (v/v_ref)³
fuel_for_a_leg(v) = consumption_per_day(v) × distance/(24·v)   →  scales as v²
```

So slowing 10% cuts fuel for a fixed distance by about 19% while adding about 11% to the days. Whether that is a good trade depends on the hire rate and on whether those extra days replace waiting time you were going to burn at anchorage anyway. That comparison is a real product feature, not a curiosity.

### Draft to tonnes — the calculation outsiders skip

A port's draft limit is really a cargo limit:

```
d_max     = permissible_draft − under_keel_clearance
ΔDWT      = TPC × 100 × (summer_draft − d_max)      [TPC in mt/cm]
DWT_avail = summer_DWT − ΔDWT
cargo     = DWT_avail − bunkers − fresh_water − stores − constants
```

Then the density correction, because river and brackish ports float a ship deeper:

```
FWA_mm = displacement / (4 × TPC)
DWA_mm = FWA_mm × (1025 − ρ_dock) / 25
```

And a volume check, because some cargoes fill the holds before they fill the deadweight:

```
volume_limited_cargo = grain_capacity_m³ / stowage_factor_m³_per_mt
INTAKE = min(weight_limited, volume_limited)
```

Coal is normally weight-limited; iron ore emphatically so; light cargoes like some fertilisers can be volume-limited. Keep both branches.

**Load line zones** add a seasonal layer: permissible draft varies by zone and date, and the Bay of Bengal has a seasonal zone that genuinely bites for autumn laycans (*verify V11*).

### Lightering

When the mother vessel is too deep for the port, part of the cargo comes out at a deepwater anchorage into smaller vessels or barges:

```
lightering_cost = tonnes_lightered × rate + extra_days × (hire + port_consumption)
```

The strategic point for our product: **a bigger ship's lower $/mt can be entirely eaten by lightering plus waiting.** An optimiser that treats vessel size as monotonically better is wrong, and demonstrating that live is our strongest moment.

---

## 4. Vessel classes

Boundaries are conventional, not legal, and sources differ. Pick one convention, cite it, be consistent (*verify V4*).

| Class | Approx DWT | Character | Geared? |
|---|---|---|---|
| Handysize | ~10–40k | Small parcels, shallow and minor ports, very flexible | usually yes |
| Handymax / Supramax | ~40–60k | The workhorse; Supramax ~52–60k | usually yes |
| Ultramax | ~60–65k | Modern, more efficient Supramax | usually yes |
| Panamax | ~65–80k | Sized to old Panama locks | usually no |
| Kamsarmax | ~80–85k | Max LOA for Port Kamsar; now the dominant Panamax-type newbuild | no |
| Post-Panamax | ~85–120k | Awkward middle | no |
| Capesize | ~150–200k | Iron ore and coal on long hauls; too big for many ports | no |
| Newcastlemax | ~200–210k | Max for Newcastle | no |
| VLOC / Valemax | ~250–400k | Dedicated ore trades, very few ports | no |

Two consequences that shape the model. **Gear matters:** at ports without adequate shore cranes, a gearless Panamax is infeasible where a geared Supramax is fine — a hard constraint, not a cost. **Bigger is not cheaper if it cannot berth:** the entire vessel-selection problem is the tension between economies of scale and port physics.

---

## 5. Indices, routes, and the basis problem

The Baltic Exchange publishes daily assessments from a panel of brokers: headline indices per vessel class and individual route assessments (voyage routes in $/mt, timecharter routes in $/day), plus timecharter basket averages that FFAs settle against.

**These assessments are licensed and paywalled.** Headline index levels leak into public news daily; route-level data does not. We do not scrape them (see MASTER-PLAN §8.2).

**The basis problem, which you must internalise.** There is no published assessment for Hay Point → Paradip. There are assessments for the big liquid trades — Brazil and West Australia to China on Capesize, the Atlantic and Pacific Panamax rounds, the Supramax and Handysize baskets. Our routes are not among them.

Practitioners handle this by decomposition, and so do we:

```
rate(our route) = liquid_reference + basis
```

The reference is forecastable and hedgeable. The basis — driven by distance, port efficiency, cargo type, local tonnage balance — is slow-moving, much less noisy, and estimated separately. This is the honest architecture, and it is what makes the hedging module truthful: you hedge the reference, you cannot hedge the basis, and **residual basis risk is a number we always report.**

---

## 6. What actually moves dry bulk freight

The governing identity:

```
freight ≈ f( tonne-mile demand / effective fleet supply )
```

Both sides move, and *effective* supply is the subtle one — congestion, slow steaming and repositioning all destroy capacity without removing a single ship from the fleet. A port queue is a supply shock.

**Demand side.** Chinese steel production and iron ore restocking; Indian coal import appetite, which is partly a function of domestic production and power plant stock cover; grain seasons in the Atlantic and South America; bauxite and coal long-hauls. New long-haul mining capacity is the structural swing factor, because tonne-miles matter more than tonnes — the same cargo shipped further consumes more of the fleet.

**Supply side.** The newbuilding orderbook and delivery schedule; scrapping, which rises when rates fall; and environmental regulation, which effectively reduces supply by pushing ships to slow down. Carbon intensity rules, regional emissions trading and fuel regulations all push in the same direction.

**Friction.** Canal and chokepoint constraints can reroute whole trades; when a route lengthens, effective supply falls and rates rise everywhere.

**Seasonality that matters for our routes specifically.** Australian cyclone season roughly December–April can close northwest Australian loading ports. Indonesian monsoon disrupts barge feeding, which is how most Kalimantan coal reaches a ship. Southwest monsoon June–September affects Indian east coast discharge operations. The Bay of Bengal has two cyclone seasons — roughly April–June and October–December, the latter more severe. Chinese New Year reliably slows activity. Northern hemisphere winter lifts coal demand.

Seasonality is free, real, high-signal, and available from decades of open cyclone-track and port-traffic data. Use it.

---

## 7. How a charterer's day actually goes

Understanding this is how we know where software can insert itself.

The plant declares a requirement — tonnage, quality, a window. The chartering desk turns that into a cargo enquiry: quantity with tolerance, load port, discharge port, laycan, terms. It goes out to three or four brokers, usually by email. Offers come back over hours or days as indications, then firm offers. There is negotiation on rate, on laytime, on demurrage, on who pays what. Eventually the deal is agreed on subs, subs are lifted, a recap circulates, and the charter party follows.

Then operations: nomination, pre-arrival, NOR on arrival, the laytime clock, loading, sailing, arrival at the discharge end, possibly a queue, discharge, and finally a laytime statement and a demurrage or despatch claim that may take weeks to settle.

**Where it hurts.** There is no price discipline — nobody can say whether today's offer is good relative to the option of waiting, so the decision defaults to "the plant needs coal, fix it." Vessel choice is habit, not calculation, and the draft-versus-scale trade is rarely computed properly. Everything lives in email and spreadsheets, so there is no institutional memory of what was decided or why. Freight price risk is carried entirely, unhedged. And post-voyage, nobody systematically compares what was paid against what could have been paid.

Every one of those is a line item in our product. That is not a coincidence — it is how the product was designed.

---

## 8. What the research literature actually says

Read this before you promise a judge an accuracy figure.

**Freight rates are hard to forecast.** Dry bulk rates show high volatility, volatility clustering, long-horizon mean reversion, and jumps. At the horizons a charterer cares about, beating a random walk on point accuracy is genuinely difficult, and published improvements are usually modest and regime-dependent.

**The forward curve is a strong competitor.** Where FFAs are liquid, forward prices aggregate informed opinion and are hard to beat as predictors of future spot. There is a literature on whether forward freight prices are unbiased predictors, with mixed findings and evidence of time-varying risk premia — but the working assumption for a student team should be: **do not claim to beat the curve.** Benchmark against it, report honestly, and locate your value elsewhere. Our product does exactly that; the value is in the stopping policy, the constraints and the hedge, none of which require forecast superiority.

**Mean reversion is real but slow.** Published half-life estimates for dry bulk indices give us a defensible calibration anchor for the mean-reversion parameter without needing the underlying licensed series.

**Hedging works, imperfectly.** There is a substantial literature on FFA hedging effectiveness, optimal hedge ratios, and time-varying hedge ratios estimated with GARCH-family models. Effectiveness is materially less than one, and basis risk is the reason. Reporting effectiveness *and* residual basis risk is the honest presentation.

**Optimal stopping is an established frame.** Timing decisions under uncertainty with a deadline are a well-studied class of problem, and Least-Squares Monte Carlo is a standard, respected numerical method for them. Using it here is applying a mature tool to a new domain — which is exactly the kind of contribution that travels well at an international hackathon.

*(Fill in the actual citations under V8 — the arguments above are correct in substance but need papers attached before they go in a deck.)*

---

## 9. Ten sentences that make you sound like an insider

Use them accurately or not at all.

"What's the laycan?" · "That's on subs." · "She's gearless, so Paradip needs shore cranes." · "Freight looks cheap but the TCE is poor because of the ballast leg." · "We'll take her at 75,000 ten percent MOLOO." · "Draft-restricted, so intake caps out well below her summer deadweight." · "Pre-berthing detention is running near three days, so price the demurrage in." · "We're long freight and unhedged into Q4." · "The basis to the published route is about a dollar." · "Short-lifting the COA costs more than the rate saving."
