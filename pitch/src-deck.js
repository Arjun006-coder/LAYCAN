const pptxgen = require("pptxgenjs");

const BG    = "0E1419";  // near-black slate
const PANEL = "18222B";  // card
const PANEL2= "202D38";  // card raised
const TXT   = "F2F5F7";  // primary
const MUTE  = "8A9BA8";  // muted
const DIM   = "5C6D7A";  // very muted
const AMBER = "FF8A3D";  // action / signal accent
const TEAL  = "4FD1C5";  // data / positive
const RED   = "E5484D";  // alert

const H = "Arial";
const M = "Courier New";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.3 x 7.5
pres.author = "Team LAYCAN";
pres.title  = "LAYCAN — Freight Decision Engine";

const W = 13.3, HT = 7.5, MG = 0.6;

function slide(kicker) {
  const s = pres.addSlide();
  s.background = { color: BG };
  if (kicker) {
    s.addText(kicker.toUpperCase(), {
      x: MG, y: 0.26, w: 8, h: 0.28, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 10.5, color: DIM, charSpacing: 2,
    });
  }
  return s;
}

function title(s, t, sub) {
  s.addText(t, {
    x: MG, y: 0.7, w: W - 2 * MG, h: 0.66, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 30, bold: true, color: TXT,
  });
  if (sub) {
    s.addText(sub, {
      x: MG, y: 1.46, w: W - 2 * MG - 1.2, h: 0.44, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 14.5, color: MUTE,
    });
  }
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: fill || PANEL }, line: { color: fill || PANEL, width: 0 },
    shadow: { type: "outer", color: "000000", blur: 10, offset: 2, angle: 90, opacity: 0.35 },
  });
}

function note(s, txt) {
  s.addText(txt, {
    x: MG, y: 6.94, w: W - 2 * MG - 0.7, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 9, color: DIM,
  });
}

let pageNo = 0;
function stamp(s) {
  pageNo++;
  s.addText(String(pageNo).padStart(2, "0"), {
    x: W - MG - 0.5, y: 6.94, w: 0.5, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 9, color: DIM, align: "right",
  });
}

/* ─────────────────────────── 01 TITLE ─────────────────────────── */
{
  const s = slide(null);
  s.addText("LAYCAN", {
    x: MG, y: 2.35, w: 8, h: 1.1, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 68, bold: true, color: TXT, charSpacing: 3,
  });
  s.addText("A freight decision engine for bulk cargo importers.", {
    x: MG, y: 3.5, w: 8.6, h: 0.5, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 20, color: AMBER,
  });
  s.addText(
    "Freight stops being a daily purchase and becomes a managed position.",
    { x: MG, y: 4.05, w: 8.2, h: 0.5, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 14.5, color: MUTE, italic: true });

  card(s, 9.3, 2.35, 3.4, 2.2, PANEL);
  const meta = [
    ["PS ID", "26006"],
    ["ORG", "Ministry of Steel"],
    ["DEPT", "SAIL"],
    ["THEME", "Transport & Logistics"],
  ];
  meta.forEach(([k, v], i) => {
    s.addText(k, { x: 9.55, y: 2.55 + i * 0.5, w: 0.9, h: 0.3, isTextBox: true,
      margin: 0, fontFace: M, fontSize: 9.5, color: DIM });
    s.addText(v, { x: 10.5, y: 2.53 + i * 0.5, w: 2.0, h: 0.32, isTextBox: true,
      margin: 0, fontFace: M, fontSize: 11, color: TXT });
  });

  s.addText("SMART INDIA HACKATHON 2026", {
    x: MG, y: 1.5, w: 6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 11, color: DIM, charSpacing: 2.5,
  });
  s.addNotes("Open with the reframe, not the problem. 'We were asked for a freight forecasting model. We're going to argue that's the wrong product — and show you what a bulk importer actually needs.'");
  stamp(s);
}

/* ─────────────────────────── 02 PROBLEM ─────────────────────────── */
{
  const s = slide("02 / the problem");
  title(s, "SAIL buys freight like a same-day plane ticket",
        "Coal from Australia, Indonesia, Mozambique, the US and Russia into Paradip, Vizag, Gangavaram, Dhamra, Gopalpur, Haldia and Sandheads — one spot voyage at a time.");

  const items = [
    ["NO PRICE DISCIPLINE",
     "Nobody can say whether today's offer is good relative to waiting. The decision defaults to “the plant needs coal — fix it.”"],
    ["VESSEL CHOICE BY HABIT",
     "The trade-off between economies of scale and a port's draft limit is rarely computed. Bigger looks cheaper until it can't berth."],
    ["NO INSTITUTIONAL MEMORY",
     "Decisions live in email and spreadsheets. Nothing compares what was paid against what could have been paid."],
    ["FULLY EXPOSED TO PRICE RISK",
     "Freight is carried unhedged, while the counterparty across every negotiation hedges routinely."],
  ];
  items.forEach(([h, b], i) => {
    const x = MG + (i % 2) * 6.25, y = 2.3 + Math.floor(i / 2) * 2.15;
    card(s, x, y, 5.85, 1.85);
    s.addText(String(i + 1).padStart(2, "0"), {
      x: x + 0.3, y: y + 0.24, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 12, color: AMBER });
    s.addText(h, { x: x + 0.95, y: y + 0.22, w: 4.7, h: 0.32, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 14.5, bold: true, color: TXT });
    s.addText(b, { x: x + 0.95, y: y + 0.66, w: 4.6, h: 1.0, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 12.5, color: MUTE });
  });
  s.addNotes("These four are not a list of complaints — each one becomes a module in the product. Say that.");
  stamp(s);
}

