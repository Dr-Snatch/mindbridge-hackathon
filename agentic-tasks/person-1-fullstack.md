# Person 1 — Fullstack Lead (Role A)

You own the backend, database, infrastructure, and monorepo. You are the first technical person to start — you publish the API contract that unblocks Persons 2 and 3.

## Setup

- `MB_ROLE=A`
- Stack: Node 20, Express, Prisma, Postgres, pnpm workspaces
- You own: `apps/api/`, `packages/types/`, `prisma/`, root `package.json`, `pnpm-workspace.yaml`, `railway.toml`

Before any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

1. Install Obsidian from obsidian.md. Sign in with the email Person 5 invited you on.
2. Settings → Sync → "Available remote vaults" → `mindbridge`.
3. Paste the E2EE password from team password manager. Local path: `~/Obsidian/MindBridge-Vault`.
4. Wait for first sync — verify you see `00-meta/`, `10-spec/`, `20-tasks/`.
5. Set env vars in `~/.claude/settings.json`: `MB_ROLE=A`, `MB_VAULT=~/Obsidian/MindBridge-Vault`, `MB_REPO=~/mindbridge`.
6. Sync check: write `40-handoffs/<today>-A.md` — "connected at HH:MM". Person 5 confirms within 30s.
7. Run `/board` — should see the live task board.
8. Read `10-spec/api-contract.md` before claiming A1.

## Task queue (do in order)

### A1 — Monorepo bootstrap
`pnpm-workspace.yaml`, root `package.json` with workspace scripts, `tsconfig.base.json`, empty `apps/api/`, `apps/ai/`, `apps/mobile/`, `apps/dashboard/`, `packages/types/`. **Done when:** `pnpm install` succeeds from root.

### A2 — Prisma schema
Full schema with all entities: User, PatientProfile, Conversation, Message, DailyCheckin, CopingPlan, Flag, ConsentLog, AuditLog, ActivityLog, ActivitySharingPreference. All indexes from `docs/app-architecture.md §5`. **Done when:** `prisma migrate dev` succeeds.

### A3 — Shared types
`packages/types/src/index.ts` — TypeScript interfaces matching the Prisma schema. All request/response shapes. **Done when:** Person 2 and 3 can `import type { Message } from '@mindbridge/types'`.

### A4 — API skeleton + health check
Express app on `process.env.PORT` (default 4000). Mock auth middleware reading `X-Patient-Id` / `X-Therapist-Id` headers, validated against seeded IDs. `GET /health` returning `{status:"ok"}`. **Done when:** `curl localhost:4000/health` returns 200.

### A5 — Check-in routes
`POST /checkin`, `GET /checkin?days=7`. Persists DailyCheckin, returns 7-day trend. **Done when:** Person 3 can submit a mood and see it on the dashboard chart.

### A6 — Conversation routes
`POST /conversation`, `POST /conversation/:id/message` (calls `apps/ai`'s `processMessage`), `GET /conversation/:id`, `GET /conversations`. **Done when:** a message round-trips to Claude and back.

### A7 — Coping plans + flags + therapist routes
`POST /coping-plans`, `PATCH /coping-plans/:id`, `DELETE /coping-plans/:id`, `GET /patients/:id/coping-plans`, `POST /patients/:id/crisis-plan`. Internal: `POST /flags`, `POST /patterns`. Therapist: `GET /patients`, `GET /patients/:id`, `GET /patients/:id/flags`, `POST /flags/:id/acknowledge`. **Done when:** full demo path works end-to-end.

### A8 — Railway deploy
`apps/api/Dockerfile`, `railway.toml` (runs `prisma migrate deploy` on start). Railway Postgres + Redis services linked. Env vars set (ANTHROPIC_API_KEY from Person 5). **Done when:** `curl https://<railway-url>/health` returns 200.

### A9 — Seed data
`prisma/seed.ts` — 1 patient (Alex), 1 therapist (Dr Sarah Chen), 7 days of moods with a clear arc, 2 conversations with AI summaries baked in, 1 coping plan, 1 urgent flag. **Done when:** dashboard loads with compelling demo data on first open.

## Cut lines

Drop if behind: activity routes → medication routes → real embedding generation (use LIKE-match instead). Never cut: checkin, conversation/message, coping-plans, flags, patients endpoints.

## Hard rules

- `packages/types` is the single source of truth — update it whenever you add a field.
- Never log conversation text to stdout — it ends up in Railway logs.
- Every therapist data route calls `canTherapistSee(patientId, dataType)` before returning patient data.
- Mock auth is fine for the demo — document it clearly in comments.
- Run `pnpm -F api test` before every `/handoff`.

## Useful agents

`a-prisma-schema` · `a-route-builder` · `a-contract-enforcer` · `a-railway-deployer` · `shared-types` · `shared-advisor`
