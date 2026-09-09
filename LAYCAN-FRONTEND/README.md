# LAYCAN · Bulk Freight Decision Intelligence Surface

An autonomous maritime procurement and optimal chartering desk dashboard built for **Smart India Hackathon (Ministry of Steel / Steel Authority of India Limited - SAIL)**, Problem Statement **26006**.

## Overview
LAYCAN answers one critical question in real time: **Fix the vessel today, or wait?**

This frontend is a reactive, high-performance command deck built with **TanStack Start**, **React 19**, and **Tailwind CSS v4**. It visualizes:
- **Optimal Stopping Decision Sheet**: Dynamic calculation of reservation prices, recommendation triggers (`FIX_NOW` vs `WAIT`), and potential freight savings.
- **Agent Audit Trail**: Multi-agent consensus (Market Specialist, Port Constraints Engineer, Hydrostatics Validator, Risk Auditor) with immutable rationale and confidence intervals.
- **Naval Hydrostatics & Physics**: Dynamic calculation of Dock Water Allowance (DWA), freshwater/brackish draft penalties, lightering thresholds, and berth constraints across major Indian ports (Paradip, Vizag, Gangavaram, Haldia).
- **Scenario Testing ("What-if")**: Stress-test bunker surcharges, market rate volatility shocks, and destination port demurrage delays.
- **5-Year Backtest Evidence**: Defensible walk-forward simulation against naive day-0 booking benchmarks.

---

## Tech Stack
- **Framework**: [TanStack Start](https://tanstack.com/start) with React 19
- **Routing**: TanStack Router (file-based routes in `src/routes/`)
- **Styling**: Tailwind CSS v4, Radix UI primitives, Lucide React icons
- **Data & Visualizations**: TanStack Query v5, Recharts
- **Build Engine**: Vite 8 with TypeScript 5.8

---

## Getting Started

### Prerequisites
- Node.js (>= 20.x) or Bun (>= 1.2.x)
- npm or bun package manager

### Installation
```bash
# Using npm
npm install

# Or using bun
bun install
```

### Running Locally
```bash
# Start the local development server
npm run dev

# Or with bun
bun dev
```
Open your browser at [http://localhost:3000](http://localhost:3000) (or the Vite dev port displayed in your terminal).

### Production Build
```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

---

## Directory Structure
```
LAYCAN-FRONTEND/
├── public/                 # Static assets & maritime favicon
├── src/
│   ├── components/ui/      # Radix UI and customized component library
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility helpers and error wrappers
│   ├── routes/             # TanStack Start file-based routes
│   │   ├── __root.tsx      # Root route shell with HTML/head definitions
│   │   └── index.tsx       # Main LAYCAN decision intelligence cockpit
│   ├── server.ts           # Server entry point
│   ├── start.ts            # TanStack Start configuration
│   └── styles.css          # Tailwind CSS v4 styling rules
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite build configuration
```

---

## License
Proprietary — Smart India Hackathon 2026 / Ministry of Steel (SAIL). All rights reserved.