/* ─────────────────────────── 03 THE TRAP ─────────────────────────── */
{
  const s = slide("03 / the trap");
  title(s, "A hundred teams will build a forecasting model",
        "It is the wrong product — and saying so out loud is where our credibility starts.");

  card(s, MG, 2.2, 3.9, 2.5);
  s.addText("Dry bulk rates are close\nto a random walk", {
    x: MG + 0.32, y: 2.5, w: 3.3, h: 0.9, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 16, bold: true, color: TXT });
  s.addText("High volatility, volatility clustering, jumps, slow mean reversion. Beating a naive benchmark at 30–90 days is genuinely hard.", {
    x: MG + 0.32, y: 3.45, w: 3.3, h: 1.0, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: MUTE });

  card(s, MG + 4.15, 2.2, 3.9, 2.5);
  s.addText("A liquid forward market\nalready prices it", {
    x: MG + 4.47, y: 2.5, w: 3.3, h: 0.9, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 16, bold: true, color: TXT });
  s.addText("Forward Freight Agreements aggregate the informed opinion of every trading desk on earth. Six students will not out-forecast that curve.", {
    x: MG + 4.47, y: 3.45, w: 3.3, h: 1.0, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: MUTE });

  card(s, MG + 8.3, 2.2, 3.8, 2.5, PANEL2);
  s.addText("So we don't try.", {
    x: MG + 8.62, y: 2.5, w: 3.2, h: 0.45, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 18, bold: true, color: AMBER });
  s.addText("We benchmark against a random walk and against the curve, publish where we lose, and put the value somewhere it doesn't depend on forecast superiority.", {
    x: MG + 8.62, y: 3.05, w: 3.2, h: 1.4, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12.5, color: TXT });

  s.addText("The real problem is not prediction. It is decision-making under uncertainty.", {
    x: MG, y: 5.15, w: W - 2 * MG, h: 0.5, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 21, bold: true, color: TEAL });
  s.addText("Which is an optimal stopping problem, a constrained optimisation problem, and a risk management problem — wearing a forecasting costume.", {
    x: MG, y: 5.72, w: W - 2 * MG, h: 0.5, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 14, color: MUTE });
  s.addNotes("This slide is the whole pitch. Deliver it slowly and with confidence. Conceding that forecasting is hard is what buys you credibility for everything after.");
  stamp(s);
}

/* ─────────────────────────── 04 REFRAME ─────────────────────────── */
{
  const s = slide("04 / the reframe");
  title(s, "Four questions a forecast can't answer");

  const rows = [
    ["Fix today, or wait?",
     "“Rates may fall around 5%”",
     "Fix if it prints at or below $21.40/mt. It's at $23.10. Wait. Threshold rises to $22.60 by the 14th."],
    ["Which vessel class?",
     "“Capesize is cheaper per tonne”",
     "Kamsarmax. The Cape is draft-limited here, so you pay for capacity you cannot load."],
    ["Which instrument?",
     "— silent —",
     "60% of Q4 on a 4-voyage COA, 40% spot. Full cover looks cheaper but your volume band is ±18%."],
    ["How much risk?",
     "— silent —",
     "Unhedged Q4 exposure $14.2M, 95% CVaR $2.1M. 45 FFA lots cut tail risk 38% at zero premium."],
  ];

  s.addText("A FORECASTING MODEL SAYS", { x: 4.15, y: 2.12, w: 3.4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 9.5, color: DIM, charSpacing: 1.5 });
  s.addText("LAYCAN SAYS", { x: 7.85, y: 2.12, w: 3.4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 9.5, color: AMBER, charSpacing: 1.5 });

  rows.forEach(([q, a, b], i) => {
    const y = 2.52 + i * 1.12;
    card(s, MG, y, 3.35, 0.98, PANEL);
    s.addText(q, { x: MG + 0.24, y: y + 0.3, w: 2.95, h: 0.4, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 14, bold: true, color: TXT });
    s.addText(a, { x: 4.15, y: y + 0.22, w: 3.4, h: 0.6, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 12, color: DIM, italic: true });
    card(s, 7.8, y, 4.9, 0.98, PANEL2);
    s.addText(b, { x: 8.02, y: y + 0.13, w: 4.5, h: 0.75, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 11.5, color: TXT });
  });
  note(s, "Figures illustrative — replace with output from your own backtest and demo scenario.");
  s.addNotes("The right-hand column is a product a company pays for. The left is a homework assignment.");
  stamp(s);
}

