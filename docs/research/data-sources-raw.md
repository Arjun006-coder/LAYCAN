# Data Source Research — Dry Bulk Freight / Vessel Chartering Platform

## ⚠️ READ THIS FIRST — CRITICAL CAVEAT ABOUT THIS REPORT

**I had zero web access for this task and verified nothing.** Specifically:
- `WebSearch` is not provisioned at the API gateway (`Tool 'web_search' not found in provided tools`)
- `mcp__workspace__web_fetch` egress allowlist permits **only** `agentrouter.org`
- `curl` from the workspace shell has no network route at all (HTTP 000)
- I spawned a subagent to confirm this is not a parent-only restriction — **it hit identical errors**

So everything below comes from **model knowledge (cutoff May 2026)**, not from live pages. I have **not fabricated** endpoints — where I recall a URL pattern I say so; where I am guessing I label it. But treat every URL as a **lead to verify**, not a citation. I have filed **task #8** with a prioritised verification checklist.

Confidence tags used throughout:
- **[HIGH]** — I am confident this source exists, is free, and works roughly as described
- **[MED]** — exists and is probably free, but access mechanics/limits need checking
- **[LOW]** — recalled vaguely; verify before relying on it, may be wrong or dead

The port draft/LOA numbers in sections 7–8 are **model knowledge, not citations**. Do not put them in a deck until checked. I flag this again inline because it is the single biggest fabrication risk in this report.

---

## 1. DRY BULK FREIGHT RATES — the honest answer

### The blunt verdict

**Baltic Exchange route assessments (C3, C5, C10_14, P2A, P6, S1B, S10, etc.) are a PAYWALLED DEAD END. There is no free tier, no free API, no delayed feed, no academic tier. Stop looking.** [HIGH]

The Baltic Exchange has been owned by **SGX** since 2016. Its indices and daily route assessments are its core commercial product, licensed to members and redistributed only through paid terminals (LSEG/Refinitiv, Bloomberg, S&P Global). Redistribution is aggressively enforced — this is *the* thing they sell. A student team will not get legitimate access to route-level data. Budget a hard "no."

The **headline index levels** (BDI, BCI, BPI, BSI, BHSI) are a different story — they leak into the public domain daily through news republication.

### Source-by-source

| Source | Reality | Verdict |
|---|---|---|
| **balticexchange.com** | Index page historically shows the day's headline BDI/BCI/BPI/BSI/BHSI values free. No history, no API, no route rates. Also posts the daily BDI to X/LinkedIn. [MED] | Free *glance* only |
| **Hellenic Shipping News** (`hellenicshippingnews.com`) | Republishes the Baltic's **daily dry bulk market report** as free articles — routinely includes BDI + all five sub-index values, and often route-level rate commentary ($/day TC averages, $/t on C5/C3). This is, practically, the closest thing to free Baltic data that exists. [MED–HIGH] | **USABLE WITH EFFORT** — best free Baltic route proxy |
| **Splash247** (`splash247.com`) | Free RSS + articles, weekly dry bulk wraps with index levels. [HIGH] | Supporting |
| **TradingEconomics** (`tradingeconomics.com/commodity/baltic`) | Free web chart with multi-year BDI history. API is paid; a limited free/guest tier has historically existed but is heavily capped. ToS forbids redistribution. [MED] | Free view; API **[LOW]** |
| **Investing.com** (Baltic Dry Index, `BDIY`) | Free historical data table, CSV export behind a free login. ToS prohibits scraping/redistribution. [MED] | Grey but practically obtainable |
| **Bloomberg** | Free public quote page for `BDIY:IND` shows current BDI. Terminal tickers are paid. [MED] | Free glance |
| **LSEG/Refinitiv** | Baltic RICs (I recall `.BADI` for BDI, `.BACI`/`.BAPI`/`.BASI` for Cape/Panamax/Supramax) — **[LOW]** on exact RICs. Paid regardless. | **PAYWALLED** |
| **Yahoo Finance** | **No BDI symbol exists.** Claims of `^BDI` are wrong. Do not build on this. [HIGH] | Dead end |
| **FRED** | **Does not carry BDI** — licensing prevents it. Do not waste time. [MED–HIGH] | Dead end |
| **Quandl / Nasdaq Data Link** | Historically hosted community BDI series; Nasdaq killed most free datasets post-acquisition. Assume gone. [MED] | Probably dead |
| **Kaggle** | **Multiple community datasets of historical BDI daily values exist as CSV.** Free, immediate, no auth beyond a Kaggle account. Licence is uploader-declared (often CC0) but the data is derived from a paywalled source — legally murky, fine for a hackathon, **not** shippable in a commercial product. [MED–HIGH] | **USABLE NOW** (grey licence) |
| **HuggingFace Datasets** | Possible but less likely than Kaggle. [LOW] | Check |
| **GitHub** | Scraped BDI CSVs in forecasting repos are common. Same grey licence. [MED] | Usable |
| **Drewry** | Publishes the **World Container Index** composite free weekly — **containers, useless for dry bulk.** Dry bulk products paywalled. [HIGH] | Dead end |
| **Xeneta** | Container + air freight. Not dry bulk. [HIGH] | Irrelevant |
| **Freightos FBX** | Container spot rates, free to view. Not dry bulk. [HIGH] | Irrelevant |
| **UNCTAD** | **Free and legally clean.** *Review of Maritime Transport* (annual PDF) publishes dry bulk freight rate charts and annual averages (sourced from Clarksons). UNCTADstat has fleet, Liner Shipping Connectivity Index, port call stats. Annual granularity only. [HIGH] | **USABLE NOW** for calibration targets |
| **Clarksons SIN** | Paid, expensive (£thousands/yr). Free press releases and *Shipping Intelligence Weekly* teasers contain occasional headline numbers. Some universities have institutional access — **worth asking your college library/department, this is the one realistic route to real data.** [HIGH] | **PAYWALLED** (unless institutional) |
| **S&P Global Commodity Insights / Platts** | Paid. Free market commentary occasionally quotes spot rates. [HIGH] | **PAYWALLED** |
| **Argus** | Paid. Free press releases (esp. coal freight). [HIGH] | **PAYWALLED** |
| **Indian sources** | **None publish Baltic indices.** IPA/MoPSW publish traffic and turnaround, not freight rates. Indian business press (BusinessLine, Business Standard, ET) quote BDI in articles. [HIGH] | Nothing native |

### The genuinely free, legally clean dry-bulk rate proxies — use these

This is the most valuable part of section 1. Four real substitutes:

