# Person 1 — Fullstack Lead (Role A)

**Your job in one sentence:** Build and deploy the API that all three other technical people depend on. You are the plumbing — everything routes through you.

---

## What you own
- `apps/api/` — the Express server
- `packages/types/` — shared TypeScript types used by everyone
- `prisma/` — database schema and migrations
- Root config files: `package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `docker-compose.yml`, `railway.toml`

## What you do NOT own (do not edit these)
- `apps/ai/` → that's Person 2
- `apps/mobile/` or `apps/dashboard/` → that's Person 3
- Vault spec files (`10-spec/api-contract.md`, `10-spec/data-model.md`) → Person 5 writes the initial spec, you implement it
- Design tokens or component specs → Person 4

**If you accidentally edit outside your folder**, the role-fence hook will block you and tell you what to do. Don't bypass it — open a vault task instead.

---

## Setup (do this first, before writing any code)

```
MB_ROLE=A
MB_VAULT=~/Obsidian/MindBridge-Vault
MB_REPO=~/mindbridge
```

Add these to `~/.claude/settings.json` under `"env"`. Then:

1. Clone the repo: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. Install Obsidian (obsidian.md), sign in with the email Person 5 invited you on
3. Settings → Sync → Available remote vaults → `mindbridge` → connect with the E2EE password from the team password manager → local path `~/Obsidian/MindBridge-Vault`
4. Wait for vault to sync. Verify you see `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`
5. Write `40-handoffs/<today>-A.md` with "connected at HH:MM" — Person 5 should confirm within 30 seconds
6. Run `/board` in Claude Code — you should see the task board
7. **Read `10-spec/api-contract.md` before writing a single line of API code** — this is what Person 3 will build against

---

## Task queue — do these in order

Each task has a hard "Done when" test. Do not move to the next task until that test passes.

### A1 — Monorepo bootstrap
Create: `pnpm-workspace.yaml`, root `package.json` (with `dev:api`, `build`, `db:migrate`, `db:seed` scripts), `tsconfig.base.json`, empty directories `apps/api/`, `apps/ai/`, `apps/mobile/`, `apps/dashboard/`, `packages/types/`, `docker-compose.yml` (Postgres on 5432, Redis on 6379).
**Done when:** `pnpm install` runs from root with no errors. Post `40-handoffs/<today>-A.md` confirming — Person 2 and 3 can now scaffold their apps.

### A2 — Prisma schema
File: `prisma/schema.prisma`. Entities (all fields listed in `docs/app-architecture.md §5`):
- User, PatientProfile, Conversation, Message
- DailyCheckin, CopingPlan, Flag
- ConsentLog (append-only), AuditLog (append-only)
- ActivityLog, ActivitySharingPreference

Required indexes: `(patientId, startedAt desc)` on Conversation, `(conversationId, timestamp)` on Message, `(patientId, date desc)` on DailyCheckin, `(patientId, acknowledgedAt, severity)` on Flag.
**Done when:** `npx prisma migrate dev --name init` succeeds and creates all tables.

### A3 — Shared types
File: `packages/types/src/index.ts`. TypeScript interfaces for every entity, every request body, every response shape. Use the `shared-types` agent for the complete definition list.
**Done when:** `pnpm -F @mindbridge/types build` succeeds AND you can confirm `import type { Message } from '@mindbridge/types'` works in a test file. Write a note in `40-handoffs/<today>-A.md` saying types are published — Person 2 and 3 unblock immediately.

### A4 — API skeleton + mock auth
Express app on `process.env.PORT ?? 4000`. Middleware: JSON body parser, CORS (allow `localhost:5173` and the Vercel dashboard URL), mock auth that reads `X-Patient-Id` and `X-Therapist-Id` headers and validates them against known seeded IDs. If the header is missing or unrecognised, return 401. `GET /health` → `{status: "ok", ts: Date.now()}`.
**Done when:** `curl -H "X-Patient-Id: patient-1" localhost:4000/health` returns 200.

### A5 — Check-in routes
- `POST /checkin` body `{moodScore: 1-10, notes?: string}` → creates DailyCheckin, returns `{checkin, weekTrend: DailyCheckin[]}` (last 7 days)
- `GET /checkin?days=7` → DailyCheckin[]

**Done when:** `curl -X POST -H "X-Patient-Id: patient-1" -H "Content-Type: application/json" -d '{"moodScore":3,"notes":"stressed"}' localhost:4000/checkin` returns 201 with the checkin and a 7-day trend array. Ping Person 3 in the vault — they can now build the check-in screen against a real endpoint.

### A6 — Conversation routes
- `POST /conversation` → creates Conversation record, returns `{id, patientId, startedAt}`
- `POST /conversation/:id/message` body `{text}` → calls `apps/ai`'s `processMessage`, persists both user and assistant Message rows, returns `{message: Message, isCrisis: boolean}`
- `GET /conversation/:id` → Conversation + messages array
- `GET /conversations?limit=10` → Conversation[]

For now, stub `processMessage` if Person 2 isn't done yet: return `{reply: "I hear you. Tell me more.", isCrisis: false}`. Replace the stub as soon as Person 2's library is ready.
**Done when:** the stub round-trip works end-to-end and you've written a note in the vault saying the real integration is ready once Person 2 finishes B3.

### A7 — Coping plans, flags, and therapist routes
Patient-facing:
- `POST /consent` body `{scope, granted}` → creates ConsentLog
- `GET /me` → User + preferences

Therapist-facing:
- `GET /patients` → PatientSummary[] (name, lastMoodScore, unacknowledgedFlagCount)
- `GET /patients/:id` → PatientDetail (week check-ins, summaries, flags, coping plans)
- `GET /patients/:id/conversations` → Conversation[] with summaries
- `GET /patients/:id/flags?status=unack` → Flag[]
- `POST /flags/:id/acknowledge` → updates Flag.acknowledgedAt
- `GET /patients/:id/coping-plans` → CopingPlan[]
- `POST /coping-plans` body `{patientId, trigger, strategy}` → CopingPlan
- `PATCH /coping-plans/:id` → CopingPlan
- `DELETE /coping-plans/:id` → 204
- `POST /patients/:id/crisis-plan` body `{text}` → updates PatientProfile.crisisPlanText

Internal (called by apps/ai):
- `POST /flags` body `{patientId, severity, conversationId, messageId, lexiconMatch}` → Flag
- `POST /patterns` body `{messageId, tags}` → updates Message.patternTags

**Done when:** all routes return correct shapes. Run the `a-contract-enforcer` agent to check. Notify Person 3 in the vault — they can now wire the full dashboard and coping plan flow.

### A8 — Railway deployment
- `apps/api/Dockerfile` (Node 20, pnpm install, build, `prisma generate`)
- `railway.toml` — start command: `npx prisma migrate deploy && node dist/index.js`, healthcheck: `/health`
- On Railway: create Postgres service, Redis service, API service. Link them. Set env vars: `ANTHROPIC_API_KEY` (get from Person 5), `CORS_ORIGIN` (Vercel dashboard URL), `NODE_ENV=production`

**Done when:** `curl https://<railway-url>/health` returns 200. Post the URL in `40-handoffs/<today>-A.md`.