/* ─────────────────────────── 05 THE MEMO ─────────────────────────── */
{
  const s = slide("05 / the product");
  title(s, "One object: the Decision Memo",
        "Every solver, every agent and every data source exists to produce this one page.");

  card(s, MG, 2.05, 7.55, 4.55, PANEL);
  const memo = [
    ["DECISION MEMO · SAIL-COK-2026-118", TXT, true],
    ["75,000 mt (±10% MOLOO) Coking Coal · Hay Point → Paradip", MUTE, false],
    ["Laycan 05–15 Oct 2026 · 43 days to window open", MUTE, false],
    ["", TXT, false],
    ["RECOMMENDATION                          WAIT", AMBER, true],
    ["Reservation rate today ....... $21.40 /mt", TXT, false],
    ["Market indication ............ $23.10 /mt  (+7.9%)", TXT, false],
    ["Threshold on 14 Sep .......... $22.60 /mt  (rising)", TXT, false],
    ["Latest advisable fixing date .. 21 Sep 2026", TXT, false],
    ["", TXT, false],
    ["Vessel class ................. KAMSARMAX", TEAL, false],
    ["Instrument ................... 4-voyage COA, 60% of Q4", TEAL, false],
    ["Hedge ........................ sell 45 lots P5TC Q4", TEAL, false],
    ["", TXT, false],
    ["Expected landed ......... $22.05 /mt (P10 19.8 / P90 25.1)", TXT, false],
    ["vs fix-today ................. −$1.05 /mt = −$78,750", TXT, false],
    ["Confidence ................... MEDIUM-HIGH", TXT, false],
    ["Critic flags ................. 1 (cyclone watch)", RED, false],
  ];
  s.addText(memo.map(([t, c, b], i) => ({
    text: t || " ",
    options: { color: c, bold: b, fontSize: t ? 11.5 : 5,
               breakLine: i < memo.length - 1 },
  })), {
    x: MG + 0.32, y: 2.28, w: 7.0, h: 4.1, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 11.5, lineSpacingMultiple: 1.28, valign: "top",
  });

  const props = [
    ["One unambiguous action", "not a chart to interpret"],
    ["A number that makes it falsifiable", "you can check us tomorrow"],
    ["The cost of ignoring it", "the counterfactual, in dollars"],
    ["A named objection", "confidence with a reason attached"],
    ["The rejected alternative, with arithmetic", "why not Capesize"],
    ["An expiry date", "decisions go stale"],
    ["Full provenance on every figure", "source, licence, timestamp"],
  ];
  s.addText("WHAT MAKES IT A PRODUCT AND NOT A DASHBOARD", {
    x: 8.5, y: 2.1, w: 4.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 9.5, color: DIM, charSpacing: 1.2 });
  props.forEach(([a, b], i) => {
    const y = 2.55 + i * 0.58;
    s.addText("→", { x: 8.5, y: y, w: 0.25, h: 0.28, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 12, color: AMBER });
    s.addText(a, { x: 8.8, y: y - 0.02, w: 4.0, h: 0.3, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 12.5, bold: true, color: TXT });
    s.addText(b, { x: 8.8, y: y + 0.25, w: 4.0, h: 0.3, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 11, color: MUTE });
  });
  note(s, "Illustrative scenario. The test: a procurement head can forward this to their director unedited.");
  stamp(s);
}

/* ─────────────────────────── 06 PORT PHYSICS ─────────────────────────── */
{
  const s = slide("06 / why bigger isn't cheaper");
  title(s, "The calculation the industry gets wrong",
        "A port's draft limit is really a cargo limit. Ignore it and you recommend a vessel that pays for capacity it cannot load.");

  card(s, MG, 2.35, 6.15, 3.5, PANEL);
  s.addText("DRAFT → TONNES", { x: MG + 0.3, y: 2.55, w: 3, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 10, color: AMBER, charSpacing: 1.2 });
  const math = [
    "d_max     = permissible_draft − UKC",
    "ΔDWT      = TPC × 100 × (summer_draft − d_max)",
    "DWT_avail = summer_DWT − ΔDWT",
    "cargo     = DWT_avail − bunkers − water",
    "            − stores − constants",
    "",
    "FWA_mm = displacement / (4 × TPC)",
    "DWA_mm = FWA_mm × (1025 − ρ_dock) / 25",
    "",
    "INTAKE = min(weight_limited, volume_limited)",
  ];
  math.forEach((l, i) => {
    s.addText(l, { x: MG + 0.3, y: 2.95 + i * 0.26, w: 5.6, h: 0.26, isTextBox: true,
      margin: 0, fontFace: M, fontSize: 11, color: l.startsWith("INTAKE") ? TEAL : TXT });
  });

  card(s, 7.35, 2.35, 5.35, 3.5, PANEL2);
  s.addText("WORKED EXAMPLE · CAPESIZE AT A DRAFT-LIMITED PORT", {
    x: 7.6, y: 2.55, w: 4.9, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 9.5, color: AMBER, charSpacing: 1 });
  const ex = [
    ["Summer deadweight", "180,000 mt"],
    ["Summer draft", "18.0 m"],
    ["Permissible draft (illustrative)", "14.5 m"],
    ["Under-keel clearance", "0.6 m"],
    ["TPC", "130 mt/cm"],
    ["Deadweight sacrificed", "−53,300 mt"],
    ["Less constants and bunkers", "−6,500 mt"],
  ];
  ex.forEach(([k, v], i) => {
    s.addText(k, { x: 7.6, y: 2.95 + i * 0.3, w: 3.4, h: 0.28, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 11.5, color: MUTE });
    s.addText(v, { x: 11.0, y: 2.93 + i * 0.3, w: 1.5, h: 0.28, isTextBox: true,
      margin: 0, fontFace: M, fontSize: 11.5, color: TXT, align: "right" });
  });
  s.addText("MAX INTAKE", { x: 7.6, y: 5.08, w: 2.4, h: 0.35, isTextBox: true,
    margin: 0, fontFace: H, fontSize: 14, bold: true, color: TXT });
  s.addText("≈ 120,200 mt", { x: 9.6, y: 5.05, w: 2.9, h: 0.4, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 17, bold: true, color: AMBER, align: "right" });
  s.addText("67% of the ship you are paying for. Scale economy gone — and full intake means lightering at anchorage, which costs money and days.", {
    x: 7.6, y: 5.46, w: 4.9, h: 0.45, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 10.5, color: MUTE });

  s.addText("Feasibility is a hard constraint, never a penalty. A vessel that cannot berth is not a worse answer — it is a wrong answer.", {
    x: MG, y: 6.15, w: W - 2 * MG, h: 0.4, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 14, bold: true, color: TEAL });
  note(s, "Draft figure illustrative pending verification (VERIFY-FIRST V3). Method is exact.");
  s.addNotes("This is the credibility moment of the whole pitch. Do not rush it. This is the layer outsiders always get wrong, and a shipping person in the room will lean forward here.");
  stamp(s);
}