**(a) BDRY — Breakwave Dry Bulk Shipping ETF** [MED–HIGH] — **strongest single find.**
This ETF holds **actual near-dated FFA contracts** on Capesize/Panamax/Supramax TC routes. Consequences:
- Its **daily price/NAV is a direct, free, tradeable proxy for the front of the dry bulk FFA curve** — pull via `yfinance` (`BDRY`), free, daily, back to inception (2018).
- The issuer publishes **daily holdings**, which disclose the specific FFA contracts held, months, and marks. If that disclosure is as granular as I recall, **it is a free window onto actual FFA settlement prices.** Verify this first — high payoff.
- Companion: **BOAT** (SonicShares Global Shipping) for broader shipping beta.

**(b) SEC EDGAR — listed dry bulk owners' TCE disclosures** [HIGH] — **the credibility anchor.**
Star Bulk (SBLK), Genco (GNK), Golden Ocean (GOGL), Diana (DSX), Eagle Bulk, Safe Bulkers, Himalaya, Pangaea file 20-F/6-K/10-Q containing **average daily Time Charter Equivalent (TCE) rates broken down by vessel class (Capesize / Kamsarmax / Panamax / Supramax / Handysize), per quarter, going back 10–15 years.** Free, official, fully citable, redistributable, and available via the **free EDGAR full-text search + submissions API** (`data.sec.gov`, no key, just a User-Agent header). [HIGH]
This gives you a **real, legal, quarterly dry-bulk earnings dataset by vessel class** — exactly the variable a chartering platform needs — with no licence problem. Use it to calibrate and to validate your synthetic daily series.

**(c) Shipping equities as a daily high-frequency proxy** [HIGH]
`yfinance` for SBLK, GNK, GOGL, DSX, NMM, SB, PANL. Dry bulk equity prices are strongly correlated with spot/FFA levels. Free, daily, decades of history, no licence issue. Use as a daily interpolator between quarterly TCE truths.

**(d) Commodity spread arithmetic — freight ≈ CIF − FOB** [HIGH conceptually]
- **API2 (CIF ARA) − API4 (FOB Richards Bay) ≈ Richards Bay→ARA Capesize freight.** Both indices are Argus/McCloskey (paid), **but CME lists futures on both** and **CME publishes free delayed daily settlement prices** on its website. [MED — verify contract codes; I recall API2 as `ATW` but **[LOW]** on that]
- Iron ore: **SGX 62% Fe CFR China futures** (free daily settlements on sgx.com [MED]) vs an FOB Australia reference → Western Australia→China Capesize freight.
- Coal: World Bank Pink Sheet has **Australian thermal (FOB Newcastle)** and **South African (FOB Richards Bay)**; pair with a CFR India reference to imply freight. Monthly only.

**Bottom line for section 1:** you cannot get Baltic route data. You *can* get (i) a free daily FFA-linked price series (BDRY), (ii) a free official quarterly TCE-by-class dataset (SEC EDGAR), (iii) free daily headline BDI via news republication, and (iv) free commodity spreads. That combination is enough to build something genuinely real and to defend it to judges.

---

## 2. FFA / FORWARD FREIGHT AGREEMENT CURVES

| Source | Detail | Verdict |
|---|---|---|
| **SGX** (`sgx.com`) | Lists FFAs on Baltic routes — Capesize 5TC, Panamax 4TC/5TC, Supramax 10TC, Handysize 7TC, plus iron ore and Indonesian coal. SGX publishes **daily settlement prices** and free monthly commodities/freight reports (volumes, open interest). Settlement files historically free; deep history paid. Because settlements derive from Baltic indices, redistribution may be restricted even if viewing is free — **read the ToS.** [MED] | **USABLE WITH EFFORT** — verify first |
| **EEX** (`eex.com`, freight desk, ex-Cleartrade) | Freight derivatives on Cape/Panamax/Supramax/Handysize TC routes + iron ore + coal. EEX generally publishes **free end-of-day settlement prices** across its markets with paid historical archives. [MED] | **USABLE WITH EFFORT** |
| **Real-time / delayed free feed** | **Does not exist for FFAs.** No free streaming or delayed API from either venue. The realistic free artefact is the **daily end-of-day settlement file.** [HIGH] | No free feed |
| **BDRY daily holdings** | See §1(a) — potentially the best free view of actual FFA marks. [MED] | **Verify — high payoff** |
| **Broker free reports** | **FIS (Freight Investor Services)**, **Braemar**, **SSY**, **Arrow**, **Clarksons Platou** all publish **free daily/weekly FFA market reports** (PDF/email newsletter) containing forward curve levels by quarter/calendar year. Free signup. Genuinely free, genuinely current, and *intended* for public circulation. **Underrated — sign up on day one.** [MED–HIGH] | **USABLE NOW** |

**Practical FFA plan:** subscribe to 2–3 broker newsletters, parse the curve levels into a small CSV daily, cross-check against BDRY. You will have a real (if manually seeded) forward curve within a week.

---

## 3. AIS VESSEL TRACKING

**Headline honesty on your geography:** *no free source provides reliable open-ocean AIS for the Indian Ocean / Bay of Bengal.* Open-ocean coverage needs **satellite** AIS, which is exclusively commercial (Spire, ORBCOMM, exactEarth/Kpler). Free/crowdsourced terrestrial AIS gives you **coastal and near-port coverage** — receivers exist around Chennai, Vizag, Kolkata, Colombo, Singapore. [HIGH]

So: **port arrival/departure/berth-time detection = feasible free. Mid-voyage ocean tracking = not feasible free.** Design your architecture around that constraint — and use **IMF PortWatch (§6)** as your free satellite-AIS-derived substitute.

| Source | Auth / cost | Coverage | Verdict |
|---|---|---|---|
| **aisstream.io** | **Free WebSocket, free signup for API key.** JSON messages (position + static). Non-commercial free tier. [MED–HIGH] | Global crowdsourced; decent near Indian ports, sparse offshore | **USABLE NOW** — primary live feed |
| **AISHub** (`aishub.net`) | Free **but you must contribute your own AIS receiver feed to gain access.** That means buying/running an AIS dongle + antenna. Real blocker. [HIGH] | Global crowdsourced | **USABLE WITH EFFORT** (needs hardware) |
| **Digitraffic** (Fintraffic, Finland) | Free, no key, REST + MQTT. CC BY 4.0. [HIGH] | Finnish waters only | Wrong geography — **excellent for pipeline dev/testing** |
| **Kystverket / BarentsWatch** (Norway) | Free open AIS, registration for some feeds. [MED] | Norwegian waters | Wrong geography |
| **Danish Maritime Authority** (`web.ais.dk` / dma.dk) | **Free bulk historical AIS downloads, no auth, open licence.** Massive daily CSVs, years of history. [HIGH] | Danish waters | **USABLE NOW** — best free AIS *training* corpus |
| **MarineCadastre.gov** (NOAA/BOEM) | **Free historical US AIS**, zipped CSV by day, 2009→present, public domain, no auth. Includes MMSI, IMO, name, **length, width, draft, vessel type**. [HIGH] | US EEZ | **USABLE NOW** — best free labelled AIS dataset, and a free vessel-particulars source (see §12) |
| **Global Fishing Watch** (`globalfishingwatch.org/our-apis`) | **Free API, free token via registration.** Not just fishing — has a **vessels** endpoint and an **events** endpoint (port visits, loitering, encounters, gaps) with **global coverage including the Indian Ocean.** CC BY-NC-style terms + attribution. [MED–HIGH] | Global, satellite-derived | **USABLE NOW** — free port-visit events for Indian ports |
| **Spire** | Commercial. Has a research/academic programme worth an email. [MED] | Global satellite | Paid |
| **MarineTraffic** | API is expensive (per-credit). Free website view; **port pages carry useful free port infrastructure info** (berths, drafts) for §7–8. Scraping breaches ToS. [HIGH] | Global | **PAYWALLED** for API; free reference pages |
| **VesselFinder** | Same shape as MarineTraffic. [HIGH] | Global | **PAYWALLED** for API |

