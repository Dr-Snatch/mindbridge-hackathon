# Person 2 — AI / Patterns (Role B)

You are Person 2. You own the **AI behaviour**: GPT-4 conversations, pattern detection, crisis safety, and conversation summarisation. Person 1's API calls into your library.

## Setup

- `MB_ROLE=B`
- Stack: TypeScript library at `apps/ai/`, imported by `apps/api`. Model: `claude-opus-4-7` via Anthropic SDK (or GPT-4 via OpenAI — coordinate with Person 5 on which key the team has).
- You're building a *library*, not a service. Export pure functions.

Before starting any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

Person 5 has set up the remote `mindbridge` vault on Obsidian Sync. You connect to it — Sync runs over HTTPS so it works on uni wifi without extra plumbing.

1. **Install Obsidian** desktop from obsidian.md. Sign in / create an account using the email Person 5 invited you on.
2. **Find the invited vault**: Settings → Sync → "Available remote vaults" → `mindbridge`.
3. **Connect**: paste the **end-to-end encryption password** from the team's 1Password / Bitwarden. Local path **`~/Obsidian/MindBridge-Vault`** — exact path matters because your `MB_VAULT` env var depends on it.
4. **Wait for first sync**. You should see `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`, `.claude/`.
5. **Set env vars** in `~/.claude/settings.json` per plan §3.1: `MB_ROLE=B`, `MB_VAULT=/Users/<me>/Obsidian/MindBridge-Vault`, `MB_REPO=/Users/<me>/mindbridge`. Restart Claude Code.
6. **Sync check**: create `40-handoffs/<YYYY-MM-DD>-B.md` with `connected at HH:MM, sync working`. Save. Within 30s Person 5 sees it.
7. **Slash command check**: `/board` prints the live task board.
8. **Orient yourself (role-specific)**: open both `10-spec/data-model.md` (entity shapes you'll reference in prompts) and `10-spec/api-contract.md` (the function signatures Person 1's API expects from your library). Read both before claiming B1.

If any step fails, write `50-flags/onboard-B.md` and ping Person 5. Do not start the task queue with broken sync.

## Task queue (do in order)

### B1 — Scaffold `apps/ai`
`apps/ai/package.json`, `tsconfig.json`, `src/index.ts` exporting the four functions below as stubs. **Done when:** `pnpm -F api build` succeeds with `import { generateReply } from '@mindbridge/ai'`.

### B2 — Crisis detector (deterministic, ship first)
`detectCrisis(text: string): { isCrisis: boolean; matched: string[] }` — keyword + regex match on suicide/self-harm phrases. Hand-curate the list from clinical sources; err on false positives. **Always ships before any LLM call.** Vitest with 10 fixtures (5 positive, 5 tricky negatives like "I'm dying laughing"). **Done when:** all 10 pass.

### B3 — System prompt + reframing
`generateReply(messages, copingPlans, patternHints): Promise<{reply, patternTags}>`. System prompt:
- validate emotion first, then question (not statement)
- if `copingPlans` has a matching trigger, weave that strategy in
- never diagnose, prescribe, or give clinical advice
- include the disclaimer reminder every ~5 turns

Use prompt caching on the system prompt + coping plans block. **Done when:** snapshot test on 5 conversation fixtures produces validating-then-questioning replies.

### B4 — Pattern detection
`detectPatterns(messages): { rumination, catastrophising, anxietySpiral, mindReading, withdrawal }: boolean`. Two-tier: deterministic keyword/structural pass first, LLM-judge second only if keyword pass is ambiguous. Returns tags written to `Conversation.pattern_tags` by Person 1's API. **Done when:** 5 hand-labelled fixtures match expected tags.

### B5 — Coping plan injection
Given current message + patient's `CopingPlan[]`, pick the most relevant trigger match (use the LLM as a classifier, cached). Surface inside the reply rather than as a separate message. **Done when:** dashboard-written plan appears in next AI reply within 1 turn.

### B6 — Conversation summariser
`summariseConversation(messages): { summary, keyThemes, flags }`. Called when conversation ends or every 10 turns. Output is what the therapist reads on the dashboard. ≤120 words. **Done when:** Person 4's dashboard displays it.

### B7 — Crisis canned response + flag emission
On `detectCrisis()` true: return a fixed canned reply (emergency contacts + therapist's per-patient crisis plan if present), AND POST to `/flags` with severity `urgent`. **Reply is hardcoded, not LLM-generated.** **Done when:** typing a crisis fixture in mobile produces both the reply and the dashboard banner.

## Cut lines
Withdrawal detection (needs multi-day data) → mind-reading nuance → adaptive learning of what works per patient.

## Hard rules
- The crisis path **never** waits on an LLM. Detect deterministically, reply with canned text.
- Every prompt that includes patient data must include the "not a substitute for professional care" disclaimer in the system prompt.
- Cache aggressively: system prompt + coping plans + patient context block. The inner conversation turns are the only uncached part.
