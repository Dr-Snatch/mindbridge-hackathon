# Person 5 — Product & Pitch Lead (Role E)

Your job: make sure the demo works end-to-end and the judges understand why MindBridge matters. You're the glue — you unblock people, make product decisions, and own the pitch.

---

## You own
- `docs/` — architecture doc, any product docs
- `agentic-tasks/` — the role briefs
- `README.md`, root config files
- The Railway + Vercel accounts
- The ANTHROPIC_API_KEY (hold it, set a $20 hard cap, never paste it in chat)

## You do NOT touch
Application code in `apps/` — that's Persons 1, 2, 3.

But you can read and edit anything to unblock someone.

---

## Setup

1. Clone: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. `cd ~/mindbridge && pnpm install`
3. Share the ANTHROPIC_API_KEY with Persons 1 and 2 directly (not in chat logs)
4. Set up Railway: create Postgres + API service, set env vars
5. Set up Vercel: deploy dashboard, set `VITE_API_URL` to Railway URL

---

## First 2 hours — everyone is blocked until these are done

**E1 — Repo scaffold** (if Person 1 hasn't already started)
Make sure these exist:
- `pnpm-workspace.yaml` (workspaces: `apps/*`, `packages/*`)
- Root `package.json` with scripts: `dev:api`, `dev:dashboard`, `dev:mobile`, `build`, `db:migrate`, `db:seed`
- `tsconfig.base.json` (ES2022, NodeNext, strict: true)
- Empty dirs: `apps/api/`, `apps/ai/`, `apps/mobile/`, `apps/dashboard/`, `packages/types/`
- `docker-compose.yml` — Postgres on 5432
- `.env.example` with all required vars

→ Done when: `pnpm install` works from root.

**E2 — API contract**
File: `docs/api-contract.md`

Copy every endpoint from `docs/app-architecture.md §API surface` into a structured document. For each:
- Method + path
- Auth header required
- Request body with types
- Response shape with types

Review with Person 1 before marking done — they implement against this exactly.

→ Done when: Person 1 confirms they have what they need.

---

## Ongoing — check in every 2 hours

Run through the demo path manually. Note what's broken. Unblock whoever is stuck.

| Time | What should be working |
|------|----------------------|
| H+2  | API contract published, repo scaffold done |
| H+10 | POST /checkin works, mobile check-in screen submits |
| H+18 | Mood check-in end-to-end: mobile → DB → dashboard chart |
| H+28 | Real AI conversation: patient sends message → Claude replies |
| H+34 | Coping plans round-trip: therapist writes plan → appears in AI reply |
| H+40 | Crisis path complete: crisis message → canned reply + urgent banner |
| H+44 | Full 5-step demo on staging, with seed data |

If a checkpoint fails: figure out who's blocked, apply the unblock hierarchy below, write it in `README.md` or message the team.

---

## Unblock hierarchy (apply in order, stop when it works)

1. **Cut it** — is this task on the demo path? If not, cut it. Move on.
2. **Mock it** — can they use hardcoded data while they wait? Describe the mock for them.
3. **Reassign** — is someone blocked on another person who has bandwidth?
4. **Decide** — does this need a call? Make one. You have authority on product decisions.
5. **Escalate** — fundamental technical problem? Message the team immediately.

---

## Later tasks (H+10 onward)

**E3 — Staging infrastructure**
- Railway: Postgres + API service linked, env vars set (ANTHROPIC_API_KEY, DATABASE_URL, CORS_ORIGIN)
- Vercel: dashboard deployed, VITE_API_URL set to Railway URL
- Set ANTHROPIC_MAX_SPEND=20 hard cap in Railway env

→ Done when: `curl https://<railway>/health` returns 200 AND `https://<vercel>/` loads.

**E4 — Seed data on staging**
After Person 1 ships the seed script, run `pnpm db:seed` against Railway. Verify: open the dashboard and see Alex's mood arc, the urgent crisis flag, the conversation summary, the coping plan. This is what judges see.

**E5 — Demo script**
File: `docs/demo-script.md`

Write the exact 90-second narration. Format:
```
[ACTION: what you click/type]
"Narration you say out loud"
[Expected result: what should appear]
```

Cover all 5 demo steps. Time it. Aim for 80–90 seconds. Rehearse with the team.

**E6 — Pitch deck outline**
File: `docs/pitch-deck.md`

5 slides, 3-minute presentation:
1. The problem — "167 hours of darkness" (30s)
2. The solution — side-by-side app + dashboard (30s)
3. Live demo (60–90s)
4. Safety — deterministic crisis path, never diagnoses (20s)
5. Team (10s)

Coordinate with Person 4 on companion name and visual style.

**E7 — Backup recording**
Record a clean run of all 5 demo steps on staging. If the live demo breaks, play this. Record at H+44 when everything is confirmed working.

**E8 — Submit**
- Confirm repo is public
- README has staging URLs and setup instructions
- Submission form filled
- Video uploaded/linked
→ Done when: submitted before H+48.

---

## What you can decide alone

- Which features to cut
- Task reassignment
- Whether a mock is acceptable for the demo
- Demo data choices
- Submission timing

**Talk to Arthur first:**
- Cutting anything on the 5-step demo path
- Spending above the $20 API cap
- Any change to the crisis path or safety disclaimers

---

## Cut order (apply when behind, no debate)

1. Activity tracking
2. Medication reminders
3. Push notifications
4. Real JWT auth (keep mock headers)
5. Streaming SSE (non-streaming is fine)
6. Embedding-based coping retrieval (LIKE-match is fine)
7. Output post-flight safety scan
8. Every-10-turns summarisation (end-of-conversation only is fine)
9. Nightly theme extractor

**Never cut:** the 5 demo path steps, the disclaimer banner, the crisis path, the backup recording.

## Stuck? Message Arthur.