---

## 4. BUNKER / FUEL PRICES

| Source | Detail | Verdict |
|---|---|---|
| **EIA API** (`api.eia.gov/v2`) | **Free API key, generous limits, public domain.** Brent, WTI, residual fuel oil, distillates, NY Harbor ULSD. Daily/weekly/monthly, decades of history. JSON/CSV. [HIGH] | **USABLE NOW** — your reliable fuel backbone |
| **Ship & Bunker** (`shipandbunker.com`) | **Free daily VLSFO / MGO / IFO380 prices by port** (~20 ports incl. Singapore, Fujairah, Rotterdam, Houston) plus "Global 20" averages. Free to view, **no API**, ToS forbids scraping/redistribution; deep history gated. [MED–HIGH] | **USABLE WITH EFFORT** — grey if automated |
| **Bunker Index** (`bunkerindex.com`) | Free daily BIX index values with historical pages. No API. [MED] | Free view |
| **Bunkerworld** (Integr8/Platts) | Paywalled; free limited index glance. [MED] | **PAYWALLED** |
| **Singapore MPA** | Publishes **monthly bunker sales volumes** free (official XLS) — **volumes, not prices.** Still valuable: Singapore is the benchmark bunkering port and volume is a demand signal. [HIGH] | **USABLE NOW** (volumes only) |
| **World Bank Pink Sheet** | Monthly Brent/Dubai/WTI + coal + gas, free XLSX, CC BY 4.0. [HIGH] | **USABLE NOW** (monthly) |
| **CME free delayed settlements** | CME lists **Singapore Marine Fuel 0.5% (Platts)** and **Singapore Fuel Oil 380cst** futures, and publishes **free delayed daily settlement prices** on cmegroup.com. This is a legitimate, free, daily **VLSFO** series. [MED — contract codes **[LOW]**] | **USABLE WITH EFFORT** — verify |
| **EU MRV / EMSA THETIS-MRV** (`mrv.emsa.europa.eu`) | **Free bulk XLSX** of annual fuel consumption, CO2, distance and time-at-sea **per individual ship** >5000 GT calling at EU ports. Free, no auth. [MED–HIGH] | **USABLE NOW** — free per-ship *consumption* data for bunker cost modelling. Underrated. |

**Recommended:** model VLSFO as `Brent (EIA, free) + port-specific spread`, where the spread is calibrated once from a Ship & Bunker snapshot and refreshed manually. Defensible, free, and honest.

---

## 5. COMMODITY PRICES

| Source | Detail | Verdict |
|---|---|---|
| **World Bank "Pink Sheet"** (`worldbank.org/en/research/commodity-markets`) | **The best free commodity dataset for this project.** Monthly XLSX: **Coal Australia (FOB Newcastle), Coal South Africa (FOB Richards Bay), Iron ore (CFR China 62% Fe)**, crude (Brent/Dubai/WTI), wheat, maize, soybeans, rice, fertilisers. Long monthly history. **CC BY 4.0 — redistributable.** No auth. [HIGH] | **USABLE NOW — top tier** |
| **IMF Primary Commodity Prices (PCPS)** | Free monthly XLSX + SDMX API. Coal, iron ore, crude, grains. Note: IMF migrated data portals in 2024–25, so the **legacy `dataservices.imf.org` SDMX endpoint may be deprecated** — verify. [MED] | **USABLE NOW** (XLSX certain) |
| **SGX iron ore 62% Fe futures** | Free daily settlement prices on sgx.com; the global benchmark. [MED] | **USABLE WITH EFFORT** |
| **ICE Newcastle coal futures (NCF)** | The global thermal coal benchmark. ICE free delayed data is patchy; **free-to-view on Investing.com / Barchart.** [MED] | Free view |
| **CME API2 / API4 coal futures** | Free delayed settlements → enables the **API2−API4 freight proxy** (§1d). Verify codes. [MED] | **USABLE WITH EFFORT** |
| **globalCOAL NEWC index** | Membership required for full data; weekly NEWC headline sometimes shown free. [MED] | Mostly **PAYWALLED** |
| **Dalian (DCE) iron ore** | Free-ish via Chinese sites / Investing.com. [MED] | Free view |
| **India — Ministry of Coal** (`coal.gov.in`) | Free monthly production, dispatch, import statistics. [HIGH] | **USABLE NOW** |
| **India — Coal India Ltd** (`coalindia.in`) | Free monthly production/offtake, **notified prices**, e-auction results. [MED–HIGH] | **USABLE NOW** |
| **India — CEA daily coal stock report** (`cea.nic.in`) | **⭐ Killer free Indian signal.** Daily report of coal stock (tonnes and **days of stock**) at ~180 thermal power plants, **split domestic vs imported**, per plant. Free PDF/XLS, daily. When plant stocks fall below critical, import demand and east-coast port throughput spike. **This is your best free leading indicator for Indian dry bulk import demand — nobody else in the hackathon will have it.** [MED–HIGH] | **USABLE NOW — strongly recommended** |
| **India — Steel (JPC / Ministry of Steel)** | Monthly JPC data partly paid; ministry press releases free. **SteelMint/BigMint** paywalled with free headline news. [MED] | Mixed |
| **Global Energy Monitor** | Free CC BY 4.0 **Global Coal Plant Tracker** — every Indian coal plant with capacity, status, coordinates. Lets you map plant → nearest import port. [MED–HIGH] | **USABLE NOW** |
| **data.gov.in** | Free API (free key), coal/steel/port datasets, GODL-India licence, JSON/CSV. [HIGH] | **USABLE NOW** |

---

## 6. PORT CONGESTION / PORT CALLS

### ⭐ IMF PortWatch — investigate this first, it is your backbone

`portwatch.imf.org` [MED–HIGH on all specifics below — **verify before building**]