/* ─────────────────────────── 07 ARCHITECTURE ─────────────────────────── */
{
  const s = slide("07 / architecture");
  title(s, "Two layers, one rule that makes it trustworthy",
        "The reasoning layer decides what to ask. The deterministic core decides what is true.");

  card(s, MG, 2.1, W - 2 * MG, 1.55, PANEL2);
  s.addText("REASONING LAYER · LLM agents on a typed graph", {
    x: MG + 0.35, y: 2.28, w: 7, h: 0.32, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 15, bold: true, color: TXT });
  s.addText("Gathers · interprets · challenges · explains · narrates", {
    x: MG + 0.35, y: 2.62, w: 7, h: 0.3, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12.5, color: MUTE });
  s.addText("MAY NOT COMPUTE.  MAY NOT EMIT A NUMERAL.", {
    x: MG + 0.35, y: 3.02, w: 7, h: 0.35, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 13, bold: true, color: RED });
  s.addText("Enforced by a Pydantic validator\nand a CI check. Not by convention.", {
    x: 8.6, y: 2.42, w: 3.7, h: 0.7, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: MUTE, align: "right" });

  s.addText("typed tool calls  ↓      ↑  typed structured results", {
    x: MG, y: 3.75, w: W - 2 * MG, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 10.5, color: DIM, align: "center" });

  card(s, MG, 4.12, W - 2 * MG, 2.15, PANEL);
  s.addText("DETERMINISTIC CORE · pure Python, no LLM, unit- and property-tested", {
    x: MG + 0.35, y: 4.3, w: 9, h: 0.32, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 15, bold: true, color: TXT });
  const mods = [
    ["physics/", "draft-limited intake, TPC, FWA, load lines"],
    ["voyage/", "TCE, bunkers (cube law), laytime, demurrage"],
    ["rates/", "OU-jump simulator, calibration, conformal bands"],
    ["timing/", "LSMC optimal stopping → reservation curve"],
    ["routing/", "marine graph, A*, weather-weighted edges"],
    ["assign/", "MILP over cargo × class × port × window"],
    ["risk/ hedge/", "CVaR, scenarios, hedge ratio, basis risk"],
    ["backtest/", "policy replay vs naive vs oracle"],
  ];
  mods.forEach(([a, b], i) => {
    const x = MG + 0.35 + (i % 2) * 5.95, y = 4.75 + Math.floor(i / 2) * 0.37;
    s.addText(a, { x, y, w: 1.35, h: 0.3, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 11, color: TEAL });
    s.addText(b, { x: x + 1.4, y, w: 4.4, h: 0.3, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 11.5, color: MUTE });
  });
  s.addText("Every numeral in the product comes from a versioned solver and carries provenance to its source, licence and timestamp. A hallucinated figure is structurally impossible, not merely unlikely.", {
    x: MG, y: 6.42, w: W - 2 * MG, h: 0.45, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 13, color: TXT });
  s.addNotes("If you remember one line from this deck, it is the red one. This is what lets a procurement head sign off on our output.");
  stamp(s);
}

/* ─────────────────────────── 08 AGENTS + CRITIC ─────────────────────────── */
{
  const s = slide("08 / the agent layer");
  title(s, "Agents at the edges, solvers in the middle",
        "If you cannot explain what an agent does that a function call could not, delete the agent.");

  const agents = [
    ["Market Analyst", "rate state, curve, calibration"],
    ["Fleet Supply", "tonnage tightness in ballast radius"],
    ["Demand", "coal stocks, plant burn, volume band"],
    ["Port Feasibility", "hard physics, intake caps, reasons"],
    ["Voyage Economist", "TCE and full cost breakdown"],
    ["Risk & Disruption", "events → jump intensity, waiting days"],
    ["Instrument Strategist", "spot / TCT / COA / FFA mix"],
    ["Hedge Desk", "ratio, lots, effectiveness, basis risk"],
  ];
  agents.forEach(([a, b], i) => {
    const x = MG + (i % 2) * 3.95, y = 2.35 + Math.floor(i / 2) * 0.92;
    card(s, x, y, 3.7, 0.78, PANEL);
    s.addText(a, { x: x + 0.22, y: y + 0.1, w: 3.3, h: 0.3, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 12.5, bold: true, color: TXT });
    s.addText(b, { x: x + 0.22, y: y + 0.42, w: 3.3, h: 0.3, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 10.5, color: MUTE });
  });

  card(s, 8.5, 2.35, 4.2, 4.15, PANEL2);
  s.addText("THE CRITIC", { x: 8.78, y: 2.55, w: 3, h: 0.4, isTextBox: true,
    margin: 0, fontFace: H, fontSize: 20, bold: true, color: RED });
  s.addText("An agent whose only job is to attack the recommendation before it ships.", {
    x: 8.78, y: 3.0, w: 3.65, h: 0.55, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: TXT });
  const checks = [
    "Out-of-distribution state",
    "Regime change tests",
    "Forward-curve disagreement",
    "Single-source ablation",
    "Calibration drift",
    "Independent feasibility recheck",
    "Magnitude plausibility",
  ];
  checks.forEach((c, i) => {
    s.addText("▪", { x: 8.78, y: 3.68 + i * 0.32, w: 0.2, h: 0.28, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 9, color: RED });
    s.addText(c, { x: 9.0, y: 3.65 + i * 0.32, w: 3.4, h: 0.3, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 11.5, color: MUTE });
  });
  s.addText("When it can't get comfortable, the product says so and escalates to a human.", {
    x: 8.78, y: 5.95, w: 3.65, h: 0.45, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, bold: true, color: TEAL });
  s.addNotes("A system that knows when to shut up is more trustworthy than one that is always sure. Demo the Critic firing live — it lands better than any diagram.");
  stamp(s);
}