### A9 — Seed data
File: `prisma/seed.ts`. Creates: 1 therapist (`id: "therapist-1"`, Dr Sarah Chen), 1 patient (`id: "patient-1"`, Alex), 7 mood check-ins (arc: 6→5→7→3→4→4→3), 2 conversations with `aiSummary` already populated, 1 coping plan (trigger: "assumes others are judging them", strategy: "ask what evidence do I have"), 1 urgent flag with `lexiconMatch: "don't want to be here anymore"`.
**Done when:** `pnpm db:seed` succeeds and the dashboard loads with Alex's story on first open.

---

## If you want to make a change that affects others

**Changing a shared type in `packages/types/`:**
Edit the file, rebuild (`pnpm -F @mindbridge/types build`), write a note in `40-handoffs/<today>-A.md` describing exactly what changed and what Person 2 and 3 need to update. Do this immediately — silent type changes break everyone.

**Changing an API endpoint shape (method, URL, request/response):**
This is a breaking change. Write a `30-decisions/ADR-XXX-<description>.md` explaining why, post it in `50-flags/breaking-change-A.md`, and sync with Person 3 before deploying. Never rename or remove a working endpoint mid-hackathon without coordinating.

**Adding a new dependency to root `package.json`:**
You own root config. Add it, run `pnpm install` from root, commit `pnpm-lock.yaml`. Notify the team.

**Need Person 2 to change their library interface:**
Write `20-tasks/T-XXX-ai-interface-change.md` with `owner: B`. Describe exactly what function signature you need and why. Don't edit `apps/ai/` directly.

**Need Person 3 to implement something differently:**
Coordinate via vault — write a note in `40-handoffs/<today>-A.md`. Never edit `apps/mobile/` or `apps/dashboard/`.

---

## How to handle being blocked

**Person 2's AI library isn't ready and you need the conversation route:**
Use the stub: `{reply: "I hear you.", isCrisis: false}`. Document it with a `// TODO: replace stub when B3 is done` comment. Don't wait.

**Railway deploy is failing:**
Run locally first. Check Railway logs with `railway logs --service api`. Common fixes: `prisma generate` not running, `DATABASE_URL` not injected, port not reading from `process.env.PORT`.

**Postgres migration fails on Railway:**
Never run `prisma migrate reset` on Railway — it drops all data. Fix the migration file, push a new one with `prisma migrate dev --name fix-<thing>`.

**Something outside your folder needs to change:**
Write a vault task for the owner. Flag it as urgent if it's blocking the demo path.

---

## Cut order (apply when behind schedule)

Drop in this order, never go back:
1. ActivityLog and ActivitySharingPreference routes
2. Medication and appointment tables/routes
3. Real embedding generation for coping plans (use LIKE-match instead)
4. AuditLog entries on non-critical routes

**Never cut:** checkin routes, conversation/message route, coping-plans CRUD, flags routes, patients therapist routes. These are the demo path.

---

## Hard rules

- `packages/types` is the single source of truth. If you add a field to Prisma, add it to types the same commit.
- Never log `message.text` or conversation content to stdout — Railway logs are not private.
- Every therapist route that returns patient data calls `canTherapistSee(patientId, dataType)` first.
- Mock auth (`X-Patient-Id` headers) is acceptable for the demo — document it clearly.
- `pnpm -F api test` must pass before every `/handoff`.
- `prisma migrate deploy` (not `dev`) runs on Railway startup.

---

## Useful agents

`a-prisma-schema` · `a-route-builder` · `a-contract-enforcer` · `a-railway-deployer` · `shared-types` · `shared-advisor`