- **Provider:** IMF, built with the **UN Global Platform**, using **satellite AIS** and the methodology of Cerdeiro, Komaromi, Liu & Saeed (2020).
- **What it gives:** **daily** port call counts and **estimated import/export trade volumes** for **~1,400+ ports** worldwide, plus ~30–100 **maritime chokepoints** (Suez, Panama, Bab el-Mandeb, Hormuz, Malacca, Gibraltar).
- **History:** from **1 January 2019** to near-present, updated daily with a few days' lag.
- **Auth:** **none.** Free, open.
- **Access:** the site is hosted on **Esri ArcGIS Online**, which means alongside the CSV download buttons there are **ArcGIS REST FeatureServer `/query` endpoints returning JSON / GeoJSON / CSV** — fully scriptable, paginated, filterable by `portid` and date. **I cannot give you the exact service URL — find it via the browser network tab or the ArcGIS Online item page. Do not let anyone put a guessed endpoint in the codebase.**
- **Fields (recalled, verify):** `portid`, `portname`, `country`, `ISO3`, `date`, `import`, `export`, and vessel-class breakdowns along the lines of `portcalls`, `portcalls_cargo`, `portcalls_tanker`, `portcalls_container`, `portcalls_dry_bulk`, `portcalls_general_cargo`, `portcalls_roro`. **The dry-bulk-specific breakdown is the reason this source matters to you** — verify it exists.
- **Indian East Coast coverage:** I believe most Indian major ports are included (Paradip, Visakhapatnam, Chennai, Ennore/Kamarajar, Kakinada, Krishnapatnam, Tuticorin, Haldia/Kolkata). **Adani private ports (Gangavaram, Dhamra, Gopalpur) are less certain.** This is verification priority #1 in task #8 — if your target ports aren't in the layer, a big chunk of your design changes.
- **Licence:** IMF open data terms — free reuse with attribution, generally fine for a hackathon and for non-commercial publication.
- **Verdict: USABLE NOW — the single most important free source for this project.** It substitutes for paid AIS, gives you congestion *and* trade volume, daily, per port, for free.

### Other port sources

| Source | Detail | Verdict |
|---|---|---|
| **Indian Ports Association** (`ipa.nic.in`) | **⭐ Free monthly + annual statistics for all Major Ports:** commodity-wise and port-wise traffic, and crucially **operational efficiency metrics — average turnaround time, pre-berthing detention, output per ship-berth-day, idle time as % of time at berth.** PDF/XLS. **This is a real, official, free congestion dataset with years of history — and it is India-specific, which judges will care about.** [HIGH] | **USABLE NOW — top tier** |
| **Port daily vessel-position reports** | Several Indian port authorities (Paradip, Visakhapatnam, others) publish **daily "vessel position" / berth occupancy PDFs** listing vessels at berth, at anchorage, expected arrivals, cargo and tonnage. Free, daily, granular. Requires per-port scraping. [MED] | **USABLE WITH EFFORT — very high value** |
| **data.gov.in** | Free API (free key) with datasets on major port traffic, turnaround time, capacity utilisation. GODL-India. [HIGH] | **USABLE NOW** |
| **MoPSW** (`shipmin.gov.in`) | Annual reports, monthly traffic press releases, policy. Free. [HIGH] | **USABLE NOW** |
| **Sagarmala** (`sagarmala.gov.in`) | Project pipeline, planned capacity, port connectivity. Free. [MED–HIGH] | **USABLE NOW** |
| **PMIS / Sagar Setu / NLP-Marine** | MoPSW digital platforms. Public dashboards exist but I cannot confirm any open API or bulk export. [LOW] | **Unverified** |
| **UNCTADstat port call statistics** | Free dataset (derived from MarineTraffic): **median time in port, arrivals, average vessel size/age by port and country**, quarterly. Good cross-check on IPA turnaround figures. [MED–HIGH] | **USABLE NOW** |
| **PIB** (`pib.gov.in`) | Free press releases + RSS — MoPSW port traffic records, capacity announcements. [HIGH] | **USABLE NOW** |

---

## 7. INDIAN EAST COAST PORT INFRASTRUCTURE

### 🚨 Every number below is model knowledge, NOT a verified citation

The user asked for actual numbers with citations. **I cannot provide citations — I had no web access.** What follows is my best recollection, offered as a **starting hypothesis to check**, with the authoritative source to check it against. **Do not hard-code these or put them in a deck before verification.** Drafts in particular change with dredging campaigns and are the kind of detail a shipping-industry judge will catch instantly.

| Port | Operator | Max draft (m) — **UNVERIFIED** | Class capability | Notes |
|---|---|---|---|---|
| **Paradip** | Paradip Port Authority | ~17–18 at deep berths | Capesize | Deepest *major* (public) port on the east coast; iron ore + coal + POL |
| **Visakhapatnam (Vizag)** | VPA | Outer Harbour ~17–18; Inner Harbour ~10–13 | Cape (OH) / Panamax–Handy (IH) | Two-harbour structure is a modelling must — **do not treat Vizag as one draft** |
| **Gangavaram** | Adani (acquired 2021) | ~21 — deepest in India | Cape / VLOC to ~200k DWT | Adjacent to Vizag; private, high productivity |
| **Dhamra** | Adani Dhamra | ~18–19 | Capesize | Odisha; coal + limestone |
| **Gopalpur** | Adani (acquired 2024, ex-Shapoorji) | Uncertain — possibly ~12–14 | Panamax? | **[LOW] — verify carefully**, historically lighterage-oriented |
| **Krishnapatnam** | Adani Krishnapatnam | ~18–18.5 | Capesize | Andhra Pradesh; deep, high productivity |
| **Kakinada** | Kakinada Seaports (deep water) + Anchorage Port | Deep Water ~13; Anchorage shallow | Panamax / small | **Two distinct ports, often conflated — model separately** |
| **Kamarajar (Ennore)** | Kamarajar Port Ltd | ~13.5–16 | Panamax → Cape at newer berths | Purpose-built coal port for Tamil Nadu power |
| **Chennai** | Chennai Port Authority | ~15.5–16.5 | Cape-capable physically | **⚠️ Critical domain fact: Chennai phased out coal and iron ore handling (c. 2018–19) on environmental grounds, shifting dry bulk to Kamarajar/Ennore. Physical draft is irrelevant if the cargo is banned. Verify current status — this kind of nuance wins hackathons.** [MED–HIGH] |
| **V.O. Chidambaranar (Tuticorin)** | VOC Port Authority | ~14.2 after deepening | Panamax | Coal for southern TN |
| **Haldia (HDC)** | Syama Prasad Mookerjee Port, Kolkata | **~8.0–8.5** | Handysize / part-laden Supramax | **Severely draft- and tide-limited**, Hooghly river, continuous dredging |
| **Kolkata Dock System** | SMP Kolkata | **~7.0** | Small vessels only, lock-gated | Very restricted; LOA-limited |
| **Sandheads / Sagar Roads** | SMP Kolkata anchorage | Effectively unlimited at anchorage | Cape part-discharge via lighterage | **Key insight: Capesize/Panamax cargoes for Kolkata–Haldia are part-discharged into barges at Sandheads/Sagar. Any east-coast chartering model must handle lighterage cost + time, not just berth draft.** [HIGH conceptually] |
| **Karaikal** | Karaikal Port (Puducherry) | ~14 | Panamax | Coal |

