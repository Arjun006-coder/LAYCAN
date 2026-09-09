# LAYCAN Frontend Developer Guide

This repository contains the interactive decision intelligence command center for **LAYCAN** (Built for Ministry of Steel / SAIL · Smart India Hackathon).

## Tech Stack
- **Framework**: TanStack Start (React 19 + TanStack Router)
- **Styling**: Tailwind CSS v4 + PostCSS / Radix UI + Lucide Icons
- **State & Data**: TanStack Query v5 + React Hook Form + Zod
- **Charts & Physics Visuals**: Recharts
- **Build Tooling**: Vite 8 + TypeScript

## Key Commands
- `npm run dev` or `bun dev`: Starts the local development server at `http://localhost:3000` or `http://localhost:5173`.
- `npm run build` or `bun run build`: Creates an optimized production build.
- `npm run preview` or `bun run preview`: Previews the production build locally.
- `npm run lint`: Checks for lint issues with ESLint.

## Project Structure
- `src/routes/`: File-based routing powered by TanStack Router (`__root.tsx`, `index.tsx`).
- `src/components/ui/`: Reusable primitive components (buttons, dialogs, sliders, etc.).
- `src/server.ts`: Server entrypoint and SSR handlers.
- `src/styles.css`: Tailwind v4 theme and custom design system rules.
