# GET THIS — everything you need to obtain before the build runs end to end

Nothing here costs money. Total time: about 40 minutes of signups, one hour of installs.

Work top to bottom. Section 1 unblocks code. Section 4 is the part that actually wins.

---

## 1. API keys to register (3 needed, all free, all instant)

| # | Key | Where | Time | Env var |
|---|---|---|---|---|
| 1 | Google Gemini | https://aistudio.google.com/apikey | 2 min | `GEMINI_API_KEY` |
| 2 | US EIA v2 | https://www.eia.gov/opendata/register.php | 2 min, emailed | `EIA_API_KEY` |
| 3 | aisstream.io | https://aisstream.io | 2 min | `AISSTREAM_API_KEY` |

**Not a key, but you must decide it:** SEC EDGAR requires a descriptive `User-Agent` containing a real contact email or it returns 403. Pick a team email and put it in `SEC_USER_AGENT`. Do not leave the default.

**Nothing else needs a key.** IMF PortWatch, Open-Meteo, IBTrACS, GDELT, World Bank, yfinance, IPA and CEA are all open.

### Two things about the Gemini free tier that will bite you at the wrong moment

The free tier is rate-limited per minute *and* per day. Five agents, each with a Critic pass, on a supervisor loop, is a lot of calls — you can exhaust a daily quota during rehearsal and walk on stage with a dead demo. So: cache every agent narration into the demo snapshot, make `make demo` read cached narrations by default, and put a `LLM_ENABLED=false` switch in config that degrades to numbers-only output. The deterministic core must produce the full decision memo with the LLM switched off entirely. If it can't, the architecture is wrong.

Second: free-tier terms generally allow the provider to use submitted content to improve models. That is fine for synthetic hackathon cargoes. It is **not** fine the moment SAIL gives you real procurement data, and a PSU security reviewer will ask. Know the answer: paid tier or self-hosted for anything confidential, and say so before they ask.

---

## 2. Software to install locally

| Tool | Version | Why that version |
|---|---|---|
| Docker Desktop | latest, **WSL2 backend** | You're on Windows. Enable WSL2 first (`wsl --install`), then Docker, or the Postgres container will fight you. |
| Python | **3.11** | Not 3.12+. LightGBM, Prophet and statsmodels wheels lag; 3.11 has everything prebuilt. |
| Node.js | 20 LTS | Next.js frontend. |
| Git | latest | CI depends on it, and so does the provenance stamp (`git_sha` on every stored decision). |
| uv | latest | `pip install uv`. Dependency resolution in seconds instead of minutes — matters when six people are rebuilding. |

**Prophet on Windows is a trap** — it compiles Stan and fails in creative ways. Run the whole ML tournament inside the Docker container, never on the host. If Prophet still fights you, drop it: SARIMAX plus LightGBM plus a random-walk baseline is a defensible tournament, and Prophet rarely wins on financial series anyway.

Optional but useful: DBeaver or pgAdmin to eyeball TimescaleDB, and the GitHub CLI.

---

## 3. One-time bulk downloads to commit into `data/raw/`

These have no stable auto-download path, or the site structure changes too often to trust a scraper for the *first* pull. Download once by hand, commit the file, then let the scheduler attempt refreshes on top.

- **EU MRV / THETIS ship dataset** — https://mrv.emsa.europa.eu → the annual XLSX, ~13,000 ships with IMO, DWT, LOA, beam, observed annual fuel consumption. This is your free source of *real* consumption figures instead of textbook cube-law guesses. Get the two most recent reporting years.
- **IPA operational statistics** — https://ipa.nic.in → the latest annual and monthly performance reports as PDFs. Turnaround time and pre-berthing detention per port.
- **World Bank Pink Sheet** — the monthly commodity price XLSX. Direct URL is stable, so this one can be fully automated, but grab it once so week 1 isn't blocked on a scraper.

Create `data/raw/README.md` recording, for each file, the URL, the date you pulled it, and the licence. That file is what makes the provenance chain real instead of decorative.

---

## 4. The asks that matter more than any API — do these in week 1

Each is an email. Each is worth more than a feature.