**Where to verify each (these are the authoritative free sources):**
1. Each port authority's own **"Port Information Guide" / "Marine Services" / "Port Facilities"** page or PDF — the legally operative figure is the Harbour Master's **declared maximum permissible draft**, which is published and often updated by circular.
2. **IPA "Port Profiles"** — consolidated berth-by-berth specs for all Major Ports.
3. **NGA World Port Index** (see §9) — free machine-readable baseline for all of them at once, though coarse and sometimes stale.
4. MarineTraffic / VesselFinder port pages — free reference, useful cross-check, not authoritative.

**Recommended approach:** ingest **NGA WPI** as the machine-readable base layer for all ports globally, then hand-override the ~13 East Coast ports with figures read off official Port Information Guides. Store `source_url` and `as_of_date` per field — judges respect provenance, and it protects you from exactly the error this report cannot rule out.

---

## 8. LOADING PORT INFRASTRUCTURE

### 🚨 Same caveat — all figures are UNVERIFIED model knowledge

| Region | Port / Terminal | Max draft (m) — **UNVERIFIED** | Notes |
|---|---|---|---|
| **Australia** | **Newcastle** (PWCS Carrington + Kooragang, NCIG) | ~16.5–16.6 sailing | World's largest coal export port; Cape but not fully laden |
| | **Hay Point** (Hay Point CT + Dalrymple Bay CT) | ~18–19.5, tide-assisted | Premium coking coal for steel |
| | **Gladstone** (RG Tanna, WICET) | ~17–18 | Thermal + coking |
| | **Abbot Point** (North Queensland Export Terminal) | ~15.5–16.5 | Coking coal |
| | **Port Hedland** | ~19.5 on tide | Iron ore (BHP/FMG/Roy Hill); **strongly tide-dependent — sailing windows matter** |
| | **Dampier** (East Intercourse Is., Parker Point) | ~19 | Rio Tinto iron ore |
| **Indonesia** | **Samarinda / Mahakam River** | River-limited, small | Barge loading |
| | **Taboneo** (Banjarmasin anchorage) | Anchorage ~15–20 | **Floating-crane transhipment** |
| | **Muara Berau / Muara Pantai** (anchorages) | Anchorage ~15–20 | **Floating-crane transhipment** |
| | **Balikpapan** | Anchorage transhipment | |
| | ⚠️ **Key domain insight:** Indonesian coal exports are largely **anchorage-based floating-crane / barge transhipment, not berths.** "Max draft" is nearly meaningless; the binding constraints are **anchorage depth, floating crane availability, barge supply, and monsoon/weather downtime.** Model Indonesian load ports differently from berth ports — this is a genuine sophistication signal. [HIGH conceptually] |
| **Mozambique** | **Nacala** | ~14+ (deep natural harbour) | Cape-capable; Vale/Nacala Logistics Corridor coal |
| | **Maputo** | ~11–12 post-dredging | Panamax; coal, chrome, ferro |
| | **Beira** | ~8–12, shallow, dredging-dependent | Handy/Supra only |
| **USA** | **Hampton Roads / Norfolk** (Lamberts Point Pier 6, Dominion Terminal, Kinder Morgan Pier IX) | ~15.2 (50 ft channel) | Largest US coal export complex; Cape |
| | **Baltimore** (CNX/Consol Marine Terminal) | ~15.2 (50 ft) | ⚠️ Key Bridge collapse (Mar 2024) disrupted access; channel since restored — **verify current status** |
| | **New Orleans / Lower Mississippi** | ~13.7–15.2 (45–50 ft) | Grain + coal; **topping-off at anchorage is standard practice** |
| | **Mobile, AL** (McDuffie Coal Terminal) | ~13.7 (45 ft) | Coal |
| **Russia** | **Vostochny / Nakhodka** | ~16.5–18 | Far East coal to Asia incl. India; Cape |
| | **Murmansk** | ~15.5 | Ice-free year-round; Cape |
| | **Taman** (OTEKO, Black Sea) | ~16–18 | Coal; Cape |
| | **Ust-Luga** (Baltic) | ~15 | Panamax/post-Panamax coal |
| | ⚠️ **Modelling note:** Russian coal to India is real and material, but carries **sanctions, insurance, payment-channel and freight-premium** complications. Treat "Russian origin" as a **risk/premium feature**, not just a distance. Judges will notice if you do — and notice if you don't. |

**Free, authoritative verification sources (these genuinely exist and are free) [MED–HIGH]:**
- **Pilbara Ports Authority** — free Port Handbooks + daily ship movement reports for Port Hedland and Dampier
- **Port of Newcastle** — free port handbook / vessel specification pages; **PWCS and NCIG** publish free terminal specs and vessel nomination rules
- **Gladstone Ports Corporation** — free port handbook
- **DBCT (Dalrymple Bay)** — free terminal handbook / operations manual
- **NQXT (Abbot Point)** — free terminal specs
- **US Army Corps of Engineers** — free authoritative channel depths for all US ports
- **NGA World Port Index** — free bulk baseline for every port above

---

## 9. SEA DISTANCES & ROUTING — strong free options, great graph-AI angle

This category is genuinely well served for free, and it is where your "graph AI" narrative can be technically real rather than decorative.

