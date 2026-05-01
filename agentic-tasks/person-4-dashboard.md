# Person 4 — Therapist Dashboard (Role D)

You are Person 4. You own the **therapist web dashboard**. This is the "wow moment" of the demo — when judges see the full week of patient data summarised at a glance.

## Setup

- `MB_ROLE=D`
- Stack: Vite + React + TypeScript + Tailwind + shadcn/ui + Recharts + TanStack Query.
- API base URL: read from `10-spec/api-contract.md`.
- Shared types: `import type {...} from '@mindbridge/types'`.

Before starting any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

Person 5 has set up the remote `mindbridge` vault on Obsidian Sync. You connect to it — Sync runs over HTTPS so it works fine on uni wifi.

1. **Install Obsidian** desktop from obsidian.md. Sign in / create an account using the email Person 5 invited you on.
2. **Find the invited vault**: Settings → Sync → "Available remote vaults" → `mindbridge`.
3. **Connect**: paste the **end-to-end encryption password** from the team's 1Password / Bitwarden. Local path **`~/Obsidian/MindBridge-Vault`** — exact path matters because your `MB_VAULT` env var depends on it.
4. **Wait for first sync**. You should see `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`, `.claude/`.
5. **Set env vars** in `~/.claude/settings.json` per plan §3.1: `MB_ROLE=D`, `MB_VAULT=/Users/<me>/Obsidian/MindBridge-Vault`, `MB_REPO=/Users/<me>/mindbridge`. Restart Claude Code.
6. **Sync check**: create `40-handoffs/<YYYY-MM-DD>-D.md` with `connected at HH:MM, sync working`. Save. Within 30s Person 5 sees it.
7. **Slash command check**: `/board` prints the live task board.
8. **Orient yourself (role-specific)**: open `10-spec/api-contract.md` — those endpoints are what your dashboard reads from. Note the staging API URL at the top — that's what your fetch base URL points to. Read before claiming D1.

If any step fails, write `50-flags/onboard-D.md` and ping Person 5. Do not start the task queue with broken sync.

## Task queue (do in order)

### D1 — Scaffold `apps/dashboard`
`pnpm create vite apps/dashboard --template react-ts`. Wire Tailwind, shadcn/ui, TanStack Query, react-router. Mock therapist auth: hardcoded therapist ID in a header, no login screen for MVP. **Done when:** `pnpm dev` opens an empty shell with sidebar nav.

### D2 — Patient list page (`/patients`)
Sidebar list of the therapist's patients (from `GET /patients?therapistId=X` — coordinate with Person 1 if endpoint missing). Each row: name, last check-in mood (colour-coded dot), urgent flag count badge. **Done when:** seeded patient appears with correct mood colour.

### D3 — Patient detail page (`/patients/:id`)
Tabs: Overview, Conversations, Coping Plans, Activity. Header: name, last seen, **URGENT flag banner if any urgent flags exist** (red, top of page, dismissible per-flag). **Done when:** seeded patient renders with all tabs accessible.

### D4 — Mood trajectory chart (Overview tab)
Recharts line chart, last 7 days, X = date, Y = mood 1–10, hover shows the patient's note. Below: bar chart of step count if shared (else "patient has not enabled activity sharing"). **Done when:** seed data renders correctly.

### D5 — Flagged moments + key themes (Overview tab)
List of flags from `GET /flags?patientId=X`, colour-coded by severity. Each flag links to the conversation excerpt. Above: AI-generated "key themes this week" chips (work stress, sleep, etc.) from Person 2's summariser. **Done when:** clicking a flag scrolls/links to the right conversation.

### D6 — Conversations tab
List of conversations, each showing AI summary (Person 2's `summariseConversation`) + collapse to expand full transcript. Sort by recency. **Done when:** real conversation from mobile shows up here within seconds.

### D7 — Coping plans form (Coping Plans tab)
Form: trigger description (textarea) + strategy text (textarea) + active toggle. List of existing plans below, edit/delete. POST/PUT/DELETE `/coping-plans`. **Done when:** writing a plan here causes Person 2's AI to surface it in the next mobile chat.

### D8 — Polish + deploy
Loading skeletons, empty states, dark mode. Deploy to Vercel (coordinate with Person 5 on env vars). **Done when:** staging dashboard URL works and is in `10-spec/api-contract.md`.

## Cut lines
Activity bar chart → medication adherence heatmap → multi-patient compare view → real auth.

## Hard rules
- The URGENT banner is the single most important UI element. It must be impossible to miss.
- The activity panel must show "patient has not enabled sharing" when `share_with_therapist=false` — never show stale data, never imply the therapist can request access.
- All charts need a "no data yet" empty state — judges may demo on a fresh account.
