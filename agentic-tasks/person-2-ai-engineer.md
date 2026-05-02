# Person 2 — AI Engineer (Role B)

**Your job in one sentence:** Build the TypeScript AI library that is the brain of MindBridge — Person 1's API calls your functions, so your interface is a contract that others depend on.

---

## What you own
- `apps/ai/` — the entire AI library
- Every file under `apps/ai/src/`: crisis detection, conversation agent, pattern detection, coping plan retrieval, summarisation

## What you do NOT own (do not edit these)
- `apps/api/` → Person 1. If the API needs to call your function differently, write a vault task for Person 1, don't edit their code.
- `apps/mobile/` or `apps/dashboard/` → Person 3
- `prisma/` or `packages/types/` → Person 1. If you need a new field on a type, write `20-tasks/T-XXX-types.md` with `owner: A`.
- The crisis lexicon is yours to write, but any change after you ship B2 needs a new version file AND an ADR entry in `30-decisions/`.

---

## Setup (do this first)

```
MB_ROLE=B
MB_VAULT=~/Obsidian/MindBridge-Vault
MB_REPO=~/mindbridge
```

Add to `~/.claude/settings.json` under `"env"`. Then:

1. Clone the repo if you haven't: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. Install Obsidian, sign in with the email Person 5 invited you on
3. Connect to the `mindbridge` vault with the E2EE password from the team password manager. Local path: `~/Obsidian/MindBridge-Vault`
4. Wait for vault sync. Verify all 6 folders appear.
5. Write `40-handoffs/<today>-B.md` — "connected at HH:MM". Person 5 confirms within 30s.
6. Run `/board` in Claude Code.
7. **Read `10-spec/api-contract.md` AND `10-spec/data-model.md` before writing anything.** Your function signatures must match exactly what Person 1 expects to call.
8. Set your `ANTHROPIC_API_KEY` — get it from Person 5.

---

## Your library's public interface

Person 1's API will import and call exactly these functions. Do not rename them, do not change their signatures without coordinating first:

```typescript
// apps/ai/src/index.ts — everything exported from here

// Called on every patient message (hot path, must be fast)
export async function processMessage(
  messages: Message[],
  patientContext: PatientContext
): Promise<{ reply: string; isCrisis: boolean; patternTags: string[] }>

// Called synchronously BEFORE processMessage — must never be async
export function detectCrisis(
  text: string
): { isCrisis: boolean; matched: string[] }

// Called async after each turn (off the hot path)
export async function detectPatterns(
  messages: Message[]
): Promise<PatternTags>

// Called when conversation ends or every 10 turns
export async function summariseConversation(
  messages: Message[],
  patientFirstName: string
): Promise<{ summary: string; keyThemes: string[]; flags: SummaryFlag[] }>
```

**If you need to add a parameter or change a return type:** write `50-flags/interface-change-B.md`, coordinate with Person 1 before shipping. A silent interface change will break the API silently.

---

## Task queue — do these in order

### B1 — Scaffold `apps/ai`
`apps/ai/package.json` (name: `@mindbridge/ai`), `tsconfig.json`, `src/index.ts` exporting stub implementations of all 4 functions above. Stubs should return plausible-looking fake data so Person 1 can wire up the API routes without waiting for you.
**Done when:** `pnpm -F @mindbridge/api build` succeeds with your stubs imported. Write `40-handoffs/<today>-B.md` — "stubs published, safe to import @mindbridge/ai".

### B2 — Crisis detector (build this before anything else — it is the most important component in the system)

File: `apps/ai/src/crisis/detect.ts`

```typescript
export function detectCrisis(text: string): { isCrisis: boolean; matched: string[] }
```

Requirements:
- **Synchronous** — no async, no await, no Promise, no LLM call. This runs before anything else on every single message.
- **Throw-safe** — wrap the entire body in try/catch. On error: return `{isCrisis: false, matched: []}` and log the error. Never let an exception crash the API.
- **Normalise input** before matching: lowercase, strip diacritics, collapse whitespace.
- **Word boundary matching** — use regex with `\b` to avoid "I'm dying laughing" matching "dying".