| Source | Detail | Verdict |
|---|---|---|
| **`searoute` (PyPI)** | **Free, permissive licence, works fully offline.** Give it two lat/lon points, get **distance + route LineString geometry** avoiding land, with Suez/Panama options. Also a JS port. Built on a marine network derived from Eurostat's MARNET. [MED–HIGH] | **USABLE NOW — top pick** |
| **`scgraph` (PyPI)** | Supply-chain graph library bundling **Marnet and SeaRoute geographs with Dijkstra/A\* shortest-path** over the marine network. Exposes the **actual node/edge graph**, which is what you want for a custom cost function. [MED — verify package name/API] | **USABLE NOW if it checks out — best fit for graph-AI** |
| **Eurostat / JRC MARNET** (GISCO, e.g. `marnet_densified_v2` GeoJSON) | **The routable marine network graph itself** — nodes + edges, free, downloadable. Load into `networkx`, attach edge weights (distance, weather penalty, piracy risk, canal fees, ECA zones), run Dijkstra/A\*. **This is the honest technical core of a graph-AI routing story.** [MED–HIGH] | **USABLE NOW — top pick** |
| **GEBCO bathymetry** (`gebco.net`, GEBCO_2024) | Free global bathymetric grid, NetCDF/GeoTIFF, no auth. Use to build your own navigable raster with a **draft-feasibility mask** (vessel draft + UKC vs charted depth) then graph it. Large files. [HIGH] | **USABLE NOW** |
| **Natural Earth** | Free public-domain coastlines/land polygons — essential for land-masking. [HIGH] | **USABLE NOW** |
| **Global shipping traffic density raster** (Cerdeiro/Komaromi/Liu/Saeed — IMF/World Bank data catalog) | Free global AIS-derived traffic density grid + port-to-port trade matrices. **Same team as PortWatch.** Use to weight your graph edges toward *actually used* lanes rather than geodesics — a nice, defensible refinement. [MED] | **USABLE NOW** |
| **UN/LOCODE** (UNECE) | Free CSV of port codes (e.g. INPRT, INVTZ). **Your essential join key across every other dataset.** [HIGH] | **USABLE NOW** |
| **NGA World Port Index** (`msi.nga.mil`) | **⭐ Free, public domain, no auth.** ~3,700 ports with **max draft/depth ranges, anchorage depth, cargo pier depth, harbour type, available services, coordinates.** CSV/shapefile/GeoJSON. Coarse and sometimes stale — use as base layer, override for your key ports. [MED–HIGH] | **USABLE NOW — top pick for §7/§8 baseline** |
| **searoutes.com** | Commercial API with a limited free tier (API key). [LOW on free-tier terms] | Verify |
| **sea-distances.org** | Free manual web lookup, no API, ToS restricts scraping. **Best used to QA your Dijkstra output against industry-accepted distances** — a great validation slide. [MED–HIGH] | **USABLE (manual QA)** |
| **Netpas Distance** | Paid desktop; industry standard. [HIGH] | **PAYWALLED** |
| **AtoBviaC** | Paid; industry-standard distance tables. [HIGH] | **PAYWALLED** |

**Recommended routing build:** MARNET GeoJSON → `networkx` graph → edge weights = `f(distance, wave height from Open-Meteo, cyclone proximity from IBTrACS, canal transit cost, ECA fuel penalty, piracy zone)` → A\* → validate a dozen real routes (Newcastle→Paradip, Richards Bay→Vizag, Taboneo→Ennore) against sea-distances.org. **Free, real, and genuinely a graph algorithm.**

---

## 10. MARINE WEATHER — excellent free coverage

| Source | Detail | Verdict |
|---|---|---|
| **Open-Meteo Marine API** (`marine-api.open-meteo.com/v1/marine`) | **Free, NO API KEY.** Wave height/direction/period, wind wave, swell. Companion forecast API for wind/precip; **archive API** (`archive-api.open-meteo.com`) with ERA5 reanalysis back to 1940. Free tier ~10k calls/day, non-commercial. **CC BY 4.0.** [HIGH — though whether a *marine historical* archive endpoint exists separately is **[MED]**] | **USABLE NOW — top pick** |
| **NOAA NOMADS — GFS + WaveWatch III** (`nomads.ncep.noaa.gov`) | Free GRIB2, no auth, **public domain** (fully redistributable). Global wave + wind forecasts. Heavy; consider NOAA **ERDDAP** servers for easier subsetting. [HIGH] | **USABLE NOW** |
| **Copernicus Marine Service (CMEMS)** | **Free registration.** Global waves, currents, analysis+forecast and multi-decade reanalysis. NetCDF via the `copernicusmarine` Python toolbox. Attribution licence. [HIGH] | **USABLE NOW** |
| **Copernicus CDS / ERA5** | Free registration, CDS API, global wind/wave reanalysis, decades. [HIGH] | **USABLE NOW** |
| **ECMWF Open Data** | **Free real-time forecasts, no auth**, 0.25°, via `ecmwf-opendata` Python client. CC BY 4.0. [MED–HIGH] | **USABLE NOW** |
| **IBTrACS** (NOAA NCEI) | **⭐ Free, no auth, public domain.** Global historical tropical cyclone tracks, CSV/NetCDF/shapefile. **Filter to North Indian Ocean for Bay of Bengal cyclone risk features.** [HIGH] | **USABLE NOW — top pick** |
| **IMD / RSMC New Delhi** (`mausam.imd.gov.in`, `rsmcnewdelhi.imd.gov.in`) | Free cyclone bulletins + **North Indian Ocean best-track archive** (text/PDF/XLS). India-specific credibility. [MED–HIGH] | **USABLE NOW** |
| **JTWC** | Free best-track and warning archive, US public domain. [HIGH] | **USABLE NOW** |
| **INCOIS** (`incois.gov.in`) | Indian National Centre for Ocean Information Services — free ocean state / wave forecasts for Indian seas. India-specific. [MED] | **USABLE NOW** |

**Domain note worth building in:** the Bay of Bengal has two cyclone seasons (**Apr–Jun** and **Oct–Dec**, the latter more severe), and the **southwest monsoon (Jun–Sep)** materially affects east-coast port operations and Indonesian barge loading. Seasonality is a free, real, high-signal feature — IBTrACS gives you 100+ years of it.

---

## 11. MACRO / ECONOMIC INDICATORS

| Source | Detail | Verdict |
|---|---|---|
| **FRED API** (`api.stlouisfed.org/fred`) | **Free API key**, 800k+ series, JSON/XML, excellent Python clients. Industrial production, FX, PPIs, commodity indices, EIA energy. **No BDI.** Some series carry source redistribution limits. [HIGH] | **USABLE NOW** |
| **World Bank API** (`api.worldbank.org/v2`) | **Free, no key**, JSON/XML/CSV, CC BY 4.0. Mostly annual. [HIGH] | **USABLE NOW** |
| **IMF** | Free XLSX + SDMX. **Portal migrated 2024–25 — legacy `dataservices.imf.org` endpoint may be dead.** IFS, DOTS (bilateral trade), PCPS (commodities). [MED] | **USABLE — verify endpoint** |
| **OECD** | Free SDMX API, no key. [MED–HIGH] | **USABLE NOW** |
| **China — NBS** (`stats.gov.cn`) | Free monthly crude steel output, iron ore imports, official PMI. Awkward HTML, some Chinese-only. [MED–HIGH] | **USABLE WITH EFFORT** |
| **China — customs** (`customs.gov.cn`) | Free monthly import volumes (iron ore, coal by origin). Awkward. [MED] | **USABLE WITH EFFORT** |
| **China steel PMI** | Official NBS manufacturing PMI free; **CFLP/CSLPC steel PMI** headline free via press release; Caixin headline free. Full sub-indices often paid. [MED] | Headline free |
| **RBI — DBIE** (`dbie.rbi.org.in`) | Free Indian macro, FX, trade. [HIGH] | **USABLE NOW** |
| **India — tradestat / DGCI&S** (`tradestat.commerce.gov.in`) | **Free** monthly India import/export by **HS code and partner country** — get HS 2701 (coal), 2601 (iron ore), 7204 (scrap) volumes by origin. **HTML query forms, no official API** — scrapeable with effort. [MED–HIGH] | **USABLE WITH EFFORT — high value** |
| **DGFT** (`dgft.gov.in`) | Policy, notifications, import restrictions. Free. [HIGH] | Reference |
| **UN Comtrade** (`comtradeapi.un.org`) | **Free tier requires a free API key**; low daily call and record caps; **bulk downloads are premium.** Monthly HS-6 bilateral trade. [MED–HIGH] | **USABLE WITH EFFORT** (tight limits) |
| **data.gov.in** | Free API + key; Indian trade, port, coal datasets; GODL-India. [HIGH] | **USABLE NOW** |

