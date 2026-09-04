# VERIFY FIRST — blocking checklist

**Status: NOT STARTED. This document blocks the deck, the UI and any customer conversation.**

Everything in `MASTER-PLAN.md` was written without live internet access. The *design* stands on its own. The *facts* do not. This checklist is the bridge.

Owner: **F**. Budget: ~2 days. Method: for each item, find a primary source, record the URL and retrieval date, and mark the item verified, corrected, or unavailable. Log results inline in this file — it becomes the citation index for the whole project.

A disproved assumption found here is a win. The same assumption found on stage is not.

## Rules

1. **Primary sources only** for port physics: the port authority's own site, its port information guide or handbook, or the official national ports body. Not a shipping-agent blog, not a wiki, not a model's recollection.
2. **Record the URL and the date** you retrieved it. It goes in `source_ref`.
3. **`unknown` is an acceptable answer. A guess is not.** Never fill a gap with a plausible number.
4. If two sources disagree, **record both** and use the more conservative figure for feasibility constraints. Being conservative on a draft limit is safe; being optimistic recommends a vessel that cannot berth.
5. When you correct something, **grep the repo and the deck** for the old value.

---

## P0 — Do these before writing any more code

**V1. Daily port-call / congestion source coverage.**
Does the IMF PortWatch dataset actually include Paradip, Visakhapatnam, Gangavaram, Dhamra, Gopalpur, Haldia, Kolkata, Kakinada, Krishnapatnam and Ennore/Kamarajar? Privately-operated ports are the doubtful ones. And does it break port calls out by vessel type, specifically dry bulk?
*Why it's first:* more of the architecture rests on this than on anything else. If our ports are missing, the congestion nowcast must be rebuilt on official monthly statistics plus per-port daily vessel-position reports, and that changes week-2 scope.
*Also capture:* the actual queryable endpoint (the site is an ArcGIS-hosted app, so there should be a REST FeatureServer behind the download buttons — find it in the browser network tab), the exact field names, the history start date, and the licence text. **Do not let a guessed endpoint into the codebase.**

**V2. Indian Ports Association operational statistics.**
Confirm what is published, at what frequency, and with what history: average turnaround time, pre-berthing detention, output per ship-berth-day, idle time at berth. Get the actual file format. Confirm whether non-major (private) ports appear at all — Gangavaram, Dhamra and Gopalpur may not, which matters because they are the deep-draft ports central to our Capesize argument.

**V3. Port constraint dataset — the credibility layer.**
For every port in `data/reference/ports.csv`, verify from a primary source: maximum permissible draft, maximum LOA, maximum beam, maximum DWT, number of dry bulk berths, published handling/discharge rate, whether shore gear is available or vessel gear is required, tidal window constraints, water density (fresh/brackish/sea), and whether lightering is practised.

Discharge ports: **Paradip, Dhamra, Gopalpur, Visakhapatnam (inner and outer harbour are different — capture both), Gangavaram, Kakinada, Krishnapatnam, Ennore/Kamarajar, Chennai, Haldia, Kolkata, Sagar Roads / Sandheads anchorage.**

Load ports: **Newcastle, Hay Point, Dalrymple Bay, Gladstone, Abbot Point, Port Hedland, Dampier, Port Walcott; Indonesian Kalimantan anchorage loading points (Taboneo, Samarinda, Banjarmasin, Balikpapan); Richards Bay, Maputo, Beira, Nacala; Hampton Roads, Baltimore, New Orleans, Mobile; Vostochny.**

*Specific things to establish rather than assume:*
- Which East Coast ports can actually take a fully-laden Capesize, and which cannot. Our whole "why not Capesize" demo moment depends on this being right.
- The Haldia and Sandheads arrangement: what is the real draft limit up-river, what is lightered where, and what does it cost. Get an actual figure or mark it unknown.
- Indonesian anchorage loading via barges and floating cranes: what does it do to the effective load rate and the maximum vessel size? This is why Indonesian coal moves in smaller parcels and our model must reflect it.
- Mississippi river draft limits for US Gulf loading, which vary.

**V4. Vessel class particulars.**
Confirm DWT boundaries, representative LOA, beam, summer draft, TPC, grain capacity, hold count, whether the class is typically geared, and representative speed and bunker consumption for Handysize, Handymax, Supramax, Ultramax, Panamax, Kamsarmax, Post-Panamax, Capesize, Newcastlemax. Class boundaries are conventional and sources differ — pick one convention, cite it, and be consistent. For consumption, the EU MRV per-ship reporting dataset gives real observed figures and is free; prefer it over textbook curves.

**V5. Stowage factors.** Coking coal, thermal coal, iron ore, iron ore pellets, limestone, bauxite. Get a cited range, not a point value, and note that coal varies by origin.