/* ─────────────────────────── 09 OPTIMAL STOPPING ─────────────────────────── */
{
  const s = slide("09 / the timing engine");
  title(s, "Fix-or-wait is an optimal stopping problem",
        "Structurally the same as exercising an American option — and solved the same way, with Least-Squares Monte Carlo.");

  card(s, MG, 2.35, 4.5, 4.0, PANEL);
  s.addText("V_t = min{ R_t , E[ V_t+1 | F_t ] }", {
    x: MG + 0.3, y: 2.62, w: 3.9, h: 0.35, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 13, color: TXT });
  s.addText("R*_t = E[ V_t+1 | F_t ]", {
    x: MG + 0.3, y: 3.02, w: 3.9, h: 0.35, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 13, color: TEAL });
  s.addText("FIX  iff  R_t ≤ R*_t", {
    x: MG + 0.3, y: 3.42, w: 3.9, h: 0.35, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 13, bold: true, color: AMBER });
  s.addText("The reservation rate is the continuation value. Two properties we test for, because they are how a real charterer behaves:", {
    x: MG + 0.3, y: 3.95, w: 3.9, h: 0.6, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: MUTE });
  s.addText("It rises as the laycan closes.\nYou get less choosy as you run out of runway.", {
    x: MG + 0.3, y: 4.62, w: 3.9, h: 0.55, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: TXT });
  s.addText("It widens with volatility.\nMore uncertainty means more value in waiting.", {
    x: MG + 0.3, y: 5.25, w: 3.9, h: 0.55, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: TXT });

  const days = [45, 40, 35, 30, 25, 20, 15, 10, 5, 0];
  s.addChart(pres.ChartType.line, [
    { name: "Reservation rate R*", labels: days.map(String),
      values: [20.4, 20.6, 20.9, 21.2, 21.6, 22.1, 22.6, 23.3, 24.1, 25.2] },
    { name: "Market rate", labels: days.map(String),
      values: [24.2, 23.8, 23.4, 23.1, 22.4, 22.6, 21.9, 21.2, 21.5, 21.8] },
  ], {
    x: 5.4, y: 2.35, w: 7.3, h: 4.0,
    showTitle: true, title: "Reservation rate vs market, by days to laycan (illustrative)",
    titleColor: TXT, titleFontSize: 12, titleFontFace: H,
    chartColors: [AMBER, TEAL], lineDataSymbol: "none", lineSize: 3,
    showLegend: true, legendPos: "b", legendColor: MUTE, legendFontSize: 10,
    catAxisLabelColor: MUTE, valAxisLabelColor: MUTE,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
    catAxisTitle: "days to laycan", showCatAxisTitle: true,
    catAxisTitleColor: DIM, catAxisTitleFontSize: 10,
    valAxisTitle: "$/mt", showValAxisTitle: true,
    valAxisTitleColor: DIM, valAxisTitleFontSize: 10,
    valGridLine: { color: "2A3742", size: 1 }, catGridLine: { style: "none" },
    valAxisMinVal: 20, plotArea: { fill: { color: PANEL } },
  });
  s.addText("↓ market crosses below the threshold — FIX", {
    x: 8.4, y: 5.42, w: 4.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 10.5, bold: true, color: AMBER });
  s.addNotes("Where the market line crosses below the reservation line, we fix. Point at the crossing.");
  stamp(s);
}

/* ─────────────────────────── 10 INSTRUMENT + HEDGE ─────────────────────────── */
{
  const s = slide("10 / instrument & hedge");
  title(s, "The layer nobody sells to physical importers",
        "Indian industrial buyers are structurally unhedged on freight while every counterparty they negotiate with hedges routinely.");

  s.addChart(pres.ChartType.line, [
    { name: "Expected cost $/mt", labels: ["0%", "20%", "40%", "60%", "80%", "100%"],
      values: [22.9, 22.6, 22.35, 22.2, 22.15, 22.1] },
    { name: "95% CVaR $/mt", labels: ["0%", "20%", "40%", "60%", "80%", "100%"],
      values: [28.4, 27.1, 25.9, 25.1, 25.4, 26.8] },
  ], {
    x: MG, y: 2.4, w: 6.6, h: 3.9,
    showTitle: true, title: "Cost vs tail risk, by share of volume on term cover (illustrative)",
    titleColor: TXT, titleFontSize: 12, titleFontFace: H,
    chartColors: [TEAL, AMBER], lineDataSymbol: "circle", lineSize: 3,
    showLegend: true, legendPos: "b", legendColor: MUTE, legendFontSize: 10,
    catAxisLabelColor: MUTE, valAxisLabelColor: MUTE,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
    valGridLine: { color: "2A3742", size: 1 }, catGridLine: { style: "none" },
    valAxisMinVal: 20, plotArea: { fill: { color: PANEL } },
  });

  card(s, 7.4, 2.4, 5.3, 1.85, PANEL2);
  s.addText("WHY COVER IS CAPPED, NOT MAXIMISED", { x: 7.65, y: 2.58, w: 4.8, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 9.5, color: AMBER, charSpacing: 1 });
  s.addText("A term contract is only cheap if you can actually lift it. So COA coverage is capped by the lower confidence bound of the volume forecast — not the mean. Short-lifting costs more than the rate saving.", {
    x: 7.65, y: 2.95, w: 4.8, h: 1.1, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: TXT });

  card(s, 7.4, 4.4, 5.3, 1.8, PANEL);
  s.addText("THE HEDGE, STATED HONESTLY", { x: 7.65, y: 4.58, w: 4.8, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 9.5, color: AMBER, charSpacing: 1 });
  const hedge = [
    ["h* = Cov(ΔS,ΔF)/Var(ΔF)", "minimum-variance ratio"],
    ["effectiveness = ρ²", "variance actually removed"],
    ["σ(S − h*F)", "residual basis risk, in $/mt"],
  ];
  hedge.forEach(([a, b], i) => {
    s.addText(a, { x: 7.65, y: 4.95 + i * 0.42, w: 2.7, h: 0.3, isTextBox: true,
      margin: 0, fontFace: M, fontSize: 11, color: TEAL });
    s.addText(b, { x: 10.35, y: 4.95 + i * 0.42, w: 2.1, h: 0.3, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 10.5, color: MUTE });
  });
  s.addText("A hedge sold as perfect is one that will eventually embarrass you.", {
    x: 7.4, y: 6.34, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11, italic: true, color: MUTE });
  s.addText("↑ tail risk bottoms out near 60% cover, not 100%", {
    x: 1.4, y: 4.28, w: 4.0, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 10, bold: true, color: AMBER });
  stamp(s);
}

