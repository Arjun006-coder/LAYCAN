# LAYCAN

**A freight decision engine for bulk cargo importers.**

Smart India Hackathon 2026 · Problem Statement **26006** · Ministry of Steel / SAIL · Transportation & Logistics

---

Ocean freight rates are close to a random walk, and a liquid forward market already prices them better than any model we could build. So this is not a freight forecasting project.

LAYCAN answers the questions a bulk importer actually faces every morning:

- **Fix today, or wait?** — a reservation rate, recomputed daily, from an optimal-stopping policy over the laycan window
- **Which vessel class, to which port?** — a mixed-integer program with draft, LOA, beam and gear feasibility as hard constraints
- **Spot, trip charter, or COA?** — an instrument portfolio on an expected-cost / tail-risk frontier
- **How much risk are we carrying?** — hedge sizing against the nearest liquid FFA, with basis risk stated honestly

And it proves itself the only way that counts: **a backtest of decisions, not of forecasts.** What would this policy have paid per tonne, versus a buyer who fixes on the day the plant asks?

## Two rules that define the architecture

**The language models may not emit a numeral.** Every figure comes from a deterministic, unit-tested, versioned solver and carries provenance to its source, licence and timestamp. Agents gather, interpret, challenge and explain. A CI check fails the build on violation.

**A Critic agent attacks every recommendation before it ships.** Out-of-distribution checks, regime-change tests, forward-curve disagreement, single-source dependency ablation, calibration drift. When it cannot get comfortable, the product says so and escalates to a human.

## Documentation

| Document | Read it when |
|---|---|
| **[docs/MASTER-PLAN.md](docs/MASTER-PLAN.md)** | The single source of truth — scope, architecture, maths, sprint plan, demo script, business case |
| **[docs/VERIFY-FIRST.md](docs/VERIFY-FIRST.md)** | ⚠️ **Before anything ships.** Blocking factual verification checklist |
| **[docs/DOMAIN-PRIMER.md](docs/DOMAIN-PRIMER.md)** | Week 1, everyone. Shipping vocabulary, voyage maths, market drivers |
| **[docs/research/](docs/research/)** | Raw data-source research with confidence tags |
| **[pitch/](pitch/)** | Judging deck and investor one-pager |

## ⚠️ Read before quoting any number

This plan was written **without live internet access**. The design stands on its own; the facts do not. Port drafts, LOA limits, handling rates, sailing distances, market sizes and competitor details are **approximate and unverified**.

`docs/VERIFY-FIRST.md` is roughly two days of work and it is the highest-value two days on the project. A judge who catches one wrong port draft will discount everything else you say.

## Quick start

```bash
docker compose up          # Postgres+TimescaleDB, Redis, API, web
make demo                  # seeded snapshot, byte-identical every run
open http://localhost:3000
```

Demo mode runs entirely from a frozen snapshot committed to the repo — no network calls. Venue wifi has ended more good projects than bad code has.

## Stack

Python 3.11 · FastAPI · Postgres + TimescaleDB · DuckDB · OR-Tools CP-SAT · networkx · LangGraph · Next.js + TypeScript · Docker Compose

Deliberately not used: Kafka, Kubernetes, microservices, a vector database. Knowing what not to build is part of the plan.

## Status

Pre-week-1. Nothing built yet. Start with `docs/MASTER-PLAN.md` §14.
