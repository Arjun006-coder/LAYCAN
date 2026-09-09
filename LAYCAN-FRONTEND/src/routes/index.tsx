import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  Anchor,
  ArrowRight,
  BarChart3,
  CloudSun,
  Gauge,
  Radio,
  Scale,
  ShieldCheck,
  Ship,
  SlidersHorizontal,
  Waves,
  Zap,
} from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LAYCAN | Bulk Freight Decision Intelligence" },
      { name: "description", content: "A maritime procurement command surface for faster, defensible bulk freight chartering decisions." },
      { property: "og:title", content: "LAYCAN | Bulk Freight Decision Intelligence" },
      { property: "og:description", content: "Autonomous maritime procurement and optimal chartering intelligence for bulk cargo." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: LaycanPage,
});

const ports = [
  { name: "Paradip", code: "INPRT", draft: 16 },
  { name: "Visakhapatnam Outer", code: "INVTZ-OH", draft: 18.1 },
  { name: "Gangavaram", code: "INGAW", draft: 17.7 },
  { name: "Haldia", code: "INHAL", draft: 8.5 },
];

const vessels = [
  { vessel: "Capesize", draft: 18, nominal: 21.3, lightering: 2.9, score: 58 },
  { vessel: "Kamsarmax", draft: 15.5, nominal: 22.4, lightering: 0, score: 96 },
  { vessel: "Panamax", draft: 14.9, nominal: 22.85, lightering: 0, score: 88 },
];

const tabs = ["Decision sheet", "Agent audit", "Vessel physics", "What-if", "5Y evidence"] as const;

function Metric({ label, value, note, accent = false }: { label: string; value: string; note: string; accent?: boolean }) {
  return (
    <div className={cn("border-r-2 border-ink px-4 py-3 last:border-r-0", accent && "bg-lime")}>
      <p className="label">{label}</p>
      <p className="mt-1 font-sans text-2xl font-bold leading-none">{value}</p>
      <p className="mt-1 text-xs text-ink/60">{note}</p>
    </div>
  );
}

