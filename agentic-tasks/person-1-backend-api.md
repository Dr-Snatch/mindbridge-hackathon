# Person 1 — Backend / API (Role A)

You are Person 1. You own the **API and database**. Other people will be hitting your endpoints, so your job is to publish a working contract early and keep it stable.

## Setup

- `MB_ROLE=A`
- `MB_REPO=/Users/<me>/mindbridge`
- `MB_VAULT=/Users/<me>/Obsidian/MindBridge-Vault`
- Stack: Node 20 + Express + Prisma + Postgres (local Docker) + Vitest

Before starting any task: run `/claim <task-id>` in the vault. After finishing: run `/handoff <task-id>` and write what works, what's stubbed, and how to test it.

## Obsidian Sync onboarding (do this BEFORE hour 0)

Person 5 has set up the remote `mindbridge` vault on Obsidian Sync. You connect to it — Sync runs over HTTPS so it works on uni wifi without Tailscale/Syncthing fuss.

1. **Install Obsidian** desktop from obsidian.md. Sign in / create an account using the email Person 5 invited you on.
2. **Find the invited vault**: Settings → Sync → "Available remote vaults" → `mindbridge`.
3. **Connect**: select `mindbridge` → paste the **end-to-end encryption password** Person 5 shared via the team's 1Password / Bitwarden (never inside the vault). Choose local path **`~/Obsidian/MindBridge-Vault`** — this exact path matters because your `MB_VAULT` env var points there.
4. **Wait for first sync**. You should see `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`, and a `.claude/` directory.
5. **Set env vars** in `~/.claude/settings.json` per plan §3.1: `MB_ROLE=A`, `MB_VAULT=/Users/<me>/Obsidian/MindBridge-Vault`, `MB_REPO=/Users/<me>/mindbridge`. Restart Claude Code so it picks them up.
6. **Sync check**: create `40-handoffs/<YYYY-MM-DD>-A.md` with `connected at HH:MM, sync working`. Save. Within 30s Person 5 sees it.
7. **Slash command check**: `/board` prints the live task board.
8. **Orient yourself (role-specific)**: open `10-spec/api-contract.md` — that document is the canonical list of endpoints you're implementing. Read it before claiming A1.

If any step fails, write `50-flags/onboard-A.md` and ping Person 5. Do not start the task queue with broken sync.

## Task queue (do in order)

### A1 — Scaffold `apps/api`
Create `apps/api/` with `package.json`, `tsconfig.json`, `src/index.ts` (Express boot on PORT=4000), `.env.example` with `DATABASE_URL`, `OPENAI_API_KEY`. Add `docker-compose.yml` at repo root with Postgres 16. **Done when:** `pnpm dev` starts API and `GET /health` returns `{ok:true}`.

### A2 — Prisma schema
Translate spec §6 into `apps/api/prisma/schema.prisma`: `User, PatientProfile, Conversation, Message, DailyCheckin, CopingPlan, MedicationLog, ActivityLog, ActivitySharingPreference, Appointment, Flag`. Run `prisma migrate dev --name init`. Generate seed script with 1 therapist + 1 patient + 7 days of check-ins. **Done when:** `pnpm db:seed` populates a working dataset.

### A3 — API contract handshake
Read `MB_VAULT/10-spec/api-contract.md`. If it doesn't exist, ping Role E in `50-flags/`. Once it exists, generate matching TS types in `packages/types/src/index.ts`.

### A4 — `/checkin` route
`POST /checkin` body `{patientId, moodScore, notes}` → creates `DailyCheckin`. `GET /checkin?patientId=X&days=7` returns last N. Vitest hitting a real test DB. **Done when:** mobile (Person 3) can post and dashboard (Person 4) can read.

### A5 — `/conversation` routes
`POST /conversation` (start), `POST /conversation/:id/message` (append + call AI service from Person 2), `GET /conversation/:id` (full thread + summary). The AI call is a single function `generateReply(messages, copingPlans)` imported from `apps/ai`. **Done when:** mobile chat works end-to-end against staging.

### A6 — `/coping-plans` routes
CRUD scoped to `(therapistId, patientId)`. Active plans only. **Done when:** dashboard form (Person 4) can write and Person 2's AI service can read.

### A7 — `/flags` routes
`POST /flags` (called by AI service on crisis/pattern detection), `GET /flags?patientId=X`. Severity enum: `info | moderate | urgent`. **Done when:** dashboard (Person 4) shows urgent banner.

### A8 — Deploy to Railway
Coordinate with Person 5 on env vars. **Done when:** staging API responds at the URL written in `10-spec/api-contract.md`.

## Cut lines (drop in this order if behind)
medication routes → activity routes → appointment routes → real auth (mock with hardcoded patient/therapist IDs in headers).

## Hard rules
- Never edit `10-spec/` or `00-meta/people.md` (Role E only).
- Update `packages/types` whenever you change a route shape — Person 3 and Person 4 depend on it.
