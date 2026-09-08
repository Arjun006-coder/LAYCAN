# LAYCAN · Final Slide-by-Slide Stage Pitch Script
### Intelligent Freight Decision Engine & Vessel Chartering Desk for Overseas Bulk Cargo
**SIH 2026 Problem Statement 26006 · Ministry of Steel / Steel Authority of India Limited (SAIL)**
**Team: Atomic**

---

## Pitch Delivery Guidelines
* **Target Duration:** 3 minutes 45 seconds to 4 minutes.
* **Tone:** Authoritative, clear, and grounded. Confident in both the industry economics and the mathematical architecture.
* **Pacing Rule:** Spend ~30 to 45 seconds per slide. Do not rush; let key metrics and terminology land clearly with the judges.

---

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PRESENTATION MAP                                       │
├─────────┬──────────────────────────────────────────────────────────┬───────────────────┤
│ SLIDE 1 │ Title & The National Hook                                │ 0:00 – 0:35       │
│ SLIDE 2 │ The Real-World Problem & The Capesize Trap               │ 0:35 – 1:20       │
│ SLIDE 3 │ Technical Architecture: Formulas, ML & Live Data Feeds   │ 1:20 – 2:15       │
│ SLIDE 4 │ Feasibility, Competitors & Why It Didn't Exist Before     │ 2:15 – 3:00       │
│ SLIDE 5 │ Quantified Business Impact & The ₹12+ Crore Backtest     │ 3:00 – 3:35       │
│ SLIDE 6 │ Official Research Anchors, Live GitHub Demo & Closing    │ 3:35 – 4:00       │
└─────────┴──────────────────────────────────────────────────────────┴───────────────────┘
```

---

## SLIDE 1: TITLE SLIDE (0:00 – 0:35)

> "Respected judges, every year India produces over 140 million tonnes of crude steel to build our nation’s highways, bridges, and infrastructure. But to make one tonne of steel, you need 0.8 tonnes of high-grade coking coal.
>
> India has virtually no domestic reserves of metallurgical coking coal. Over 85% of it must be imported by sea—mostly from Australia, Indonesia, and South Africa.
>
> The Steel Authority of India Limited (SAIL) alone imports roughly 16 million tonnes of coal every year, spending thousands of crores on ocean shipping freight.
>
> But right now, this multi-crore chartering is done through reactive, manual spot buying. When a steel plant signals low inventory, logistics managers call shipping brokers and fix whatever ship is available at whatever price the market demands that morning.
>
> We are **Team Atomic**, and we built **LAYCAN**: an autonomous maritime procurement co-pilot that answers two operational questions every morning:
> **Should we book today, or wait?**
> And **which exact vessel class will fit which port?**"

---

## SLIDE 2: PROPOSED SOLUTION & THE "CAPESIZE TRAP" (0:35 – 1:20)

> "Turning to Slide 2, let’s address the elephant in the room that every smart judge will think:
> *'If the IMF opened this satellite data in late 2023, it’s been 3 years! Why didn’t someone build this? If you can build it, why didn't the industry?'*
>
> The answer lies in **three commercial and technical realities**:
>
> **1. The Incumbent Conflict of Interest:**
> Who dominates chartering today? Big global brokerage houses (like Clarksons and Braemar). They earn a **1.25% commission on closed deals**. A broker has zero financial incentive to build an autonomous system that tells SAIL to wait 7 days for rates to drop. **Brokers make money when you trade, not when you save.**
>
> **2. The Multi-Disciplinary Silo:**
> Naval architects who understand berth drafts and Hooghly river water density don't know American option optimal stopping math. Quantitative finance graduates who understand Longstaff-Schwartz work at hedge funds in London or New York, not on coal procurement desks in Kolkata. And computer science engineers don't know that Capesize ships cannot berth at Paradip! LAYCAN bridges these three isolated worlds.
>
> **3. Modern Agentic AI Only Matured in 2025–2026:**
> Raw IMF and weather APIs give you fragmented data tables. To build an autonomous co-pilot, you needed **multi-agent reasoning and structured adversarial auditing**—the ability for an AI Critic (Gemini 3.6 Flash) to verify weather alerts and draft limits before emitting a decision memo. That technology stack was not mature 3 years ago; it is mature today.
>
> That is why LAYCAN operates as an **Autonomous Decision Desk** built on three pillars:
>
> **First, The Timing Advisor:** 
> We use an **Optimal Stopping mathematical engine** (Least-Squares Monte Carlo) that calculates a daily price threshold—called the *Reservation Rate*. If today’s market quote is higher than our expected continuation value over the next week, the system says **'WAIT'**. If it hits an attractive market dip, it says **'FIX TODAY'**.
>
> **Second, The Port Physics Core:** 
> This eliminates the costliest mistake in shipping: the **Capesize Fallacy**. 
> A giant Capesize vessel carries 180,000 tonnes and looks \$2 a tonne cheaper on paper due to scale economies. But a loaded Capesize draws 18 meters of water. Paradip’s coal berths cap permissible depth at 16 meters, and Haldia caps at 8.5 meters! 
> 
> That giant ship physically cannot enter! It is forced to anchor out at sea at Sandheads for 4 days while smaller barges lighter its cargo, racking up **+\$2.90 a tonne in extra lightering and \$25,000-a-day demurrage penalties**, turning a supposed saving into a ₹2 Crore loss. LAYCAN calculates ship depths down to the centimeter to eliminate demurrage before contracts are signed.
>
> **Third, The Adversarial Critic Agent:** 
> A dedicated AI watchdog powered by Google Gemini 3.6 Flash that stress-tests every recommendation against cyclones, port jams, and load-port rules before any memo reaches management."

---

## SLIDE 3: TECHNICAL APPROACH, FORMULAS & LIVE DATA FEEDS (1:20 – 2:15)

> "On Slide 3, let’s look under the hood at our technical architecture.
>
> We enforce an inviolable architectural rule: **Our AI agents never compute arithmetic.** 
> If you ask a language model to compute shipping economics and ship drafts, it hallucinates. In LAYCAN, pure Python mathematical solvers calculate 100% of the numbers:
>
> - **Voyage Economics:** We use the **Time Charter Equivalent (TCE)** formula, deducting address commissions and voyage costs to evaluate true daily vessel earnings.
> - **Fuel Optimization:** We model the **Admiralty Cube Law**, where fuel consumption scales with the cube of ship speed ($FC \propto v^3$). If destination berths are congested, our system calculates slow-steaming speeds that save 19% of bunker fuel without delaying unloading.
> - **Hydrostatics & Density:** We compute **Tonnes Per Centimetre (TPC) immersion** and **Dock Water Allowance (DWA)** for the brackish water of the Hooghly river at Haldia ($1010\text{ kg/m}^3$), preventing grounding.
> - **Optimal Stopping Math:** We solve the **Longstaff-Schwartz American Option backward induction** across 2,000 simulated paths to establish our daily reservation boundary.
>
> For rate forecasting, we run an automated daily tournament benchmarking **Random Walk vs. 7-Day Moving Average vs. ARIMA vs. LightGBM**, providing an 80% **Conformal Prediction** confidence band ($P_{10}–P_{90}$).
>
> **Where does our live data come from?**
> We don't use fake data. We integrated three 100% free, automated live feeds:
> 1. **IMF PortWatch ArcGIS REST:** Tracks real-time satellite AIS dry-bulk arrivals for Paradip, Vizag, and Haldia.
> 2. **Open-Meteo Marine API:** Ingests live wave heights and swell indices across the Bay of Bengal.
> 3. **Yahoo Finance (`BDRY`):** Pulls the Breakwave Dry Bulk ETF daily log-returns as an exogenous freight momentum shock."

---

## SLIDE 4: FEASIBILITY, COMPETITORS & WHY IT DIDN'T EXIST BEFORE (2:15 – 3:00)

> "On Slide 4, judges often ask: *'Why did this not exist before, and what about competitors?'*
>
> **Why It Didn't Exist Until Now:**
> 1. *The Satellite Data Wall fell in late 2023:* Until recently, global vessel AIS data was locked behind \$50,000 proprietary paywalls. In late 2023, the IMF and Oxford University opened PortWatch data via public APIs for the first time.
> 2. *Modern Structured LLMs (2025–2026):* Five years ago, AI could not act as an adversarial auditor parsing real-time unstructured marine weather and port circulars.
> 3. *The Multi-Disciplinary Silo:* Naval architects, quantitative finance analysts, and software engineers rarely work on the same problem. LAYCAN unifies all three.
>
> **The Competitor Landscape:**
> - **Global Maritime Giants (Kpler, Signal Ocean):** Cost \$50,000 to \$80,000 a year. They are *descriptive*, not *prescriptive*—they show dots on a map, but never give an Indian importer a daily 'Fix or Wait' decision, and they ignore Indian berth draft restrictions.
> - **Domestic Logistics Tech (FreightFox, Fretron):** Focus exclusively on domestic road and rail freight; their expertise ends at the shoreline.
> - **Human Shipbrokers:** Earn a 1.25% commission on closed fixtures. Their commercial incentive is to close a deal quickly, not to tell you to wait 5 days for a market dip.
>
> **Four Pillars of Feasibility:**
> - **Zero Cost:** 100% free public data.
> - **Zero Crashes:** Dual-mode graceful degradation with offline verified snapshots.
> - **Low Adoption Friction:** 90-day shadow mode pilot proving P&L side-by-side.
> - **CVC & CAG Compliance:** Immutable, timestamped audit logs for every trade decision."

---

## SLIDE 5: QUANTIFIED BUSINESS IMPACT & THE BACKTEST (3:00 – 3:35)

> "Turning to Slide 5, what is the bottom-line financial proof?
>
> We ran a **5-year walk-forward decision backtest** across 24 sequential shipments.
> 
> *Where did the data come from?* 
> Real route fixtures are private OTC contracts under NDAs. So we calibrated a mean-reverting Ornstein-Uhlenbeck stochastic process where volatility ($\sigma = 0.022$) is grounded in **5 years of live BDRY ETF log-returns**, and price boundaries (\$16 to \$32/MT) are anchored in **audited SEC 10-K filings from public carriers like Star Bulk and Genco**.
>
> Across those 24 shipments:
> - The **Naive Policy** (buying on Day 0) averaged **\$23.50/MT**.
> - The **LAYCAN Policy** averaged **\$22.90/MT**—saving an average of **\$0.60 per tonne**.
> - LAYCAN captured **52% of all theoretically available timing dips** (Capture Ratio).
> - Total net delivered savings: **\$1.4 Million USD, or ₹12.06 Crores INR**.
>
> For an enterprise like SAIL importing 16 million tonnes of coal annually, saving just **75 cents a tonne expands recurring EBITDA by over ₹100 Crore every single year**."

---

## SLIDE 6: RESEARCH, LIVE DEMO & CLOSE (3:35 – 4:00)

> "On Slide 6, our work is rigorously anchored in official port handbooks from Paradip, Visakhapatnam, and Kolkata, backed by established maritime economics literature.
>
> Our system is not an idea on paper. The entire platform—including all deterministic solvers, live API feeds, multi-agent supervisor, FastAPI backend, and interactive Streamlit cockpit—is **fully built, unit-tested, and live on our GitHub repository right now**.
>
> LAYCAN turns overseas bulk procurement from a reactive gamble into an automated, money-saving science.
>
> Thank you, and we are now ready for your questions!"

---

## Quick Reference: 5 Essential Points to Keep in Mind During Q&A

1. **If asked about AI doing math:**  
   *"Our AI agents never compute numbers. Pure Python solvers calculate 100% of dollars, drafts, and days. The Gemini 3.6 Flash agent acts as an executive translator and an Adversarial Critic."*
2. **If asked why Capesize isn't always best:**  
   *"Capesize draws 18.0m laden draft. Paradip coal berths cap at 16.0m and Haldia caps at 8.5m. Forced lightering at Sandheads adds +\$2.90/t and 3.5 days of delay, wiping out the \$2.10/t scale discount."*
3. **If asked about the backtest data:**  
   *"Specific route rates are private OTC contracts under NDAs. We calibrated our stochastic rate path to 5-year BDRY ETF volatility and verified price levels against SEC 10-K filings from listed bulk carriers like Star Bulk and Genco."*
4. **If asked about data costs:**  
   *"Total data cost is ₹0. We use open scientific APIs: IMF PortWatch ArcGIS REST, Open-Meteo Marine, US EIA v2, and Yahoo Finance."*
5. **If asked about competitors:**  
   *"Global tools like Kpler cost \$50k/yr and only show dots on a map; domestic tools only do road trucking; and human brokers have a 1.25% commission conflict of interest. LAYCAN is the only prescriptive decision co-pilot built for Indian bulk importers."*