/* ─────────────────────────── 11 THE EVIDENCE ─────────────────────────── */
{
  const s = slide("11 / the evidence");
  title(s, "We backtest decisions, not forecasts",
        "Everyone shows forecast error. We show money. Walk-forward, point-in-time features, a leakage test in CI, and net of all frictions.");

  s.addChart(pres.ChartType.bar, [
    { name: "Mean freight paid $/mt",
      labels: ["Naive buyer\n(status quo)", "LAYCAN policy", "Oracle\n(perfect hindsight)"],
      values: [23.80, 22.35, 20.90] },
  ], {
    x: MG, y: 2.5, w: 6.4, h: 3.7,
    barDir: "col", showTitle: false,
    chartColors: [DIM, AMBER, TEAL],
    varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: TXT,
    dataLabelFontFace: M, dataLabelFontSize: 13, dataLabelFormatCode: "$0.00",
    showLegend: false,
    catAxisLabelColor: MUTE, valAxisLabelColor: MUTE,
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    valGridLine: { color: "2A3742", size: 1 }, catGridLine: { style: "none" },
    valAxisMinVal: 18, valAxisMaxVal: 25,
    plotArea: { fill: { color: PANEL } },
  });

  card(s, 7.2, 2.5, 5.5, 1.5, PANEL2);
  s.addText("CAPTURE RATIO", { x: 7.45, y: 2.68, w: 3, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 9.5, color: AMBER, charSpacing: 1.2 });
  s.addText("50%", { x: 7.45, y: 2.98, w: 2.0, h: 0.75, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 46, bold: true, color: TXT });
  s.addText("of the timing value that was theoretically available", {
    x: 9.5, y: 3.15, w: 2.95, h: 0.6, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: MUTE });

  const mets = [
    ["Saving vs naive", "$1.45 /mt"],
    ["Regret vs oracle", "$1.45 /mt"],
    ["Worst quarter", "always reported"],
    ["Tail risk with hedge", "CVaR −38%"],
  ];
  mets.forEach(([k, v], i) => {
    const y = 4.22 + i * 0.52;
    s.addText(k, { x: 7.45, y, w: 2.9, h: 0.3, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 12, color: MUTE });
    s.addText(v, { x: 10.35, y: y - 0.02, w: 2.1, h: 0.32, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 12, color: TXT, align: "right" });
  });
  s.addText("Capture ratio is the number to lead with. It concedes the oracle is unreachable, and it is a claim a CFO can act on.", {
    x: 7.45, y: 6.32, w: 5.1, h: 0.45, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11, italic: true, color: TEAL });
  note(s, "Illustrative structure — populate with your own backtest output. Never quote a saving without its worst case.");
  s.addNotes("This is the slide that closes. If the backtest doesn't beat naive, say so honestly and pivot the pitch to the constraint and hedging value, which doesn't depend on timing skill.");
  stamp(s);
}

/* ─────────────────────────── 12 HONESTY ─────────────────────────── */
{
  const s = slide("12 / what's real");
  title(s, "Our data honestly, before you ask");

  card(s, MG, 2.2, 3.85, 4.2, PANEL);
  s.addText("REAL AND CITED", { x: MG + 0.28, y: 2.4, w: 3.3, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 10, color: TEAL, charSpacing: 1.2 });
  const real = ["Daily port calls and trade estimates", "Official Indian port turnaround and pre-berthing detention", "Daily power-plant coal stocks", "Commodity and energy price series", "Marine weather and cyclone history", "Global news event feed", "Machine-readable port specifications", "Marine routing network graph", "Quarterly TCE by class from owners' filings"];
  real.forEach((t, i) => {
    s.addText("✓", { x: MG + 0.28, y: 2.76 + i * 0.36, w: 0.2, h: 0.28,
      isTextBox: true, margin: 0, fontFace: H, fontSize: 10, color: TEAL });
    s.addText(t, { x: MG + 0.52, y: 2.73 + i * 0.36, w: 3.1, h: 0.36, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 10.5, color: MUTE });
  });

  card(s, 4.75, 2.2, 3.85, 4.2, PANEL);
  s.addText("SIMULATED, AND BADGED AS SUCH", { x: 5.03, y: 2.4, w: 3.4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 10, color: AMBER, charSpacing: 1.2 });
  s.addText("Licensed freight route assessments are paywalled and we will not scrape them. So the daily rate series is a calibrated stochastic process — and every simulated value carries a visible badge in the UI.", {
    x: 5.03, y: 2.78, w: 3.35, h: 1.3, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: TXT });
  s.addText("CALIBRATED TO", { x: 5.03, y: 4.2, w: 3.4, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 9.5, color: DIM, charSpacing: 1 });
  const cal = ["Official quarterly TCE disclosures", "Freight-linked traded instrument volatility", "Published mean-reversion half-lives", "Event frequency from the news feed"];
  cal.forEach((t, i) => {
    s.addText("▪ " + t, { x: 5.03, y: 4.55 + i * 0.36, w: 3.35, h: 0.34,
      isTextBox: true, margin: 0, fontFace: H, fontSize: 10.5, color: MUTE });
  });
  s.addText("Then validated against free observables, and the correlation table published.", {
    x: 5.03, y: 6.02, w: 3.35, h: 0.32, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 10.5, italic: true, color: TEAL });

  card(s, 8.85, 2.2, 3.85, 4.2, PANEL2);
  s.addText("WHAT WE REFUSE TO CLAIM", { x: 9.13, y: 2.4, w: 3.4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 10, color: RED, charSpacing: 1.2 });
  const ref = [
    "That we beat the forward curve at long horizons",
    "A savings figure without its worst-case counterpart",
    "Simulated series presented as observed",
    "A confidence number whose calibration we haven't measured",
  ];
  ref.forEach((t, i) => {
    s.addText("✗", { x: 9.13, y: 2.85 + i * 0.85, w: 0.22, h: 0.28,
      isTextBox: true, margin: 0, fontFace: H, fontSize: 11, color: RED });
    s.addText(t, { x: 9.4, y: 2.8 + i * 0.85, w: 3.1, h: 0.7, isTextBox: true,
      margin: 0, fontFace: H, fontSize: 11.5, color: TXT });
  });
  s.addText("A licence is a config change and a line in the funding plan — not an architectural problem.", {
    x: 9.13, y: 6.02, w: 3.4, h: 0.32, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 10.5, italic: true, color: MUTE });
  s.addNotes("Deliver this slide proactively, before anyone asks. Volunteering a measured limitation is the strongest signal that your other numbers weren't chosen to flatter.");
  stamp(s);
}

