# MindBridge

**An AI companion that lives in the gap between therapy sessions.**

Therapy is one hour a week. The other 167 hours, your therapist is blind to what you're feeling. MindBridge is a patient-facing AI companion + a therapist-facing dashboard that bridges that gap — so the work that happens in the room can be informed by the life that happens outside it.

We're 5 people. We have 48 hours. This document is how we stay on the same page.

---

## What we're building (in one minute)

**For the patient** — a mobile app with two things:
1. A daily check-in (mood + a sentence about your day).
2. An AI you can talk to any time, especially during distress. It listens, validates, and — when appropriate — gently reframes unhelpful thought patterns. It surfaces coping strategies your therapist has written for you. If you're in crisis, it directs you to human help and tells your therapist.

**For the therapist** — a web dashboard with one job: show them their patient's week at a glance. Mood trajectory, key themes from conversations, flagged moments, somewhere to write coping strategies. They walk into the next session already knowing what's been going on.

**Demo path we're aiming for:**
1. Patient logs a mood, says "I think my friend hates me"
2. AI validates, gently reframes ("is there another reason they might not have replied?")
3. Patient writes something distressing → urgent flag fires → dashboard banner
4. Therapist sees the week's mood chart, conversation summaries, and the urgent flag
5. Therapist writes a coping plan → next time the patient chats, AI weaves it in

That's the whole demo. ~90 seconds. Anything else is gravy.

---

## The team — 5 roles

3 technical roles, 2 non-technical. Match people to roles by skill. Your detailed brief is in [`agentic-tasks/`](agentic-tasks/).

| Role | What you own | Technical? |
|---|---|---|
| **A — Fullstack Lead** | Express API, Prisma schema, Postgres DB, Railway deployment, monorepo setup, shared types | ✅ Technical |
| **B — AI Engineer** | The AI library — conversations, crisis detection, pattern recognition, coping plan injection, summarisation | ✅ Technical |
| **C — Frontend Engineer** | Both apps — patient mobile (Expo/React Native) AND therapist dashboard (Vite/React) | ✅ Technical |
| **D — Brand & UX Designer** | Visual identity, colour palette, typography, UX flows, component specs, UI copy, accessibility review | 🎨 Non-technical |
| **E — Product & Pitch Lead** | Coordination, vault management, API contract, demo script, pitch deck, recorded backup video, submission | 🎯 Non-technical |