**4.1 — SAIL's historical fixture data, through the SIH mentor / problem-statement owner channel.** Ask for anonymised or aggregated past fixtures: route, laycan window, vessel class, date fixed, freight paid, discharge port, demurrage incurred. Even 200 rows over two years transforms the project. It converts your headline slide from *"our simulated backtest suggests"* into **"here is what you actually paid, and here is what LAYCAN would have told you to pay."** That is the difference between a good project and the one the sponsor remembers. It costs them nothing, it is their own data, and the worst case is they decline. Ask in week 1, not week 4 — procurement approvals are slow.

**4.2 — Free FFA broker daily reports.** Sign up with a team email at two or three of: Freight Investor Services, SSY, Braemar, Clarksons Securities, Fearnleys. These arrive as daily or weekly PDFs containing **real forward curve levels by quarter and calendar year**, and they are intended for circulation. This is the single highest-value data item on the whole list, because it is the only free, legitimate route to genuine forward freight levels — the thing your entire optimal-stopping module benchmarks against. Set up an inbox rule and a parser; the parsing is annoying and worth it.

**4.3 — Your college library.** One email asking whether the institution holds any shipping intelligence subscription (Clarksons SIN, Drewry, Baltic Exchange academic access). Institutional access is the only realistic free door to licensed-grade data. Ten minutes for a possible transformation.

**4.4 — One chartering professional.** A shipbroker, a port operations person, anyone who has actually fixed a Panamax. Twenty minutes on a call, and one written sentence you can quote. A judge asking "have you spoken to anyone who does this?" is the question that separates the top three from the rest.

---

## 5. Later, with funding — not now

Licensed Baltic route assessments, satellite AIS beyond coastal range, and a commercial shipping intelligence terminal. All are line items in the investor ask, not blockers. Do not scrape any of them.

---

## 6. Five things to pin down while the keys arrive

These are open contradictions or traps in the data plan. Each takes minutes and each can waste a week if ignored.

**6.1 — The PortWatch service name is ambiguous in your notes.** `Daily_Trade_Data` and `Daily_Ports_Data` both appear as "the confirmed endpoint." They are different layers with different fields. Pin the exact service, layer index and field list, then **save one real JSON response into `tests/fixtures/portwatch_sample.json`** and write the parser against the fixture. That fixture is also what makes your test suite run offline.

**6.2 — Gangavaram is not in the returned port list.** The `portid` list you got back contains Kolkata, Chennai, Dhamra, Haldia, Kakinada, Kamarajar, Karaikal, Krishnapatnam, Paradip, Visakhapatnam and Gopalpur — but **not Gangavaram**, even though a later summary claims it is covered. Gangavaram matters more than most: at ~17.7 m it is one of the few genuinely Capesize-capable East Coast options and it sits next to Vizag, which makes it the sharpest comparison in your whole demo. Query for it explicitly by name and by neighbouring coordinates. If it is absent, congestion for Gangavaram comes from IPA statistics plus the port's own daily vessel-position reports, and you need to know that before writing the ingestion schema.

**6.3 — BDRY's price is not a freight rate.** It holds rolling FFA positions, so its level embeds roll yield and expense drag and drifts away from any index over time. Use its **daily returns as a factor**, never its level as a rate. Treating the price series as a freight index is exactly the error a judge with a markets background will catch in one question. Also confirm it is still trading, confirm the actual inception date before assuming history back to 2018, and add a fallback price source — `yfinance` is an unofficial scraper of Yahoo and it breaks and rate-limits without warning.

**6.4 — Check the terms before scraping exchange FFA settlements.** SGX and EEX settlement values derive from licensed Baltic Exchange indices even when a page is free to view. Free to *look at* is not the same as licensed to *store, redistribute and build a product on*. Read the terms, record the verdict in `VERIFY-FIRST.md` V6, and if it is not clearly permitted, drop it — the broker reports in 4.2 give you the same information legitimately.

**6.5 — Update the VERIFY-FIRST log.** Several items are now closed but the table still shows all sixteen unchecked, and `handling_rate_mtpd` is still `unknown` for the ports in `ports.csv`. Fill in the URL and retrieval date for every item you closed. That table is your citation index, and it is what you show a judge who asks where a number came from.

---

## 7. Copy this to `.env`

`.env.example` sits at the repo root. `cp .env.example .env`, fill the three keys and the SEC email, and never commit `.env` — check that `.gitignore` covers it before your first push.

Once `.env` is filled and Docker is running, the build has no external blockers left.
