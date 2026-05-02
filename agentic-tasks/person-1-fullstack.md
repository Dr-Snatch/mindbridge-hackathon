# Person 1 — Fullstack Lead

You build and deploy the API and database. Everything routes through you — the other three people depend on your endpoints being up and returning the right shapes.

---

## You own
`apps/api/` · `packages/types/` · `prisma/` · root config files (`package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `docker-compose.yml`, `railway.toml`)

## You do NOT touch
`apps/ai/` · `apps/mobile/` · `apps/dashboard/` · vault spec files in `10-spec/`

---

## Setup

1. Clone: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. `cd ~/mindbridge && pnpm install`
3. Copy `.env.example` to `.env` — fill in `DATABASE_URL` (local Postgres) and `ANTHROPIC_API_KEY` (get from Arthur)
4. `pnpm db:migrate` to set up local DB
5. `pnpm db:seed` to load demo data
6. `pnpm dev:api` — should start on port 4000
7. `curl localhost:4000/health` should return `{"status":"ok"}`
8. Read `10-spec/api-contract.md` in the vault before writing any routes — that's the contract everyone builds against

---

## Tasks — do in order

**1. Monorepo bootstrap**
`pnpm-workspace.yaml`, root `package.json`, `tsconfig.base.json`, `docker-compose.yml` (Postgres + Redis). Empty `apps/` and `packages/` dirs.
→ Done when: `pnpm install` works from root.

**2. Prisma schema**
All entities from `docs/app-architecture.md §5`: User, PatientProfile, Conversation, Message, DailyCheckin, CopingPlan, Flag, ConsentLog, AuditLog, ActivityLog. All indexes too.
→ Done when: `npx prisma migrate dev --name init` succeeds.

**3. Shared types**
`packages/types/src/index.ts` — TypeScript interfaces for every entity, every request body, every response shape.
→ Done when: `pnpm -F @mindbridge/types build` succeeds. **Message Arthur** — Person 2 and 3 unblock immediately.

**4. API skeleton**
Express on `process.env.PORT ?? 4000`. Mock auth: read `X-Patient-Id` / `X-Therapist-Id` headers, validate against known seeded IDs, return 401 if missing. `GET /health` → `{status:"ok"}`.
→ Done when: `curl -H "X-Patient-Id: patient-1" localhost:4000/health` returns 200.

**5. Check-in routes**
`POST /checkin` `{moodScore, notes}` → DailyCheckin + 7-day trend. `GET /checkin?days=7` → DailyCheckin[].
→ Done when: POST returns 201 with checkin + weekTrend array. **Message Arthur.**

**6. Conversation routes**
`POST /conversation` → Conversation. `POST /conversation/:id/message` `{text}` → calls `apps/ai` `processMessage`, persists messages, returns `{message, isCrisis}`. `GET /conversation/:id`. `GET /conversations`.
→ Done when: message round-trips through the AI stub and back. **Message Arthur.**

**7. Coping plans + flags + therapist routes**
Full list in `10-spec/api-contract.md`. Key ones: `GET /patients`, `GET /patients/:id`, `GET /patients/:id/flags?status=unack`, `POST /flags/:id/acknowledge`, `POST /coping-plans`, `PATCH /coping-plans/:id`.
→ Done when: all routes return correct shapes. **Message Arthur.**

**8. Railway deploy**
`Dockerfile` + `railway.toml` (start cmd: `prisma migrate deploy && node dist/index.js`). Railway Postgres + Redis linked. Env vars set.
→ Done when: `curl https://<railway-url>/health` returns 200. Share URL with Arthur.

**9. Seed data**
`prisma/seed.ts` — patient Alex (id: `patient-1`), therapist Dr Sarah Chen (id: `therapist-1`), 7 mood check-ins (arc: 6→5→7→3→4→4→3), 2 conversations with `aiSummary` populated, 1 coping plan, 1 urgent flag.
→ Done when: dashboard shows Alex's story on first load.

---

## Rules

- If you add a field to Prisma, update `packages/types` in the same commit and message Arthur
- Never log message content to stdout
- Every therapist route checks `canTherapistSee(patientId, dataType)` before returning patient data
- `pnpm -F api test` passes before you consider a task done
- Breaking API changes (renamed route, changed response shape): message Arthur before deploying

## Stuck? Message Arthur.
