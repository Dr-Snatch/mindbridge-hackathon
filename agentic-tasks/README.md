# MindBridge — Per-Person Agentic Task Files

One file per person. Each is a self-contained brief for a Claude Code session. 3 technical roles, 2 non-technical.

| File | Role | Technical? |
|---|---|---|
| [person-1-fullstack.md](person-1-fullstack.md) | A — Fullstack Lead | ✅ Node + Express + Prisma + Postgres + Railway |
| [person-2-ai-engineer.md](person-2-ai-engineer.md) | B — AI Engineer | ✅ TypeScript library, Anthropic SDK |
| [person-3-frontend.md](person-3-frontend.md) | C — Frontend Engineer | ✅ Expo (React Native) + Vite/React |
| [person-4-designer.md](person-4-designer.md) | D — Brand & UX Designer | 🎨 Figma, Obsidian vault, component specs |
| [person-5-product.md](person-5-product.md) | E — Product & Pitch Lead | 🎯 Coordination, demo, pitch deck, vault |

## How each person uses their file

1. Open Claude Code in their machine's `mindbridge/` clone.
2. **Do the Obsidian Sync onboarding section first** — it's at the top of every file. Until the vault syncs, you can't `/claim` or `/handoff` anything.
3. Set `MB_ROLE`, `MB_VAULT`, `MB_REPO` in `~/.claude/settings.json`.
4. Paste the file's content as the opening message, or `/read` it.
5. Work the task queue top-to-bottom. `/claim` before, `/handoff` after.

## Critical ordering

- **Person E (Product Lead) goes first.** Without the vault, API contract, and infra, the other four are blocked.
- **Person A (Fullstack) and Person B (AI Engineer) go second**, in parallel. A publishes the API contract; B publishes the AI library stubs.
- **Person C (Frontend)** can scaffold immediately but meaningful work starts once A has endpoints running.
- **Person D (Designer)** starts immediately — producing specs in the vault for Person C to implement. No blocking dependency.

## Related docs

- **App architecture:** [`../docs/app-architecture.md`](../docs/app-architecture.md)
- **All Claude Code agents:** [`.claude/agents/README.md`](../.claude/agents/README.md)
