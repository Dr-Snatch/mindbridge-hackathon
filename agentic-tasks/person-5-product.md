# Person 5 — Product & Pitch Lead (Role E)

**Your job in one sentence:** Make sure the team never gets stuck, the demo works end-to-end by H+44, and the judges understand why MindBridge matters.

---

## What you own
- `10-spec/` in the vault — API contract, data model, demo script, pitch deck outline
- `00-meta/` in the vault — who's who, role assignments
- `20-tasks/` in the vault — the task board (you seed it, everyone else uses it)
- `30-decisions/`, `40-handoffs/`, `50-flags/` — coordination infrastructure
- Root repo files: `README.md`, `agentic-tasks/`, `docs/`, root configs, `pnpm-lock.yaml`
- Railway and Vercel accounts + the ANTHROPIC_API_KEY

## What you do NOT own
- Application code in `apps/` — that's Persons 1, 2, 3
- Component specs and UX flows — Person 4 writes those in `10-spec/`
- The AI library — Person 2 owns that

**But you can read and edit anything.** MB_ROLE=E means unrestricted. Use this power for unblocking, not for "improving" other people's work without asking.

---

## Setup (do this first — everyone else is blocked until you do)

```
MB_ROLE=E
MB_VAULT=~/Obsidian/MindBridge-Vault
MB_REPO=~/mindbridge
```

1. Install Obsidian from obsidian.md. Create an account if you don't have one.
2. Create a new remote vault: Settings → Sync → Create new vault → name it `mindbridge` → set a strong E2EE password → **save this password in a team password manager immediately** (if you lose it, the vault is unrecoverable)
3. Invite all 4 teammates by the email addresses you have for them
4. Set up the local vault at `~/Obsidian/MindBridge-Vault`
5. Add env vars to `~/.claude/settings.json` under `"env"`
6. Write `40-handoffs/<today>-E.md` — "vault up at HH:MM, invites sent"

---

## Your first 2 hours — everyone is blocked until these are done

### E0 — Vault folder structure
In `~/Obsidian/MindBridge-Vault`, create:
```
00-meta/
  people.md      ← MB_ROLE assignments and team contact info
10-spec/         ← API contract, data model, brand guidelines (Person 4 fills in), demo script
20-tasks/        ← you'll seed task files here in E5
30-decisions/    ← ADRs, append-only
40-handoffs/     ← end-of-shift notes, sync confirmations
50-flags/        ← blockers, urgent issues, decisions needed
.claude/         ← shared slash commands
```
**Done when:** you've confirmed at least 2 teammates can see this structure after connecting.

### E1 — Repo bootstrap
In the GitHub repo, create the skeleton structure that Person 1 will flesh out:
- `pnpm-workspace.yaml` (list `apps/*` and `packages/*`)
- Root `package.json` with scripts: `dev:api`, `dev:dashboard`, `dev:mobile`, `build`, `db:migrate`, `db:seed`
- `tsconfig.base.json` (ES2022, NodeNext, strict: true)
- Empty directories: `apps/api/`, `apps/ai/`, `apps/mobile/`, `apps/dashboard/`, `packages/types/`
- `docker-compose.yml` — Postgres on 5432, Redis on 6379 (for local development)

Commit and push. **Done when:** `pnpm install` works from root. Write `40-handoffs/<today>-E.md`.

### E2 — API contract (this is the most blocking task)
File: `10-spec/api-contract.md`

Copy every endpoint from `docs/app-architecture.md §8` into a structured document. For each endpoint include:
- Method + path
- Auth: `X-Patient-Id` or `X-Therapist-Id` header
- Request body (with types)
- Response shape (with types)
- Notes (e.g. "returns SSE stream", "internal endpoint called by apps/ai")

Review it with Person 1 before marking done — they will implement this exactly.

**Done when:** Person 1 confirms they have what they need to start A4. This is the single most important document you'll produce.

### E3 — Slash commands
In the vault's `.claude/` folder, create simple slash command scripts:
- `/board` — lists all task files in `20-tasks/` with their `status` field
- `/claim T-XXX` — sets `status: in_progress` and `owner: [role]` in the task file
- `/handoff T-XXX` — sets `status: done`, prompts for notes
- `/blocked T-XXX <reason>` — sets `status: blocked`, creates a `50-flags/` entry
- `/standup` — calls the `shared-standup` agent

These can be shell scripts or Claude Code custom commands. **Done when:** any teammate can run `/board` and see tasks.

### E4 — Seed task files
Create at least 20 task files in `20-tasks/`. Name them `T-001.md` through `T-020.md`. Assign each to a role (A, B, C, D, or E). Map directly to the task queues in each person's brief.

Template for each file:
```markdown
---
id: T-001
title: Monorepo bootstrap
owner: A
status: unassigned
priority: must
demo_path: false
---

Brief description of the task. Link to the relevant section of the person's brief.
```

**Done when:** `/board` shows a populated list covering all 5 demo steps.

---

## Ongoing every 2 hours

### E-triage — Review `50-flags/` and unblock the team

Read every new file in `50-flags/`. Apply this rubric in order, stop when you find an answer:

