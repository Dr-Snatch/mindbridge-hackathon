# Person 5 — Product & Pitch Lead (Role E)

You own **coordination, the vault, the demo, and the story**. You unblock everyone, manage the task board, write the pitch deck, and make sure the 90-second demo is flawless. You go first — nothing else starts until you've set up the vault and published the API contract.

## Setup

- `MB_ROLE=E` — unrestricted write access everywhere
- Your tools: Obsidian vault, Claude Code, GitHub, `scripts/sync.sh`
- You are the only person who edits: `10-spec/`, `00-meta/people.md`, root configs, `README.md`, `agentic-tasks/`

Before any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Your first 2 hours (everyone is blocked until you finish these)

### E0 — Obsidian Sync infrastructure
Create a remote vault called `mindbridge` on Obsidian Sync. Set a strong E2EE password. Save the password in the team password manager. Invite all 4 teammates by email. **Done when:** you see `mindbridge` in your Available Remote Vaults.

### E1 — Vault bootstrap
Create the folder structure in `~/Obsidian/MindBridge-Vault/`:
```
00-meta/people.md        ← who's who, MB_ROLE assignments
10-spec/                 ← API contract, data model, brand guidelines (Person 4 fills this)
20-tasks/                ← task files (you seed these in E5)
30-decisions/            ← ADRs (append-only)
40-handoffs/             ← sync notes
50-flags/                ← blockers and urgent issues
.claude/                 ← shared slash commands
```
**Done when:** all teammates see this structure when they connect.

### E2 — Repo bootstrap
Create the monorepo skeleton (Person 1 will fill it): `pnpm-workspace.yaml`, root `package.json`, `tsconfig.base.json`, empty `apps/` and `packages/` directories, `docker-compose.yml` for local Postgres + Redis. **Done when:** `pnpm install` works from root.

### E3 — API contract (blocking everyone)
Write `10-spec/api-contract.md` with every endpoint, method, request body, and response shape from `docs/app-architecture.md §8`. This is what Persons 1, 3, and 4 build against. **Done when:** you've reviewed it with Person 1 and it's published to the vault.

### E4 — Shared `.claude/` config
Vault `.claude/` with slash command stubs: `/claim`, `/handoff`, `/blocked`, `/board`, `/standup`. These can be simple Bash scripts or Claude Code custom commands. **Done when:** any teammate can run `/board` and see the task list.

### E5 — Seed task files (20 tasks minimum)
Create `20-tasks/T-001.md` through `T-020.md` (and more if needed) covering the full demo path. Assign each to a role. Each file needs: `id`, `title`, `owner`, `status`, `priority`, `demo_path`. **Done when:** `/board` shows a populated task list everyone can claim from.

## Ongoing (every 2 hours for the full 48h)

### E6 — Triage loop
Read all files in `50-flags/`. Apply the rubric in order:
1. Cut the feature (not on demo path? drop it)
2. Mock the dependency (can they use hardcoded data for now?)
3. Reassign (someone has bandwidth; someone is stuck)
4. Escalate (decision needed from the whole team)

Write your triage response in the same flag file. Ping the team chat if critical.

### E7 — Schedule checkpoint
At each checkpoint (H+10, H+18, H+28, H+34, H+40), run `shared-demo-validator` or manually test the demo steps that should be working. If a checkpoint fails, triage immediately — don't wait until the next cycle.

## Later tasks

### E8 — Staging infra
Set up Railway (Postgres + Redis + API service) and Vercel (dashboard). Share URLs with the team. Set ANTHROPIC_API_KEY with a hard usage cap (e.g. $20). **Done when:** `curl https://<railway>/health` returns 200.

### E9 — Demo data
Coordinate with Person 1 to run `prisma db seed` on staging. Verify the demo story loads correctly: Alex's mood arc, the crisis conversation, the urgent flag, the existing coping plan. **Done when:** dashboard opens on compelling data on first load.

### E10 — Demo script
Write the 90-second demo narration to `10-spec/demo-script.md`. Rehearse it with the team. Time it. Adjust. Every word should be deliberate. **Done when:** any team member can narrate the demo without notes.

### E11 — Pitch deck
Write the 5-slide pitch structure (problem, solution, demo, safety, team) to `10-spec/pitch-deck.md`. Coordinate with Person 4 on visuals. **Done when:** slides are ready by H+44.

### E12 — Recorded backup video
Record a clean run of all 5 demo steps on staging. This is non-negotiable — if anything breaks during the live demo, you play the video. Record at H+44 when everything is working. **Done when:** video is saved and backed up.

### E13 — Submit
Final submission by H+48. Confirm repo is public, README is clear, staging URLs are live, video is uploaded. **Done when:** submitted.

## Cut order (enforce this)

1. Activity tracking (step counts)
2. Medication reminders
3. Push notifications
4. Real JWT auth (keep mock headers)
5. Streaming SSE
6. Embedding-based coping retrieval
7. Output post-flight safety scan (L5)
8. Every-10-turns summarisation
9. Nightly theme extractor

## Hard rules

- You hold the ANTHROPIC_API_KEY. Set a hard cap before sharing with the team.
- You are the only one who edits `10-spec/` and `00-meta/` — removes all conflict surface from the vault.
- The recorded backup video is non-negotiable. Start recording at H+44 even if something's still slightly rough.
- Demo on staging (not localhost) by H+44 — give yourself 4 hours of buffer.
- Triage every 2 hours. Write a standup note even if nothing changed.

## Useful agents

`e-task-triage` · `e-demo-rehearser` · `e-seed-generator` · `e-monorepo` · `design-pitch` · `shared-standup` · `shared-advisor`