Lexicon categories to cover (curate carefully, err on false positives):
- Suicidal ideation: "want to die", "don't want to be here anymore", "wish i was dead", "should just disappear", "better off without me", "end it all", "kill myself", "suicidal"
- Self-harm: "hurt myself", "cut myself", "harm myself"
- Hopelessness + plan: "no point anymore", "nothing will ever get better", "can't go on", "have a plan", "know how i'll do it"

False positives to explicitly NOT match: "dying of laughter", "killing it at work", "I could kill for a coffee", "dead tired".

Store as a versioned file: `apps/ai/src/crisis/lexicon_v1.ts`. Any future change = new version file + entry in `30-decisions/ADR-XXX-lexicon.md`.

Test file: `apps/ai/tests/crisis.test.ts` — 10 fixtures, 5 must-match and 5 must-not-match.

**Done when:** all 10 test fixtures pass. Run `pnpm -F @mindbridge/ai test`. Write `40-handoffs/<today>-B.md` — "B2 done, crisis detector live". This unblocks Person 1's crisis path and Person 3's crisis modal.

### B3 — Conversation agent + system prompt + caching

File: `apps/ai/src/conversation/agent.ts`

The main conversation function. Call `detectCrisis()` first (synchronous). If crisis: return the canned response immediately, post the flag (see B7), skip the LLM entirely.

If not crisis:
1. Build the system prompt (two cached blocks — see below)
2. Call Anthropic with `claude-sonnet-4-6`
3. Return `{reply, isCrisis: false, patternTags: []}`

**System prompt structure (critical — must use prompt caching):**
```typescript
system: [
  {
    type: "text",
    text: CORE_SYSTEM_PROMPT,           // ~400 tokens, same for all patients
    cache_control: { type: "ephemeral" }
  },
  {
    type: "text",
    text: buildPatientContextBlock(patientContext), // ~200 tokens, per-patient
    cache_control: { type: "ephemeral" }
  }
]
```

**Core system prompt persona:**
- Validate the emotion first, always, before anything else
- Reframe through questions ("Is there another way to look at that?"), never statements
- Never diagnose, prescribe, speculate about others, or discourage professional help
- Reinject disclaimer every ~5 turns: "Just a reminder: I'm here to support you between sessions, not replace your therapist."
- In CRISIS_MODE (when `conversation.crisisMode = true`): only stabilise, validate, anchor on human help — do not process emotional content

**Done when:** when you send "my friend hasn't replied, they hate me" — the reply validates the feeling first and asks a gentle question, not "you're catastrophising". Write `40-handoffs/<today>-B.md` — "B3 done, real AI replies working".

### B4 — Pattern detection

File: `apps/ai/src/patterns/detect.ts`

This runs **async, off the hot path** — it gets enqueued after the reply is sent.

```typescript
export async function detectPatterns(messages: Message[]): Promise<PatternTags>
// PatternTags: { rumination, catastrophising, anxietySpiral, mindReading, withdrawal }: boolean
```

Two-tier:
1. Keyword pass first (fast, always runs): phrase lists per category
2. Haiku judge only if keyword pass is ambiguous: `claude-haiku-4-5-20251001`, structured JSON output

