# Person 5 — Integrator / Coordinator (Role E)

You are Person 5. You own **glue, infra, demo, and vault triage**. You're the only person who edits `10-spec/` and `00-meta/people.md`. You unblock everyone else. By H+44 the demo must run end-to-end on staging — that's on you.

## Setup

- `MB_ROLE=E`
- You can write to all of `MB_VAULT/`. Everyone else is restricted.
- Stack: pnpm workspaces, Railway (API), Vercel (dashboard), Supabase or Railway Postgres, GitHub Actions (optional).

You do not "claim" tasks the same way. You triage them.

## Task queue (do in order)

### E0 — Obsidian Sync infrastructure (BEFORE everything else)

You're the only person with the Obsidian Sync subscription. The other 4 are blocked until you set up the remote vault and send invites.

1. **Install Obsidian** desktop. Create local folder `~/Obsidian/MindBridge-Vault` and open it as a vault (this initialises `.obsidian/`).
2. **Verify your Sync subscription** is active at obsidian.md/sync.
3. **Create remote vault**: Settings → Sync → "Create new remote vault". Name: `mindbridge`. Set an **end-to-end encryption password** (long, random) and save it to a 1Password / Bitwarden item shared with the team. **Never put the password inside the vault itself.**
4. **Configure what syncs** (Settings → Sync, toggle each):
   - Sync notes (markdown + attachments) ✓
   - Sync `.obsidian/plugins/` ✓ (so Dataview installs everywhere)
   - Sync `.obsidian/snippets/` ✓
   - Sync core plugin settings ✓
   - **Do NOT sync** `.obsidian/workspace.json` (per-machine UI state — would create needless conflicts)
5. **Invite the other 4** by their Obsidian account email. To each person send (in 1Password share + team chat):
   - their role letter (A/B/C/D),
   - the vault name `mindbridge`,
   - the E2EE password (via 1Password share, not plaintext),
   - the local path they should choose: `~/Obsidian/MindBridge-Vault`,
   - a link to their `agentic-tasks/person-N-*.md` brief.
6. Proceed to E1 immediately — the folder structure you create syncs down to each person as they accept the invitation.
7. **Pre-flight test** (run once at least one other person has connected): create `00-meta/sync-test.md`. Verify they see it within 30s. Have them append a line. Verify you see it. Delete the file. Verify the delete propagates. **Do not unblock the team for task work until this passes.**

Block here. Nothing in the plan works until sync works.

### E1 — Vault bootstrap (hour 0)
Create the vault structure from §2 of the plan: `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`. Drop in `00-meta/README.md`, `00-meta/conventions.md` (frontmatter spec, hard rules), `00-meta/people.md` (5 rows: name, role, current task, machine). **Done when:** all 5 people see the vault sync in Obsidian within 60s.

### E2 — Repo bootstrap (hour 0–1)
At `/Users/arthur/mindbridge/`: `git init`, `pnpm init`, `pnpm-workspace.yaml` covering `apps/*` and `packages/*`. Root `tsconfig.base.json`, `.gitignore`, `.editorconfig`, `package.json` scripts (`dev`, `build`, `typecheck`, `test`). Create empty `apps/{api,ai,mobile,dashboard}` and `packages/types` placeholders. `infra/docker-compose.yml` with Postgres. **Done when:** `pnpm install && pnpm -r typecheck` succeeds across empty workspaces.

### E3 — `.claude/` shared config (hour 0–1)
In the vault, create `.claude/settings.json` with the four hooks from the plan (§3.3) and `.claude/commands/{claim,handoff,blocked,board,standup,adr}.md`. Each command is a small bash/python script that munges YAML frontmatter. Create `.claude/agents/triage.md` (your coordinator agent — only you should run it). Test each hook fires before declaring done.

### E4 — API contract (hour 1–2, **blocking everyone else**)
Write `10-spec/api-contract.md`: every endpoint, request/response shape, status codes. Once published, ping all four others in `50-flags/` so they can start. Generate matching TS types in `packages/types/src/index.ts`. **Done when:** Person 1 says "I have my targets" and Person 3+4 are unblocked on integration.

### E5 — Seed 15 task files (hour 1–2)
For each role's queue (A1–A8, B1–B7, C1–C7, D1–D8), create `20-tasks/T-XXX-<slug>.md` with proper frontmatter. Pre-assign `owner` to the right role. **Done when:** `_board.md` Dataview view shows 30+ todos grouped by owner.

### E6 — Staging infra (hour 2–6)
Provision Railway (Postgres + API service), Vercel project (dashboard). Copy env vars to a shared `1Password` or encrypted note (NOT the vault). Set up a single OpenAI/Anthropic key with usage cap. **Done when:** Person 1 can `git push` API and Person 4 can deploy dashboard. Both URLs go in `api-contract.md`.

### E7 — Triage every 2 hours
Run your `triage` agent. It scans `20-tasks/` for `status: blocked` or stalled `in-progress`, posts a digest to `50-flags/`, and lists rebalancing suggestions. You decide: reassign, descope, escalate, cut. Update `00-meta/people.md` if assignments change.

### E8 — Demo data (hour 36–40)
Write a richer seed script: 1 patient, 7 days of varied moods (3 good, 2 mid, 2 bad), 3 conversations (one casual, one with a coping-plan-triggered reframe, one with a crisis flag), 2 active coping plans, step data showing a sedentary streak. **Done when:** demo path runs convincingly without any "lorem ipsum" feel.

### E9 — Demo script + recorded backup (hour 44–47)
Write `10-spec/demo-script.md`: minute-by-minute, who clicks what, what they say. Screen-record a successful run on staging. If the live demo fails on stage, the recorded backup plays. **Done when:** dry run succeeds twice in a row.

### E10 — Submit (hour 47–48)
Push final builds, fill out hackathon submission form, post the URLs.

## Triage decision rubric

When something's stuck, in priority order:
1. **Cut features** — see each person's cut lines. Step count, medication, push notifications, real auth go first.
2. **Mock the dependency** — if Person 1's API is slow, Person 3+4 use mock data. Re-integrate later.
3. **Reassign** — pull a person off a nice-to-have to help with a must-have.
4. **Escalate to humans** — if it's blocked on an external service (Apple Health key, Twilio account), tell the team out loud.

## Hard rules
- The demo runs end-to-end on staging by H+44 with **at least an hour** of buffer. If H+40 hits and any must-have isn't working, cut it without asking.
- You hold the OpenAI/Anthropic API key. Set a hard usage cap. If anyone burns through credits in a runaway loop, kill the key and rotate.
- The recorded backup video is non-negotiable. Live demos fail. Always have the recording.
- Do not let perfect be the enemy of working. A janky end-to-end flow beats four polished features that don't connect.
