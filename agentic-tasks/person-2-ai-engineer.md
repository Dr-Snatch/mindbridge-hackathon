# Person 2 — AI Engineer (Role B)

You own the **brain** of MindBridge — the TypeScript library that handles all AI behaviour: conversations, crisis detection, pattern recognition, and summarisation. Person 1's API imports your library directly.

## Setup

- `MB_ROLE=B`
- Stack: TypeScript library at `apps/ai/`, imported by `apps/api`. Model: `claude-sonnet-4-6` for conversation, `claude-haiku-4-5-20251001` for async tasks.
- You own: `apps/ai/` — export pure functions, no HTTP server.

Before any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

1. Install Obsidian from obsidian.md. Sign in with the email Person 5 invited you on.
2. Settings → Sync → "Available remote vaults" → `mindbridge`.
3. Paste the E2EE password from team password manager. Local path: `~/Obsidian/MindBridge-Vault`.
4. Wait for first sync — verify you see `00-meta/`, `10-spec/`, `20-tasks/`.
5. Set env vars in `~/.claude/settings.json`: `MB_ROLE=B`, `MB_VAULT=~/Obsidian/MindBridge-Vault`, `MB_REPO=~/mindbridge`.
6. Sync check: write `40-handoffs/<today>-B.md` — "connected at HH:MM". Person 5 confirms within 30s.
7. Run `/board` — should see the live task board.
8. Read both `10-spec/api-contract.md` and `10-spec/data-model.md` before claiming B1 — your function signatures must match what Person 1's API expects.

## Task queue (do in order)

### B1 — Scaffold `apps/ai`
`apps/ai/package.json`, `tsconfig.json`, `src/index.ts` exporting stubs: `processMessage`, `detectCrisis`, `detectPatterns`, `summariseConversation`. **Done when:** `pnpm -F @mindbridge/api build` succeeds importing your stubs.

### B2 — Crisis detector (ship first, everything else depends on this)
`detectCrisis(text: string): { isCrisis: boolean; matched: string[] }` — synchronous, deterministic, throw-safe. Curated lexicon of suicide/self-harm/hopelessness phrases with word-boundary regex to avoid false positives. Vitest with 10 fixtures (5 positive, 5 tricky negatives). **Done when:** all 10 pass. This ships before any LLM call.

### B3 — Conversation agent + system prompt
`processMessage(messages, patientContext): Promise<{reply, isCrisis, patternTags}>`. System prompt: validate emotion first, then reframe through questions. Never diagnose/prescribe. Disclaimer reinjected every ~5 turns. Prompt caching on system prompt + patient context block. **Done when:** mind-reading fixture produces validating-then-questioning reply.

### B4 — Pattern detection
`detectPatterns(messages): PatternTags` — two-tier: keyword pass first, Haiku judge if ambiguous. Detect: rumination, catastrophising, anxietySpiral, mindReading, withdrawal. Tags written to `Conversation.patternTags`. **Done when:** 5 labelled fixtures match expected tags.

### B5 — Coping plan injection
Given current message + patient's `CopingPlan[]`, pick the most relevant plan (keyword match for MVP, embeddings if time allows). Surface inside the reply in the AI's voice — never "your therapist said". **Done when:** dashboard-written plan appears in next AI reply.

### B6 — Conversation summariser
`summariseConversation(messages): { summary, keyThemes, flags }`. Haiku model. ≤120 words. Output is what therapists read. **Done when:** Person 3's dashboard displays it on the Conversations tab.

### B7 — Crisis canned response + flag emission
On `detectCrisis() = true`: return hardcoded canned response (acknowledges distress, directs to crisis line + therapist, therapist's per-patient crisis plan if set). POST to `/flags` with `severity: urgent`. **Done when:** crisis fixture in mobile produces the response AND the dashboard urgent banner.

## Cut lines

Async LLM backup classifier → adaptive pattern learning → coping effectiveness tracker. Never cut: B2 (crisis), B3 (conversation), B7 (crisis canned response + flag).

## Hard rules

- Crisis path is **synchronous**. No await, no LLM. If it throws, catch and return `{isCrisis: false}` — never crash the API.
- The canned response is **hardcoded text**. Never LLM-generated, not even "lightly edited".
- Every prompt that sees patient data includes the "not a substitute for professional care" disclaimer.
- Cache aggressively: system prompt + patient context block. Conversation history is never cached.
- Lexicon changes need a new version file (`lexicon_v1.ts`) and an ADR entry.

## Useful agents

`b-crisis-detector` · `b-prompt-engineer` · `b-pattern-detector` · `b-summarizer` · `b-coping-injector` · `b-safety-auditor` · `b-cache-optimizer` · `shared-advisor`