/* ─────────────────────────── 13 DIFFERENTIATION ─────────────────────────── */
{
  const s = slide("13 / positioning");
  title(s, "Incumbents sell terminals. We sell a decision.");

  card(s, MG, 2.3, 5.85, 3.9, PANEL);
  s.addText("MARITIME INTELLIGENCE PLATFORMS", { x: MG + 0.3, y: 2.5, w: 5.2, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 10, color: DIM, charSpacing: 1.2 });
  s.addText("Vessel tracking, market data, fixture history, voyage management, chartering workflow", {
    x: MG + 0.3, y: 2.85, w: 5.2, h: 0.55, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: MUTE });
  s.addText("SOLD TO", { x: MG + 0.3, y: 3.55, w: 5.2, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 9.5, color: DIM, charSpacing: 1 });
  s.addText("Shipowners · operators · brokers · commodity trading desks", {
    x: MG + 0.3, y: 3.88, w: 5.2, h: 0.4, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 13, bold: true, color: TXT });
  s.addText("People who charter every day, have a desk, and already know what the market is worth. They need data, and they buy it by the seat.", {
    x: MG + 0.3, y: 4.4, w: 5.2, h: 0.8, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: MUTE });
  s.addText("They do not sell a prescriptive fix-or-wait threshold, a port-constrained vessel choice, an instrument mix, or a hedge — to a buyer with no desk.", {
    x: MG + 0.3, y: 5.3, w: 5.2, h: 0.7, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, italic: true, color: MUTE });

  card(s, 6.85, 2.3, 5.85, 3.9, PANEL2);
  s.addText("LAYCAN", { x: 7.15, y: 2.5, w: 5.2, h: 0.35, isTextBox: true,
    margin: 0, fontFace: H, fontSize: 17, bold: true, color: AMBER });
  s.addText("A daily decision with a threshold, a vessel, an instrument and a hedge — backtested in money", {
    x: 7.15, y: 2.9, w: 5.2, h: 0.5, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 12, color: TXT });
  s.addText("SOLD TO", { x: 7.15, y: 3.55, w: 5.2, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 9.5, color: DIM, charSpacing: 1 });
  s.addText("Industrial importers moving 0.5–10 Mtpa with no chartering desk", {
    x: 7.15, y: 3.88, w: 5.2, h: 0.4, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 13, bold: true, color: TXT });
  s.addText("Steel, power and cement companies with real freight exposure, no quantitative rate policy, and no hedge. Big enough for the savings to matter, small enough not to have built the capability.", {
    x: 7.15, y: 4.4, w: 5.2, h: 0.9, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11.5, color: MUTE });
  s.addText("Different buyer. Different product. An unoccupied position.", {
    x: 7.15, y: 5.5, w: 5.2, h: 0.4, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 13, bold: true, color: TEAL });
  note(s, "Competitive claims pending verification (VERIFY-FIRST V12) — test this hypothesis before pitching it.");
  stamp(s);
}