---

## 12. VESSEL PARTICULARS (IMO, DWT, dimensions)

**The paid incumbents:** Clarksons World Fleet Register, S&P Global Sea-web, Lloyd's Register — all **PAYWALLED**, all expensive. [HIGH]

**Free routes that actually work:**

| Source | Detail | Verdict |
|---|---|---|
| **AIS static messages (Type 5) — via MarineCadastre / Danish AIS / aisstream** | **⭐ The best free path to a bulk vessel-particulars database.** AIS static data carries **name, callsign, IMO, MMSI, ship type code, length, beam, and reported draught.** MarineCadastre CSVs ship with `Length`, `Width`, `Draft`, `VesselType` columns already parsed. From L×B×T you can **estimate DWT** with a block-coefficient regression — calibrate on a few hundred known ships and you have a free, self-built fleet database. Public domain (US) / open (DK). [MED–HIGH] | **USABLE NOW — recommended** |
| **Equasis** (`equasis.org`) | **Free registration.** Per-vessel: IMO, name, flag, type, GT, DWT, year built, class society, ISM manager, registered owner, **port state control inspection history** (a genuine risk signal). **No API, no bulk export; ToS forbids automated harvesting.** Manual lookup of a few hundred ships is legitimate. [HIGH] | **USABLE WITH EFFORT** (manual only) |
| **IMO GISIS** (`gisis.imo.org`) | **Free registration.** Ship and company particulars, casualties, port reception facilities. No bulk API; same automation caveat. [HIGH] | **USABLE WITH EFFORT** |
| **ITU MARS** (`maritime.itu.int`) | Free MMSI ↔ callsign ↔ IMO ↔ name lookup; some bulk. Useful **identity reconciliation** across AIS feeds. [MED] | **USABLE NOW** |
| **Global Fishing Watch vessel API** | Free token; includes non-fishing **carrier/cargo** vessel identity records. Attribution + non-commercial terms. [MED] | **USABLE NOW** |
| **EU MRV / EMSA THETIS-MRV** | **⭐ Free bulk XLSX, no auth**: per-ship annual **fuel consumption, CO2, distance travelled, hours at sea, technical efficiency (EEDI/EIV)** for ships >5000 GT calling at EU ports. Includes IMO + ship type. **Real per-ship consumption data — gold for bunker cost and voyage P&L modelling, and there is no paid equivalent you'd need.** [MED–HIGH] | **USABLE NOW — underrated** |
| **UNCTADstat fleet statistics** | Free aggregate fleet by type/flag/age. No vessel-level. [HIGH] | Context only |

---

## 13. NEWS / EVENT SIGNALS

### ⭐ GDELT — investigate properly, it is the right answer here

`gdeltproject.org` [MED–HIGH]

**Free, no authentication, global, enormous.** Three access modes:

1. **GDELT DOC 2.0 API** — `api.gdeltproject.org/api/v2/doc/doc` (URL pattern recalled; verify). Full-text search over global online news covering roughly a rolling 3-month window, returning **JSON/CSV**. Critically it supports **timeline modes** (`TimelineVol`, `TimelineVolRaw`, `TimelineTone`, `TimelineSourceCountry`) which return a **ready-made time series of article volume and sentiment tone** for any query. Query `"Paradip port" OR "Visakhapatnam coal"` and you get a congestion/disruption signal for free, no ML required.
2. **Raw 15-minute CSV files** — `data.gdeltproject.org/gdeltv2/lastupdate.txt` points at the latest Events / Mentions / GKG zips. **Full history: Events back to 1979 (v1), GDELT 2.0 from Feb 2015.** Includes **CAMEO event codes** (PROTEST, STRIKE, EMBARGO, ASSAULT) and **geolocation** — so you can extract "labour action at an Indian port" as a structured, dated, geocoded event series going back years.
3. **Google BigQuery public dataset** — queryable within BigQuery's **free 1 TB/month** tier.

**Licence:** GDELT is explicitly free for any use with attribution (much of it CC BY 4.0). **This is the rare case where the free option is also the best option.** **Verdict: USABLE NOW — top pick for a risk agent.**

### Other news sources

| Source | Detail | Verdict |
|---|---|---|
| **RSS: Splash247, Hellenic Shipping News, Maritime Executive, gCaptain, Offshore Energy, Riviera, Seatrade** | Free RSS, no auth. **Hellenic Shipping News is doubly valuable — it republishes the daily Baltic dry bulk report (see §1).** Headlines/snippets only; don't redistribute full text. [HIGH] | **USABLE NOW** |
| **TradeWinds, Lloyd's List** | **Hard paywalls.** RSS gives titles only. Do not plan on their content. [HIGH] | **PAYWALLED** |
| **NewsAPI.org** | Free tier ~100 req/day, **24h delayed**, and explicitly **"development use only."** ⚠️ **A public hackathon demo arguably breaches that clause.** Honest flag — use GDELT instead. [MED–HIGH] | Licence trap |
| **GNews / NewsData.io / Mediastack** | Small free tiers, similar restrictions. [MED] | Marginal |
| **Google News RSS** (`news.google.com/rss/search?q=`) | Free, works, unofficial, grey ToS. [MED] | Grey fallback |
| **PIB** (`pib.gov.in`) | Free official Indian govt press releases + RSS — MoPSW, ports, coal. Clean licence, India-specific. [HIGH] | **USABLE NOW** |

---

## DAY ONE DATA STACK

The minimal set of **genuinely free, clean-licence** sources that gets you to something real. Ordered by build sequence.

### Tier 1 — build on these immediately (free, no/easy auth, clean licence)