---

## P1 — Before the backtest is believed

**V6. Freight rate proxies.** Confirm each is real and accessible: the dry bulk freight ETP's daily price history and whether its published holdings disclose the underlying FFA contracts and marks; the quarterly TCE-by-vessel-class disclosures in listed dry bulk owners' filings (confirm which companies break out by class, and how far back); the free settlement data on the freight derivative exchanges and — critically — **whether their terms permit our use, since settlements derive from a licensed index even when viewing is free.**

**V7. FFA broker newsletters.** Sign up for two or three free daily or weekly FFA market reports. Confirm they contain forward curve levels by quarter and calendar year, and confirm they are intended for circulation. This is the most underrated item on the list — a real forward curve, free, within a week.

**V8. Academic calibration anchors.** Find published statistics you can legally cite for dry bulk index mean-reversion half-life, volatility, and jump behaviour. Also settle the honest position on the central question: **does the forward curve beat model forecasts of future spot?** Our §12.3 refusal depends on knowing the literature's answer. Record the papers.

**V9. Contract and cost conventions.** Typical address and brokerage commission percentages. Typical demurrage rates in $/day by vessel class in current market conditions. Typical despatch convention (half demurrage?). Port disbursement magnitudes at the target ports. Canal toll schedules if any route uses one. Each of these enters the voyage calculator directly.

**V10. Sailing distances.** Get accepted distances for the dozen validation routes and use them to check the graph router's output. Sources: an industry distance reference for the ground truth, plus the marine network graph for our own computation. Record the mean absolute error — it goes on a slide.

**V11. Load line zones.** Confirm the seasonal zone boundaries and dates applicable to the Bay of Bengal and the routes we model. This affects permissible draft for an autumn laycan and is the kind of detail that impresses.

---

## P2 — Before the business material goes out

**V12. Competitors.** For Kpler (and the vessel-tracking and port-data businesses it has absorbed), Signal Ocean, Veson Nautical, Windward, Clarksons, Shipfix, Sedna, Marcura, Bearing AI, Toqua, and the container-focused visibility players: what each actually sells, to whom, and at what price where public. Then specifically test our central claim — **that none of them sell prescriptive timing-plus-instrument-plus-hedge decisions to occasional physical importers.** Look for counter-evidence honestly. If someone does occupy this position, better to know now.
Also check Indian freight-tech and maritime-tech startups, and whether any FFA broker offers software rather than broking to physical buyers.

**V13. Market sizing.** India's coking and thermal coal import volumes and values; SAIL's disclosed import tonnage and freight or logistics spend from its annual report; import volumes for the other large Indian steel, power and cement importers; global dry bulk seaborne trade in tonnes and tonne-miles from the UNCTAD annual review; FFA market size in lots cleared and notional value; freight as a share of delivered cost for imported coal into India. Every figure sourced or explicitly labelled an estimate with reasoning.

**V14. The savings claim.** This one needs care because it is the number people will remember. Find published Indian port average turnaround and pre-berthing detention figures, typical demurrage rates, and any studies on freight timing or hedging value. Then build the savings estimate bottom-up from our own backtest rather than top-down from a market-size multiplication. **Never quote a savings percentage that the backtest does not produce.**

**V15. PSU procurement reality.** How software is actually bought by an Indian public sector enterprise: the government marketplace route, tender processes, lowest-price selection, empanelment, typical cycle length. This is a genuine go-to-market risk and the one-pager must describe it accurately rather than optimistically.

**V16. Licensing cost of real data.** Get indicative pricing for a licensed freight index feed and for satellite AIS. It belongs in the funding ask as a concrete line item — it is the single cleanest use of seed capital and it turns our biggest weakness into a plan.

---

## Log

| ID | Item | Status | Source URL | Retrieved | Notes |
|---|---|---|---|---|---|
| V1 | Port-call coverage | ☐ | | | |
| V2 | IPA statistics | ☐ | | | |
| V3 | Port constraints | ☐ | | | |
| V4 | Vessel particulars | ☐ | | | |
| V5 | Stowage factors | ☐ | | | |
| V6 | Rate proxies | ☐ | | | |
| V7 | FFA newsletters | ☐ | | | |
| V8 | Literature anchors | ☐ | | | |
| V9 | Cost conventions | ☐ | | | |
| V10 | Distances | ☐ | | | |
| V11 | Load line zones | ☐ | | | |
| V12 | Competitors | ☐ | | | |
| V13 | Market sizing | ☐ | | | |
| V14 | Savings claim | ☐ | | | |
| V15 | PSU procurement | ☐ | | | |
| V16 | Data licence cost | ☐ | | | |
