# MindBridge — Per-Person Agentic Task Files

One file per person. Each is a self-contained brief that can be pasted into a Claude Code session. Match humans to roles however you want — the role queues are skill-shaped, not name-shaped.

| File | Role | Stack |
|---|---|---|
| [person-1-backend-api.md](person-1-backend-api.md) | A — Backend / API | Node + Express + Prisma + Postgres |
| [person-2-ai-patterns.md](person-2-ai-patterns.md) | B — AI / Patterns | TS library, Anthropic or OpenAI SDK |
| [person-3-mobile.md](person-3-mobile.md) | C — Patient mobile | Expo (React Native) + NativeWind |
| [person-4-dashboard.md](person-4-dashboard.md) | D — Therapist dashboard | Vite + React + Tailwind + shadcn |
| [person-5-coordinator.md](person-5-coordinator.md) | E — Integrator + vault triage | pnpm workspaces, Railway, Vercel |

## How each person uses their file

1. Open Claude Code in their machine's `mindbridge/` clone.
2. **Do the Obsidian Sync onboarding section first** — it's at the top of every person-N file, right above the task queue. Until the vault syncs to your machine, you can't `/claim` or `/handoff` anything.
3. Set `MB_ROLE`, `MB_VAULT`, `MB_REPO` in their per-machine `~/.claude/settings.json` (see plan §3.1).
4. Paste their file's content as the opening message — or `/read /Users/arthur/mindbridge/agentic-tasks/person-N-*.md`.
5. Work the task queue top-to-bottom. `/claim` before, `/handoff` after.

## Critical ordering

- **Person 5 (E) goes first.** Without the vault, repo, and `api-contract.md`, the other four are blocked.
- **Person 1 (A) and Person 2 (B) go second**, in parallel. They both need to publish working contracts that 3 and 4 consume.
- **Person 3 (C) and Person 4 (D)** can scaffold immediately but their meaningful work starts when 1+2 have stubs deployed to staging.

## Related docs

- **Team coordination plan** — `/Users/arthur/.claude-account1/plans/can-we-make-a-snoopy-glacier.md`
- **App architecture & agentic workflows** — [`../docs/app-architecture.md`](../docs/app-architecture.md) — the deep technical spec: orchestration, sync vs async paths, safety layers, memory model, named agentic components (Companion, Watcher, Bridge, Scribe, Sentinel), MVP cuts.

Read the architecture doc before claiming any task — your role's deliverable depends on the contracts it defines.
