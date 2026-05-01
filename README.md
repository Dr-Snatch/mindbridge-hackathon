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

We're matching humans to roles based on skill, not assigning by name. If you're not sure which role suits you, ask in the team chat.

| Role | What you own | Stack |
|---|---|---|
| **A — Backend / API** | The Express + Prisma + Postgres API that everything talks to. You own the endpoints other people consume. | Node 20, Express, Prisma, Postgres |
| **B — AI / Patterns** | The library that handles conversations, pattern detection, crisis safety, and summarising. The "brain." | TypeScript, Anthropic SDK |
| **C — Patient Mobile** | The patient-facing mobile app — check-in, chat, crisis modal. The app judges see first. | Expo (React Native), NativeWind |
| **D — Therapist Dashboard** | The web dashboard — mood charts, conversation summaries, coping plan editor. The "wow" reveal. | Vite, React, Tailwind, Recharts |
| **E — Coordinator / Integrator** | Glue, infrastructure, deployment, vault triage, demo. Unblocks everyone else. | Whatever it takes |

Your detailed task queue is in [`agentic-tasks/person-N-*.md`](agentic-tasks/) — one file per role. Read your file before doing anything else.

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