| # | Source | Gives you | Auth |
|---|---|---|---|
| 1 | **IMF PortWatch** | Daily port calls + trade volume estimates, ~1,400 ports, 2019→now, dry-bulk breakdown | None |
| 2 | **Indian Ports Association** | Monthly Indian port traffic **+ turnaround time / pre-berthing detention** | None |
| 3 | **CEA daily coal stock report** | Daily coal stock (days of cover) at ~180 Indian power plants, domestic vs imported | None |
| 4 | **World Bank Pink Sheet** | Monthly coal (Newcastle FOB, Richards Bay FOB), iron ore CFR China, crude — CC BY 4.0 | None |
| 5 | **EIA API** | Daily/weekly Brent + fuel products, public domain | Free key |
| 6 | **Open-Meteo Marine + Archive** | Free wave/wind forecast + ERA5 history, no key, CC BY 4.0 | None |
| 7 | **IBTrACS** | Historical cyclone tracks for Bay of Bengal risk | None |
| 8 | **GDELT DOC 2.0 API** | News volume/tone time series per port, event codes, free | None |
| 9 | **NGA World Port Index** | Machine-readable port specs (draft, depths, services) for every port worldwide | None |
| 10 | **MARNET GeoJSON + `searoute`/`scgraph`** | Routable marine graph → your own Dijkstra/A\* sea routing | None |
| 11 | **UN/LOCODE** | The join key across all of the above | None |
| 12 | **`yfinance`: BDRY, SBLK, GNK, GOGL, DSX** | Daily dry-bulk freight-linked price series | None |
| 13 | **SEC EDGAR API** | Official quarterly **TCE by vessel class**, 10–15 yrs — your ground truth | None (UA header) |

### Tier 2 — add in week two (needs effort or registration)

Global Fishing Watch API (free token, port-visit events) · aisstream.io (free key, live coastal AIS) · MarineCadastre + Danish AIS bulk (free AIS training corpus + vessel dimensions) · EU MRV THETIS (per-ship fuel consumption) · Copernicus Marine (free registration, waves/currents) · SGX + EEX freight settlement pages (verify free) · FIS/Braemar/SSY free FFA newsletters · tradestat.commerce.gov.in (India coal imports by origin) · UN Comtrade (free key) · Equasis manual lookups for your vessel shortlist · Indian port daily vessel-position PDFs · Global Energy Monitor coal plant tracker · data.gov.in API

### Tier 3 — explicitly do NOT plan around these

Baltic Exchange route assessments (C3/C5/C10_14/P2A/P6/S1B/S10) · Clarksons SIN · Platts/S&P · Argus · Drewry dry bulk · MarineTraffic/VesselFinder/Spire APIs · Netpas · AtoBviaC · IHS Sea-web · World Fleet Register. **All paywalled. The one exception worth ten minutes: ask your university library whether it holds Clarksons SIN or Sea-web institutional access. That is the only realistic free door to real Baltic-grade data, and it costs you an email.**

---

## WHAT MUST BE SYNTHESISED, AND HOW TO DO IT CREDIBLY

You will not have a licensed daily Baltic route rate series. So **be explicit and proud about it** rather than hiding it — judges punish fake precision far harder than they punish an honest, well-calibrated simulator.

**1. Synthetic daily freight rate series per route.**
Model log-rate as a **mean-reverting Ornstein–Uhlenbeck process with jumps and seasonality**:

`d ln(R_t) = κ(θ_t − ln R_t)dt + σ dW_t + J dN_t`

Calibrate each parameter to a **free, citable** anchor:
- **θ (long-run level, per vessel class)** → SEC EDGAR quarterly TCE disclosures from Star Bulk/Genco/Golden Ocean/Diana. Real, official, free, per class.
- **σ (volatility)** → BDRY daily returns (free via `yfinance`), plus volatility statistics published in the academic BDI-forecasting literature (papers report BDI mean, σ, κ, ADF/half-life — **citing a published statistic is legal even when the underlying series is not free**).
- **κ (mean-reversion speed / half-life)** → same literature; BDI half-life estimates are widely published.
- **Seasonality θ_t** → UNCTAD *Review of Maritime Transport* annual averages + IPA monthly traffic seasonality + monsoon/cyclone calendar.
- **Jump intensity λ and size** → GDELT event counts (port strikes, cyclones, chokepoint closures) + IBTrACS cyclone frequency. **This makes your jump process empirically grounded rather than hand-waved — a genuinely strong slide.**

**2. Cross-validate the synthetic series against free observables.** Your simulated Capesize TCE should correlate with (a) BDRY prices, (b) reported TCEs in EDGAR filings for the matching quarter, (c) API2−API4 spread moves, (d) the headline BDI values you can read daily off Hellenic Shipping News. Publish that correlation table. **A judge who sees "our synthetic Cape series has ρ=0.8 with BDRY and reproduces Star Bulk's reported Q3 TCE within 7%" will treat this as real work.** A judge who sees an unexplained rate curve will not.

**3. Voyage economics — mostly real, little synthesis needed.** Distance (MARNET graph), speed/consumption (EU MRV per-ship data + standard consumption curves), bunker price (EIA Brent + calibrated port spread), port DA and load/discharge rates (port handbooks + IPA output-per-ship-berth-day), canal fees (published tariffs). **Only the freight rate itself needs synthesising** — say that clearly.

**4. Label the synthetic data in the UI.** A visible "simulated / calibrated" badge on modelled series, with a data-provenance page listing every source and licence. This converts your biggest weakness into a credibility asset, and it is the correct engineering practice regardless.

---

## Bottom line

- **Baltic route data is a hard paywall.** Not partially, not with effort — no. Say so plainly in your pitch. The best legal substitutes are **BDRY (daily FFA-linked price)**, **SEC EDGAR TCE-by-class (official quarterly ground truth)**, **API2−API4 / commodity spreads**, and **headline BDI via news republication**.
- **The genuinely strong free finds** are: **IMF PortWatch** (daily port calls + trade, free, the backbone), **IPA turnaround statistics** (official Indian congestion data), **CEA daily coal stock** (a real leading demand indicator almost no competing team will use), **NGA World Port Index** (free machine-readable port specs), **MARNET + searoute/scgraph** (a real routable graph for a real graph algorithm), **GDELT** (free global event signal), **EU MRV** (free per-ship fuel consumption), and **Open-Meteo + IBTrACS** (free weather and cyclone history).
- **Weather, routing, macro, commodities and news are all solidly free.** Freight rates and open-ocean AIS are the two genuinely hard gaps. Design around exactly those two.

**Final caution:** none of the above was live-verified. **Task #8** contains the prioritised verification checklist — run it before anything here reaches the master plan, the deck, or code. Verify **IMF PortWatch's endpoint and Indian port coverage first**; the architecture depends on it more than on anything else in this report.

agentId: af2320c6a6a68a6ef (use SendMessage with to: 'af2320c6a6a68a6ef', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 69010
tool_uses: 9
duration_ms: 856948</usage>