**Critical ordering:** Person E goes first (vault + API contract). Then A and B in parallel. Then C (needs A's endpoints). D starts immediately and produces specs for C to implement.

---

## How we work together

We split coordination from code:

- **Code lives in this GitHub repo.** That's `apps/`, `packages/`, `docs/` — everything you'd expect.
- **Live coordination lives in a shared Obsidian vault** synced via Obsidian Sync. Tasks, decisions, hand-offs, the kanban board, the API contract — all in there.

```
Code = git (snapshot, slow, reviewed)
Coordination = Obsidian vault (live, fast, append-only)
```

This split matters because git merges are too slow for "I'm picking up T-014" and Obsidian is too informal for code review. Each tool does what it's good at.

### The vault structure

```
MindBridge-Vault/
├── 00-meta/         who's who, conventions
├── 10-spec/         the API contract, data model, demo script (Role E writes; everyone reads)
├── 20-tasks/        one task = one file = one owner
├── 30-decisions/    architecture decisions (append-only)
├── 40-handoffs/     end-of-shift notes, sync-test pings
├── 50-flags/        urgent cross-cutting issues
└── .claude/         shared slash commands and Claude Code hooks
```

### Slash commands (work from any Claude Code session)

- `/claim T-014` — assign yourself to a task, mark it in-progress
- `/handoff T-014` — finish a task, write what works, what's stubbed, how to test
- `/blocked T-014 <reason>` — flag a blocker, alert Role E
- `/board` — see the live state of every task
- `/standup` — generate three bullets from your in-progress tasks for the next sync

### House rules (so we don't trip over each other)

1. **One task = one file = one owner.** Never edit someone else's task file. If you have a comment, create a new task that links to theirs.
2. **Decisions and hand-offs are append-only.** New file, never edit an old one.
3. **Only Role E edits `10-spec/` and `00-meta/people.md`.** Removes the only real conflict surface.
4. **Disclaimer banner stays visible** on every screen with AI content. Non-negotiable.
5. **The crisis path never waits on an LLM.** Lexicon-only on the hot path.
6. **Cut features, not quality.** A janky end-to-end demo beats four polished features that don't connect.
7. **Stay in your folder.** Each role owns one subtree (table below). The `role-fence` hook will physically block Edits and Writes outside your folder — if you hit it, that's a signal to use the vault instead.

---

## Working alongside 4 other Claude Code sessions

5 sessions editing the same repo in parallel can wreck `main` fast — Claude tends to "tidy up" adjacent code without being asked, and overlapping edits become merge fights. Two rails keep this from happening.

### Rail 1 — file ownership, enforced by a hook

Each role owns a distinct subtree of the repo. The `PreToolUse` hook at [`.claude/hooks/role-fence.py`](.claude/hooks/role-fence.py) reads your `MB_ROLE` env var and blocks any Edit / Write / MultiEdit outside your folder.

| Role | Owns (writable) |
|---|---|
| **A — Fullstack** | `apps/api/`, `packages/types/`, `prisma/` |
| **B — AI Engineer** | `apps/ai/` |
| **C — Frontend** | `apps/mobile/`, `apps/dashboard/` |
| **D — Designer** | `packages/design-tokens/` (specs live in vault, not repo) |
| **E — Product Lead** | everywhere (docs, root configs, lockfile, README, agentic-tasks) |

Everyone can **read** anywhere. Only writes are fenced.

If you genuinely need a change outside your folder (e.g. Person 1 needs Person 5 to add a workspace package), open a vault task `20-tasks/T-XXX-<reason>.md` assigned to the file's owner. Don't try to bypass the hook — it's there because we can't review 5 streams of Claude output by eye.

### Rail 2 — sync discipline

Run [`bash scripts/sync.sh`](scripts/sync.sh) every 20–30 min, and whenever you finish a task. It does the right thing: stash, `git pull --rebase`, restore your work, push.

```
small + frequent syncs   →   small fixable conflicts
hoarding hours of work   →   merge disasters at hour 24
```

If `sync.sh` reports a real conflict, don't panic: resolve the file(s), `git add` them, `git rebase --continue`, then re-run the script. The conflict surface is small because of Rail 1.

### Single-owner hot files

A few files everyone wants to touch. Exactly one person can write each; the rest open a vault task to ask:

| File | Owner |
|---|---|
| `pnpm-lock.yaml`, root `package.json` | E |
| `packages/types/src/*` | A (everyone reads, only A writes) |
| `prisma/schema.prisma` | A |
| `docs/*`, `README.md`, `agentic-tasks/*` | E |
| `.claude/*` (hooks, shared settings) | E |

### Why no pull requests?

For a 48-hour hackathon, PR ceremony is overhead. The two rails above replace what PR review would have caught: out-of-domain edits and unsynced branches. Push directly to `main`. If something breaks the build, fix forward — `git revert` is your rollback button.

---

## Your first 30 minutes

Do these in order. If any step fails, write `50-flags/onboard-<your role>.md` and ping Role E.

1. **Get the repo.** Clone this on your machine: `git clone <url> ~/mindbridge`.
2. **Read your role brief.** Open `agentic-tasks/person-N-*.md` for your role.
3. **Read the architecture.** [`docs/app-architecture.md`](docs/app-architecture.md) — the deep technical spec. Skim it now, refer back as you build.
4. **Get on Obsidian Sync.**
   - Install Obsidian: <https://obsidian.md>
   - Sign in with the email Role E invited you on
   - Settings → Sync → "Available remote vaults" → connect to `mindbridge`
   - Paste the encryption password from the team's 1Password (Role E shared it)
   - Local path: `~/Obsidian/MindBridge-Vault` (this exact path matters)
5. **Set your env vars** in `~/.claude/settings.json`:
   ```json
   {
     "env": {
       "MB_ROLE": "<your letter A-E>",
       "MB_VAULT": "/Users/<you>/Obsidian/MindBridge-Vault",
       "MB_REPO": "/Users/<you>/mindbridge"
     }
   }
   ```
6. **Sync test.** Create `40-handoffs/<today>-<role>.md` with the line "connected at HH:MM". Save. Watch Role E confirm it appeared on their machine within 30 seconds.
7. **Slash command test.** Run `/board` in your Claude Code session — you should see the live task board.
8. **Claim your first task.** `/claim T-XXX` (Role E has seeded the board). Start.

---

## Schedule (rough, 48 hours)

| Hour | Focus | Who |
|---|---|---|
| 0–2 | Vault + repo setup, everyone onboarded, API contract published | E (the rest unblock at H+2) |
| 2–10 | API skeleton, DB schema, mock AI replies, mobile shell | A, B, C |
| 10–18 | Mood check-in works end-to-end | A, C, D |
| 18–28 | Real AI conversation + reframing + pattern detection | B, A |
| 28–34 | Therapist coping plans surface in patient chat | B, D |
| 34–40 | Crisis path: lexicon detection → urgent flag → dashboard banner | B, C, D |
| 40–44 | Seed demo data, deploy staging | E, A |
| 44–47 | Demo rehearsal + recorded backup video | All |
| 47–48 | Submit | E |

If we hit hour 40 and a must-have isn't working, we cut it without ceremony. Cut order: step counts → medication reminders → push notifications → real auth (mock with hardcoded IDs).

---

## The full demo path (must work by H+44)

This is the only thing that has to work end-to-end. Everything else is decoration.

1. Open mobile → log mood 3/10, "stressed about work" → saves to DB
2. Open chat → "my friend hasn't replied, they hate me" → AI validates and reframes (gently asks if there's another explanation)
3. Type something matching the crisis lexicon → AI surfaces emergency contacts; URGENT flag posts to dashboard
4. Open therapist dashboard → mood chart shows today; conversation summary visible; URGENT banner at top of patient detail
5. Therapist writes a coping plan ("when patient mind-reads, ask: what evidence?") → next mobile chat, AI surfaces it

If we can demo this in 90 seconds, we win regardless of what else is or isn't built.

---

## Where to find detail

| If you want to know… | Read this |
|---|---|
| What you specifically should do | [`agentic-tasks/person-N-*.md`](agentic-tasks/) |
| How the app actually works under the hood | [`docs/app-architecture.md`](docs/app-architecture.md) |
| How the team coordinates | This README + [`agentic-tasks/README.md`](agentic-tasks/README.md) |
| Live task state | The Obsidian vault, `20-tasks/_board.md` |
| Why we made some technical decision | The Obsidian vault, `30-decisions/ADR-*.md` |
| The full spec we're working from | [`docs/app-architecture.md`](docs/app-architecture.md) §0–6 |

---

## Safety statement (this matters)

We're building something that touches mental health. That comes with responsibilities even at hackathon scope:

- **The AI never diagnoses, prescribes, or discourages professional support.** Hard system-prompt rules + output post-flight checks.
- **The crisis path is deterministic** — lexicon-based, hardcoded canned response. It doesn't depend on the LLM working.
- **Consent is explicit and revocable.** Activity tracking is opt-in. Sharing with therapist is a separate opt-in. Patients can revoke either at any time.
- **No data leaves Anthropic / OpenAI / our DB.** No third-party analytics, no logging of conversation content to anywhere we don't control.
- **The disclaimer is always visible** when there's AI content on screen.

If you find yourself about to build something that bends one of these rules "just for the demo" — stop and bring it to the team. We'd rather drop a feature than ship something that could harm someone if it survived past the hackathon.

---

## Questions, blockers, panic

In order of escalation:
1. Check [`docs/app-architecture.md`](docs/app-architecture.md) — answer is probably there.
2. Check `30-decisions/` in the vault — we may have already decided.
3. Drop a flag in `50-flags/<your-issue>.md` — Role E triages every 2 hours.
4. Ping the team chat for anything blocking your hot path.

We've got this.