function LaycanPage() {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("Decision sheet");
  const [volume, setVolume] = useState(75000);
  const [days, setDays] = useState(14);
  const [shock, setShock] = useState(0);
  const [portCode, setPortCode] = useState("INPRT");
  const [confirmed, setConfirmed] = useState(false);
  const port = ports.find((item) => item.code === portCode) ?? { name: "Paradip", code: "INPRT", draft: 16 };
  const spot = 23.1 * (1 + shock / 100);
  const savings = Math.round(418000 + days * 17400 - shock * 8900);
  const recommended = port.draft < 14 ? "Handymax" : port.draft < 17.9 ? "Kamsarmax" : "Capesize";
  const chart = useMemo(() => [22.7, 22.9, 22.6, 23.1, 23.25, 23.5, 23.4, 23.85, 24.1, 24.05, 24.55, 24.8], []);

  return (
    <main className="min-h-screen bg-canvas p-2 text-ink sm:p-4 lg:p-6">
      <div className="mx-auto max-w-[1500px] overflow-hidden border-[3px] border-ink bg-paper shadow-page">
        <header className="grid border-b-[3px] border-ink lg:grid-cols-[260px_1fr_auto]">
          <div className="flex items-start justify-between bg-orange p-5 lg:border-r-[3px] lg:border-ink">
            <div>
              <h1 className="font-display text-6xl leading-[0.68] tracking-normal">LAY<br />CAN</h1>
              <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.18em]">Bulk freight decision intelligence</p>
            </div>
            <Anchor className="size-8" strokeWidth={2.5} />
          </div>
          <div className="flex flex-col justify-between gap-5 p-5">
            <div className="flex flex-wrap items-center gap-3 text-xs font-bold uppercase">
              <span className="border-2 border-ink bg-cyan px-2 py-1">SAIL · PS 26006</span>
              <span>Nomination SAIL-COK-2026-118</span>
            </div>
            <p className="max-w-3xl font-display text-3xl leading-none sm:text-4xl lg:text-5xl">Should we fix this ship today?</p>
          </div>
          <div className="flex items-center gap-3 border-t-[3px] border-ink bg-ink px-5 py-3 text-paper lg:border-l-[3px] lg:border-t-0">
            <span className="live-dot size-3 bg-lime" />
            <div><p className="text-xs font-bold uppercase">Live feed</p><p className="text-[10px] text-paper/60">4 sources · synced</p></div>
          </div>
        </header>

        <nav className="hide-scrollbar flex overflow-x-auto border-b-[3px] border-ink bg-paper" aria-label="Decision views">
          {tabs.map((tab, index) => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={cn("shrink-0 border-r-2 border-ink px-4 py-3 text-xs font-bold uppercase transition-colors", activeTab === tab ? "bg-ink text-paper" : "hover:bg-cyan")}>
              <span className="mr-2 opacity-50">0{index + 1}</span>{tab}
            </button>
          ))}
        </nav>

        <section className="grid border-b-[3px] border-ink xl:grid-cols-[300px_1fr]">
          <aside className="border-b-[3px] border-ink bg-soft p-5 xl:border-b-0 xl:border-r-[3px]">
            <div className="mb-5 flex items-center justify-between"><p className="label">Cargo nomination</p><SlidersHorizontal className="size-4" /></div>
            <div className="space-y-4">
              <label className="block"><span className="field-label">Commodity</span><select className="field"><option>Coking Coal</option><option>Thermal Coal</option><option>Iron Ore</option><option>Limestone</option></select></label>
              <label className="block"><span className="field-label">Quantity (MT)</span><input className="field" type="number" min="10000" max="200000" step="5000" value={volume} onChange={(event) => setVolume(Number(event.target.value))} /></label>
              <label className="block"><span className="field-label">Discharge</span><select className="field" value={portCode} onChange={(event) => setPortCode(event.target.value)}>{ports.map((item) => <option key={item.code} value={item.code}>{item.name} · {item.code}</option>)}</select></label>
              <label className="block"><span className="field-label">Laycan closes · {days} days</span><input className="range" type="range" min="2" max="30" value={days} onChange={(event) => setDays(Number(event.target.value))} /></label>
            </div>
            <div className="mt-5 border-2 border-ink bg-cyan p-3 shadow-hard-sm">
              <div className="flex items-center justify-between"><span className="label">Route</span><Ship className="size-4" /></div>
              <p className="mt-3 font-display text-2xl leading-none">Hay Point <ArrowRight className="mx-1 inline size-5" /> {port.name}</p>
              <p className="mt-2 text-xs font-bold uppercase">Draft limit {port.draft.toFixed(1)}m</p>
            </div>
          </aside>

          <div>
            <div className="decision-grid grid lg:grid-cols-[1.35fr_1fr]">
              <div className="relative overflow-hidden border-b-[3px] border-ink bg-lime p-6 lg:border-b-0 lg:border-r-[3px] lg:p-8">
                <p className="label">Optimal stopping policy / LSMC</p>
                <div className="mt-4 flex flex-wrap items-end justify-between gap-5">
                  <div><p className="font-display text-6xl leading-[0.8] sm:text-8xl">FIX<br />TODAY</p><p className="mt-5 max-w-md text-sm font-medium">Market indication is inside the action boundary. Lock the lift before forward momentum turns against the laycan.</p></div>
                  <div className="stamp rotate-[-5deg]">91%<span>CONFIDENCE</span></div>
                </div>
              </div>
              <div className="grid grid-cols-2 bg-paper">
                <Metric label="Market indication" value={`$${spot.toFixed(2)}`} note="per metric tonne" />
                <Metric label="Reservation rate" value="$21.42" note="spread +7.8%" />
                <Metric label="Vessel" value={recommended} note="intake optimized" accent />
                <Metric label="Timing saving" value={`$${(savings / 1000).toFixed(0)}K`} note="vs naive day-0 fix" />
              </div>
            </div>

            <div className="grid border-t-[3px] border-ink lg:grid-cols-[1.45fr_1fr]">
              <section className="border-b-[3px] border-ink p-5 lg:border-b-0 lg:border-r-[3px]">
                <div className="flex items-center justify-between"><p className="label">30-day freight trace</p><span className="text-xs font-bold text-positive">UP +4.2%</span></div>
                <div className="mt-4 flex h-40 items-end gap-1 border-b-2 border-l-2 border-ink p-2">
                  {chart.map((value, index) => <div key={index} className={cn("chart-bar flex-1 border-2 border-ink", index === 3 ? "bg-orange" : "bg-cyan")} style={{ height: `${35 + (value - 22) * 26}%`, animationDelay: `${index * 45}ms` }} title={`Day ${index * 3}: $${value}`} />)}
                </div>
                <div className="mt-2 flex justify-between text-[10px] font-bold uppercase"><span>Today</span><span>ARIMA champion · MAE 0.41</span><span>Day 30</span></div>
              </section>
              <section className="bg-orange p-5">
                <div className="flex items-center justify-between"><p className="label">Critic's red pencil</p><ShieldCheck className="size-5" /></div>
                <p className="mt-4 font-display text-3xl leading-tight">Capesize looks cheaper. It isn't.</p>
                <p className="mt-3 text-sm leading-relaxed">Its 18.0m draft breaches {port.name}'s {port.draft.toFixed(1)}m limit. Part-discharge adds <strong>$2.90/MT</strong>. {recommended} clears the berth geometry.</p>
              </section>
            </div>
          </div>
        </section>

        <section className="grid border-b-[3px] border-ink lg:grid-cols-[1.25fr_1fr]">
          <article className="border-b-[3px] border-ink p-5 lg:border-b-0 lg:border-r-[3px]">
            <div className="flex items-center gap-2"><Radio className="size-4" /><p className="label">Executive decision note · generated 14:32 UTC</p></div>
            <p className="mt-4 font-display text-3xl leading-tight sm:text-4xl">Fix a {recommended} against the current indication of ${spot.toFixed(2)}/MT.</p>
            <div className="mt-5 columns-1 gap-8 text-sm leading-relaxed sm:columns-2">
              <p>The rate sits above the LSMC reservation boundary, while the 30-day tournament projects upward pressure. Waiting offers limited optionality against a closing {days}-day laycan.</p>
              <p className="mt-3 sm:mt-0">Port physics eliminates headline-cheap Capesize tonnage. The selected class protects intake, avoids lightering, and preserves approximately ${(savings / 1000).toFixed(0)}K in timing value.</p>
            </div>
            <div className="mt-5 flex flex-wrap gap-2"><span className="tag">LOA ✓</span><span className="tag">BEAM ✓</span><span className="tag">DRAFT ✓</span><span className="tag">DWA ✓</span></div>
          </article>
          <aside className="grid grid-cols-2 bg-soft sm:grid-cols-4 lg:grid-cols-2">
            {[{ icon: Waves, label: "Wave", value: "1.8m", note: "Moderate" }, { icon: CloudSun, label: "Weather", value: "Low", note: "risk index" }, { icon: Activity, label: "BDRY", value: "$16.50", note: "+2.2% daily" }, { icon: Radio, label: "Agents", value: "4/4", note: "audit passed" }].map(({ icon: Icon, label, value, note }) => <div className="border-b-2 border-r-2 border-ink p-4" key={label}><Icon className="size-5" /><p className="mt-4 label">{label}</p><p className="font-sans text-xl font-bold">{value}</p><p className="text-xs text-ink/55">{note}</p></div>)}
          </aside>
        </section>

        <section className="border-b-[3px] border-ink p-5">
          <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="label">Vessel physics · shortlist</p><h2 className="mt-1 font-display text-4xl">Paper cheap vs port possible.</h2></div><Scale className="size-8" /></div>
          <div className="mt-5 overflow-x-auto"><table className="min-w-[720px] w-full border-collapse text-left"><thead><tr className="border-y-2 border-ink text-[10px] uppercase"><th>Class</th><th>Draft</th><th>Nominal $/MT</th><th>Lightering</th><th>Net cost</th><th>Suitability</th></tr></thead><tbody>{vessels.map((item) => { const feasible = item.draft <= port.draft; return <tr key={item.vessel} className={cn("border-b-2 border-ink", item.vessel === recommended && "bg-lime")}><td className="font-bold">{item.vessel}{item.vessel === recommended && <span className="ml-2 text-[9px]">RECOMMENDED</span>}</td><td>{item.draft.toFixed(1)}m</td><td>${item.nominal.toFixed(2)}</td><td className={!feasible ? "text-negative font-bold" : ""}>{feasible ? "$0.00" : `+$${item.lightering.toFixed(2)}`}</td><td>${(item.nominal + (feasible ? 0 : item.lightering)).toFixed(2)}</td><td><div className="h-3 w-28 border-2 border-ink bg-paper"><div className="h-full bg-cyan" style={{ width: `${feasible ? item.score : 32}%` }} /></div></td></tr>; })}</tbody></table></div>
        </section>

        <section className="grid border-b-[3px] border-ink lg:grid-cols-[1fr_1.5fr]">
          <div className="border-b-[3px] border-ink bg-cyan p-5 lg:border-b-0 lg:border-r-[3px]">
            <div className="flex items-center gap-2"><Gauge className="size-5" /><p className="label">What-if desk</p></div>
            <p className="mt-3 font-display text-3xl">Stress the recommendation.</p>
            <label className="mt-5 block"><span className="field-label">Market shock · {shock > 0 ? "+" : ""}{shock}%</span><input className="range" type="range" min="-30" max="30" step="5" value={shock} onChange={(event) => setShock(Number(event.target.value))} /></label>
            <div className="mt-5 grid grid-cols-2 gap-3"><div className="border-2 border-ink bg-paper p-3"><p className="label">Simulated rate</p><p className="text-2xl font-bold">${spot.toFixed(2)}</p></div><div className="border-2 border-ink bg-paper p-3"><p className="label">Decision</p><p className="text-2xl font-bold">{shock < -15 ? "WAIT" : "FIX"}</p></div></div>
          </div>
          <div className="p-5"><div className="flex items-center gap-2"><BarChart3 className="size-5" /><p className="label">Five-year evidence · walk-forward</p></div><div className="mt-5 grid grid-cols-2 gap-0 border-2 border-ink sm:grid-cols-4"><Metric label="Voyages" value="1,240" note="96.5M tonnes" /><Metric label="Policy edge" value="$1.84" note="saved per MT" accent /><Metric label="Net value" value="₹214.6Cr" note="simulated" /><Metric label="Capture" value="78.3%" note="of oracle" /></div><p className="mt-4 text-sm">Positive savings were maintained through the worst volatility quarter. All figures are solver-derived; the language layer only explains and challenges the result.</p></div>
        </section>

        <footer className="grid items-center gap-4 bg-orange p-5 sm:grid-cols-[1fr_auto]">
          <div><p className="label">Chartering desk verdict</p><p className="mt-1 font-display text-3xl">The window is open. The vessel fits. The rate won't wait.</p></div>
          <Button variant={confirmed ? "ink" : "default"} onClick={() => setConfirmed((value) => !value)}>{confirmed ? <ShieldCheck className="size-5" /> : <Zap className="size-5" />}{confirmed ? "FIX INSTRUCTION QUEUED" : "CONFIRM FIX TODAY"}</Button>
        </footer>
      </div>
    </main>
  );
}