1. **Cut it** — is this task on the demo path? If not, mark it `status: cut` and move on.
2. **Mock it** — can they use hardcoded data or a stub while they wait? Write the mock spec for them.
3. **Reassign** — is someone blocked waiting on another person? Does the owner have bandwidth right now?
4. **Decide** — does this need a team decision? Write it up clearly and make a call (you have authority to make product decisions during the hackathon).
5. **Escalate** — is this a fundamental technical problem? Ping the team chat immediately.

Write your triage response in the flag file. Flag as resolved or escalated. Move on.

### E-checkpoint — Check schedule at each milestone

| Time | What should be working |
|------|----------------------|
| H+2 | API contract published, vault up, repo scaffold done |
| H+10 | POST /checkin works, mobile check-in submits |
| H+18 | Mood check-in end-to-end: mobile → DB → dashboard chart |
| H+28 | Real AI conversation: patient sends message → Claude replies |
| H+34 | Coping plans round-trip: therapist writes plan → appears in AI reply |
| H+40 | Crisis path complete: crisis message → canned reply + urgent banner |
| H+44 | Full 5-step demo on staging, with seed data |

At each checkpoint: run `shared-demo-validator` or manually test the steps that should work. If a checkpoint fails, triage immediately. Write the result in `40-handoffs/<today>-E.md`.

---

## Later tasks (H+10 onward)

### E5 — Staging infrastructure
- Railway: create account (or use existing), set up Postgres service, Redis service, API service. Set env vars: `ANTHROPIC_API_KEY` (set a hard spend cap — $20 maximum), `NODE_ENV=production`, `CORS_ORIGIN` (Vercel URL).
- Vercel: deploy the dashboard. Set `VITE_API_URL` to the Railway URL.
- Share both URLs in `40-handoffs/<today>-E.md` so the whole team can test on staging.

**Done when:** `curl https://<railway>/health` returns 200 AND `https://<vercel>/` loads the dashboard.

### E6 — Demo data on staging
After Person 1 ships A9 (seed data), run `pnpm db:seed` against the Railway database. Verify: open the dashboard and see Alex's mood arc, the urgent crisis flag, the conversation summary, the coping plan. This is what judges will see.

**Done when:** the dashboard tells Alex's story on first load.

### E7 — Demo script
File: `10-spec/demo-script.md`

Write the exact narration for the 90-second live demo. Every sentence deliberate. Format:
```
[ACTION: what you click/type]
"Narration you say out loud"
[Expected result: what should appear]
```

Cover all 5 demo steps. Time it (aim for 80–90 seconds). Rehearse with the team. Adjust.

**Done when:** any team member can narrate the demo from memory in under 90 seconds.

### E8 — Pitch deck
File: `10-spec/pitch-deck.md`

5 slides (3-minute presentation):
1. The problem — "167 hours of darkness" (30s)
2. The solution — side-by-side: app + dashboard (30s)
3. [Live demo] — use the actual product (60–90s)
4. Safety — deterministic crisis path, 6 layers, never diagnoses (20s)
5. Team (10s)

Coordinate with Person 4 on the visual style. The `design-pitch` agent has a full script template.

**Done when:** slides are ready by H+44.

### E9 — Recorded backup video
Record a clean run of all 5 demo steps on staging. This is not optional — if the live demo breaks, you play this video.

Timing: record at H+44 when everything is confirmed working. Record again if something changes.

**Done when:** video is saved, backed up in at least 2 places, and you've watched it back to confirm it's usable.

### E10 — Submit
- Confirm repo is public on GitHub
- README has the staging URLs and setup instructions
- Submission form completed
- Video uploaded/linked

**Done when:** submitted by H+48.

---

## Your decision authority

You have authority to make these decisions alone without a team vote:
- Which features to cut (apply the cut order)
- Task assignment and reassignment
- Whether a mock/stub is acceptable
- Demo data choices
- Submission timing

Bring these to the team before deciding:
- Cutting anything on the demo path
- Changing the API contract after H+4
- Spending above the $20 API key cap
- Any decision that affects safety (crisis path, consent, disclaimers)

---

## Cut order (you enforce this, no debate)

When the team is behind, cut in this order. Never reverse a cut.

1. Activity tracking (step counts, ActivityLog, ActivitySharingPreference)
2. Medication reminders
3. Push notifications (FCM)
4. Real JWT auth — keep mock `X-Patient-Id` headers
5. Streaming SSE — non-streaming JSON reply is fine
6. Embedding-based coping plan retrieval — LIKE-match is fine
7. Output post-flight safety scan (Layer 5)
8. Every-10-turns summarisation — end-of-conversation only is fine
9. Nightly theme extractor

**Never cut:** the 5 demo path steps. The recorded backup video. The disclaimer banner. The crisis path.

---

## Hard rules

- Hold the ANTHROPIC_API_KEY. Set a hard usage cap (Railway env var `ANTHROPIC_MAX_SPEND=20`). Never share the raw key in Slack or chat.
- You are the only person who edits `10-spec/` (except brand guidelines which Person 4 fills in) and `00-meta/`. This prevents vault conflicts.
- Recorded backup video: non-negotiable. Record it at H+44.
- Demo on staging, not localhost, by H+44.
- Triage every 2 hours. Write a `40-handoffs/<today>-E.md` note even if nothing changed — the team needs to know you're watching.

---

## Useful agents

`e-task-triage` · `e-demo-rehearser` · `e-seed-generator` · `e-monorepo` · `design-pitch` · `shared-standup` · `shared-demo-validator` · `shared-advisor`