/* ─────────────────────────── 14 BUSINESS ─────────────────────────── */
{
  const s = slide("14 / the company");
  title(s, "Be the decision to earn the data",
        "Then be the data to earn the index — a benchmark for India-bound bulk freight that nobody publishes today.");

  const phases = [
    ["PHASE 1", "0–6 months", "One route, one customer, shadow mode",
     "Run alongside an existing desk for a quarter. Log every recommendation immutably. The deliverable is not software — it is a number."],
    ["PHASE 2", "6–18 months", "The product",
     "Full instrument layer, hedge advisory, ERP integration, multi-plant portfolio. Three to five paying customers. Pricing normalises."],
    ["PHASE 3", "18–36 months", "The data asset",
     "Models trained on real fixture outcomes. And an authoritative benchmark for India-bound dry bulk freight, which does not exist publicly today."],
  ];
  phases.forEach(([p, t, h, b], i) => {
    const x = MG + i * 4.12;
    card(s, x, 2.25, 3.85, 2.6, i === 2 ? PANEL2 : PANEL);
    s.addText(p, { x: x + 0.28, y: 2.45, w: 1.6, h: 0.3, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 10, color: AMBER, charSpacing: 1.2 });
    s.addText(t, { x: x + 1.9, y: 2.45, w: 1.7, h: 0.3, isTextBox: true, margin: 0,
      fontFace: M, fontSize: 10, color: DIM, align: "right" });
    s.addText(h, { x: x + 0.28, y: 2.82, w: 3.3, h: 0.55, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 14.5, bold: true, color: TXT });
    s.addText(b, { x: x + 0.28, y: 3.5, w: 3.3, h: 1.2, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 11.5, color: MUTE });
  });

  card(s, MG, 5.1, W - 2 * MG, 1.72, PANEL);
  s.addText("THE MOAT", { x: MG + 0.3, y: 5.28, w: 2, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 10, color: AMBER, charSpacing: 1.2 });
  s.addText("Software features are copyable. Two things are not.", {
    x: MG + 0.3, y: 5.6, w: 5.5, h: 0.35, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 14, bold: true, color: TXT });
  s.addText("Every recommendation, stored with its model version, joined to what actually happened — the rate fixed, the days waited, the demurrage paid. Nobody else has this for India-bound bulk, because nobody else is in the decision loop.", {
    x: MG + 0.3, y: 5.98, w: 5.5, h: 0.6, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11, color: MUTE });
  s.addText("And the benchmark. Baltic-grade assessments exist for the world's liquid routes, not for Newcastle→Paradip. A platform inside enough Indian importers' fixture flow can construct the reference nobody publishes — and index businesses become infrastructure.", {
    x: 6.6, y: 5.98, w: 6.1, h: 0.6, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11, color: MUTE });
  s.addNotes("Sequence matters. Do not try to start at the index.");
  stamp(s);
}

/* ─────────────────────────── 15 SCOPE ─────────────────────────── */
{
  const s = slide("15 / scope discipline");
  title(s, "What we built, and what we deliberately did not",
        "Naming your exclusions is a credibility signal, not a weakness.");

  card(s, MG, 2.35, 6.1, 4.1, PANEL);
  s.addText("BUILT FOR SIH", { x: MG + 0.3, y: 2.55, w: 3, h: 0.3, isTextBox: true,
    margin: 0, fontFace: M, fontSize: 10, color: TEAL, charSpacing: 1.2 });
  const built = ["Canonical port, vessel and cargo domain model", "Rate state with basis decomposition", "Calibrated probabilistic forecasts", "Reservation-rate timing policy", "Draft-limited cargo intake solver", "MILP vessel and port assignment", "Full voyage economics and TCE", "Congestion and waiting nowcast", "Idle and repositioning comparison", "Instrument portfolio on a CVaR frontier", "Hedge sizing with basis risk", "Risk and disruption early warning", "Decision memo with full provenance", "Decision backtest harness"];
  built.forEach((t, i) => {
    const x = MG + 0.3 + (i % 2) * 2.95, y = 2.92 + Math.floor(i / 2) * 0.47;
    s.addText("✓ " + t, { x, y, w: 2.85, h: 0.44, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 10.5, color: MUTE });
  });

  card(s, 7.1, 2.35, 5.6, 4.1, PANEL2);
  s.addText("DELIBERATELY OUT OF SCOPE", { x: 7.38, y: 2.55, w: 4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: M, fontSize: 10, color: AMBER, charSpacing: 1.2 });
  const out = [
    ["Real-time global satellite AIS", "commercial only — we use free coastal and port-call data and say so"],
    ["Licensed route assessments", "paywalled, and we will not scrape"],
    ["Trade execution and clearing", "we advise; a human and a broker execute"],
    ["Charter party and laytime workflow", "adjacent, valuable, a different product"],
    ["Container, tanker, gas, breakbulk", "dry bulk only — focus is the point"],
  ];
  out.forEach(([a, b], i) => {
    const y = 2.95 + i * 0.68;
    s.addText(a, { x: 7.38, y, w: 5.05, h: 0.3, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 12, bold: true, color: TXT });
    s.addText(b, { x: 7.38, y: y + 0.27, w: 5.05, h: 0.32, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 10.5, color: MUTE });
  });
  s.addText("Rule: if it does not change the decision memo, it is not built before SIH.", {
    x: 7.1, y: 6.56, w: 5.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 11, italic: true, color: TEAL });
  stamp(s);
}

/* ─────────────────────────── 16 CLOSE ─────────────────────────── */
{
  const s = slide(null);
  s.addText("Freight stops being a daily purchase", {
    x: MG, y: 2.6, w: 11.5, h: 0.85, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 40, bold: true, color: TXT });
  s.addText("and becomes a managed position.", {
    x: MG, y: 3.45, w: 11.5, h: 0.85, isTextBox: true, margin: 0,
    fontFace: H, fontSize: 40, bold: true, color: AMBER });

  const closers = [
    ["A threshold, not an arrow", "optimal stopping over the laycan window"],
    ["Port physics as a constraint", "draft-limited intake, not a lookup table"],
    ["An instrument and a hedge", "the layer nobody sells this buyer"],
    ["Backtested in money", "capture ratio, with the worst quarter shown"],
  ];
  closers.forEach(([a, b], i) => {
    const x = MG + i * 3.05;
    s.addText(a, { x, y: 5.0, w: 2.8, h: 0.6, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 13, bold: true, color: TXT });
    s.addText(b, { x, y: 5.6, w: 2.8, h: 0.6, isTextBox: true, margin: 0,
      fontFace: H, fontSize: 11, color: MUTE });
  });
  s.addText("LAYCAN  ·  PS 26006  ·  Ministry of Steel / SAIL", {
    x: MG, y: 6.6, w: 8, h: 0.3, isTextBox: true, margin: 0,
    fontFace: M, fontSize: 10.5, color: DIM, charSpacing: 1.5 });
  stamp(s);
}

pres.writeFile({ fileName: process.argv[2] || "Laycan-SIH-Deck.pptx" })
    .then(f => console.log("wrote " + f));