Patterns to detect: rumination (repeated dwelling), catastrophising (worst-case chains), anxiety spiral (what-if chains), mind-reading (assuming others' thoughts), withdrawal (social/activity avoidance).

5 test fixtures in `apps/ai/tests/patterns.test.ts`.

**Done when:** 5 fixtures produce correct tag output. Write `40-handoffs/<today>-B.md`.

### B5 — Coping plan injection

File: `apps/ai/src/coping/retrieve.ts`

```typescript
export async function retrieveCopingPlans(
  message: string,
  plans: CopingPlan[]
): Promise<CopingPlan[]>
```

MVP: keyword/substring match between message text and `plan.trigger`. Return top 1-3 matches.

These plans get injected into the patient context block as:
```
THERAPIST'S STRATEGIES FOR THIS PATIENT:
- When: "trigger text" → Approach: "strategy text"
```

The AI must weave this naturally — never quote it directly, never say "your therapist says".

**Done when:** a plan saved by the therapist on the dashboard surfaces in the next patient chat response. Write `40-handoffs/<today>-B.md`.

### B6 — Conversation summariser

File: `apps/ai/src/summarise/conversation.ts`

Use `claude-haiku-4-5-20251001`. Output must be ≤120 words. Format:
```typescript
{ summary: string, keyThemes: string[], flags: SummaryFlag[], mood_arc: string }
```

This is what therapists read before sessions. It must be factual, never diagnostic, written in third person ("The patient discussed…").

Called by Person 1's API when conversation ends or every 10 turns. Result stored in `Conversation.aiSummary`.

**Done when:** Person 3's dashboard Conversations tab displays the summary text for a real conversation.

### B7 — Crisis canned response + flag emission

When `detectCrisis()` returns `isCrisis: true`:
1. Fetch `PatientProfile.crisisPlanText` if set (therapist's custom instructions)
2. Return the hardcoded canned response — this text is **never LLM-generated**:
   ```
   I hear you, and what you're describing sounds really painful. 
   I'm concerned about you right now.
   
   Please reach out: Crisis line: 988 (24/7) · Your therapist: [name]
   
   I've let your therapist know we're talking now.
   ```
   If `crisisPlanText` is set, append it.
3. POST to internal `POST /flags` with `{patientId, severity: "urgent", conversationId, messageId, lexiconMatch: matched.join(", ")}`

**Done when:** typing a crisis phrase in the mobile app triggers the canned response AND a red urgent banner appears on the therapist dashboard. Write `40-handoffs/<today>-B.md`.

---

## If you want to make a change that affects others

**Changing a function signature (name, parameters, return type):**
This breaks Person 1's API immediately. Write `50-flags/interface-change-B.md` with the exact before/after, coordinate with Person 1 before committing. Never silently change an interface.

**Changing the crisis lexicon after B2 is shipped:**
Create `apps/ai/src/crisis/lexicon_v2.ts`, keep `lexicon_v1.ts` unchanged. Write `30-decisions/ADR-001-lexicon-v2.md` documenting what changed and why. Update `detect.ts` to import the new version.

**Adding a new exported function:**
Fine — just add it to `apps/ai/src/index.ts` and tell Person 1 in `40-handoffs/<today>-B.md`.

**Need a new field on a database type:**
Write `20-tasks/T-XXX-new-field.md` with `owner: A` describing exactly what field you need and why. Don't edit `packages/types/` directly.

**Need to test without the full app running:**
Write test fixtures in `apps/ai/tests/`. You can test all your functions in isolation — they're pure TypeScript functions, they don't need the API or the DB running.

---

## How to handle being blocked

**Anthropic API key not working:**
Check with Person 5 — they hold the key. Check the usage cap hasn't been hit. Use a local stub in development: return `{reply: "STUB", isCrisis: false, patternTags: []}`.

**Person 1's API isn't up yet:**
You don't need it to build B2–B4. Crisis detection and pattern detection are pure functions. Build and test them independently. For B7 (flag emission), use a conditional: `if (process.env.API_URL) { await postFlag(...) }` so it degrades gracefully in tests.

**Person 1 changed the `Message` type:**
They should have notified you in `40-handoffs/`. Run `pnpm -F @mindbridge/types build`, then fix any TypeScript errors in `apps/ai/`.

---

## Cut order (apply when behind schedule)

1. Async Haiku backup crisis classifier
2. Pattern detection (B4) — keyword-only tagging is acceptable
3. Coping effectiveness tracker
4. Every-10-turns summarisation (end-of-conversation only is fine)
5. Nightly theme extractor

**Never cut:** B2 (crisis detection), B3 (conversation agent), B7 (canned response + flag). These are the demo path.

---

## Hard rules

- `detectCrisis` is **synchronous**. No async. No LLM. No exceptions.
- The canned crisis response is **hardcoded text**. Not LLM-generated. Not "lightly edited". Hardcoded.
- Every call to Anthropic that includes patient message content must include the "not a substitute for care" disclaimer in the system prompt.
- Prompt caching: `cache_control: {type: "ephemeral"}` on the system prompt and patient context blocks. Forgetting this silently doubles costs.
- Lexicon changes: new version file + ADR. Always.
- `pnpm -F @mindbridge/ai test` must pass before every `/handoff`.

---

## Useful agents

`b-crisis-detector` · `b-prompt-engineer` · `b-pattern-detector` · `b-summarizer` · `b-coping-injector` · `b-safety-auditor` · `b-cache-optimizer` · `shared-advisor`
