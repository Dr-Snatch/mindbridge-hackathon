# Person 2 — AI Engineer (Role B)

You build the AI library. The API imports your functions directly — no separate service, no HTTP between them. Everything judges see in the AI responses comes from you.

---

## You own
`apps/ai/`

## You do NOT touch
`apps/api/` · `apps/mobile/` · `apps/dashboard/` · `packages/types/` · `prisma/`

---

## Setup

1. Clone: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. `cd ~/mindbridge && pnpm install`
3. Copy `.env.example` to `.env` — add `ANTHROPIC_API_KEY` (get from Arthur)
4. `pnpm -F @mindbridge/ai test` — should run (nothing passes yet)
5. Read `docs/app-architecture.md` before writing anything

---

## Your public interface — these 4 functions, exact signatures, never rename

```typescript
// apps/ai/src/index.ts

// Called on every patient message
export async function processMessage(
  messages: Message[],
  patientContext: PatientContext
): Promise<{ reply: string; isCrisis: boolean; patternTags: string[] }>

// Called synchronously BEFORE processMessage — no async, no LLM, ever
export function detectCrisis(text: string): { isCrisis: boolean; matched: string[] }

// Called after each turn (after reply is already sent)
export async function detectPatterns(messages: Message[]): Promise<PatternTags>

// Called when conversation ends
export async function summariseConversation(
  messages: Message[],
  patientFirstName: string
): Promise<{ summary: string; keyThemes: string[]; flags: SummaryFlag[] }>
```

If you need to change a signature: message Arthur before committing. A silent change breaks the API.

---

## Tasks — do in order

**1. Scaffold `apps/ai`**
`package.json` (name: `@mindbridge/ai`), `tsconfig.json`, `src/index.ts` with stub implementations of all 4 functions above. Stubs return plausible fake data — Person 1 needs to import you before you're real.
→ Done when: `pnpm -F @mindbridge/api build` succeeds with your stubs imported. **Message Arthur.**

**2. Crisis detector — build this first, it's the most important thing in the system**
File: `apps/ai/src/crisis/detect.ts`

```typescript
export function detectCrisis(text: string): { isCrisis: boolean; matched: string[] }
```

Requirements:
- **Synchronous. No async. No LLM. No network. Ever.**
- Wrap in try/catch — on error return `{isCrisis: false, matched: []}`, log the error, never throw
- Normalise input: lowercase, strip diacritics, collapse whitespace
- Use `\b` word boundaries — avoid "I'm dying laughing" matching "dying"

Lexicon to cover:
- Suicidal ideation: "want to die", "don't want to be here anymore", "wish i was dead", "should just disappear", "better off without me", "end it all", "kill myself", "suicidal"
- Self-harm: "hurt myself", "cut myself", "harm myself"
- Hopelessness + plan: "no point anymore", "nothing will ever get better", "can't go on", "have a plan", "know how i'll do it"

Must NOT match: "dying of laughter", "killing it at work", "I could kill for a coffee", "dead tired"

Store lexicon in `apps/ai/src/crisis/lexicon_v1.ts`. Any future change = new version file.

Test file: `apps/ai/tests/crisis.test.ts` — 10 fixtures: 5 must-match, 5 must-not-match.
→ Done when: all 10 tests pass. **Message Arthur** — this unblocks Person 1's crisis path and Person 3's crisis modal.

**3. Conversation agent + system prompt**
File: `apps/ai/src/conversation/agent.ts`

Flow:
1. Call `detectCrisis(latestMessage)` first
2. If crisis: return canned response (hardcoded text, never LLM), flag will be created by the API
3. If not crisis: fetch active coping plans for this patient, do a simple substring match against the message text, inject matching ones into the patient context block
4. One Anthropic call with `claude-sonnet-4-6`
5. Return `{reply, isCrisis: false, patternTags: []}`

System prompt structure (use prompt caching):
```typescript
system: [
  {
    type: "text",
    text: CORE_SYSTEM_PROMPT,  // ~400 tokens, same for all patients
    cache_control: { type: "ephemeral" }
  },
  {
    type: "text",
    text: buildPatientContext(patientContext),  // ~200 tokens, per-patient
    cache_control: { type: "ephemeral" }
  }
]
```

Core system prompt persona:
- Validate the emotion first, always, before anything else
- Reframe through questions ("Is there another way to look at that?"), never statements
- Never diagnose, prescribe, speculate about others, or discourage professional help
- Reinject disclaimer every ~5 turns: "Just a reminder: I'm here to support you between sessions, not replace your therapist."
- Include coping plans as: `THERAPIST'S STRATEGIES: When: [trigger] → Approach: [strategy]`
  The AI must weave them naturally — never quote them directly, never say "your therapist says"

Canned crisis response (hardcoded, never edit this without telling Arthur):
```
I hear you, and what you're describing sounds really painful.
I'm concerned about you right now.

Please reach out: Crisis line: 988 (24/7) · Your therapist: [name]

I've let your therapist know we're talking now.
```

→ Done when: "my friend hasn't replied, they hate me" → reply validates first, then asks a gentle question. **Message Arthur.**

**4. Pattern detection**
File: `apps/ai/src/patterns/detect.ts`

```typescript
export async function detectPatterns(messages: Message[]): Promise<PatternTags>
// PatternTags: { rumination: boolean, catastrophising: boolean, anxietySpiral: boolean, mindReading: boolean, withdrawal: boolean }
```

Keyword-only pass. No LLM needed for the demo.
- Rumination: "keeps thinking", "can't stop thinking", "going around in circles", repeated dwelling on same topic
- Catastrophising: "everything is ruined", "it's all over", worst-case language
- Mind-reading: "they think", "they must hate", "everyone thinks", "I know they"
- Anxiety spiral: "what if", "and then what if", chained what-if questions
- Withdrawal: "staying home", "don't want to see", "cancelled", "didn't go"

5 test fixtures in `apps/ai/tests/patterns.test.ts`.
→ Done when: 5 fixtures pass.

**5. Coping plan retrieval**
File: `apps/ai/src/coping/retrieve.ts`

```typescript
export function retrieveCopingPlans(message: string, plans: CopingPlan[]): CopingPlan[]
```

Simple substring match: if `message.toLowerCase()` contains words from `plan.trigger.toLowerCase()`, return it. Top 3 max. Synchronous, no LLM, no embeddings.
→ Done when: a plan saved by the therapist surfaces in the next patient chat that matches the trigger.

**6. Conversation summariser**
File: `apps/ai/src/summarise/conversation.ts`

Use `claude-haiku-4-5-20251001`. Output ≤120 words. Third person ("The patient discussed..."). Never diagnostic. Returns:
```typescript
{ summary: string, keyThemes: string[], flags: SummaryFlag[] }
```
→ Done when: dashboard Conversations tab shows summary text for a real conversation.

**7. Crisis canned response + flag emission**
When `detectCrisis()` returns true inside `processMessage`:
1. Fetch `PatientProfile.crisisPlanText` if set, append to canned response
2. Return the hardcoded canned response
3. Signal to the API to POST /flags (Person 1 handles the actual DB write — you just set `isCrisis: true` in the return value)
→ Done when: crisis phrase → canned response in chat + urgent banner on dashboard. **Message Arthur.**

---

## Rules

- `detectCrisis` is synchronous. No async. No LLM. No exceptions.
- The canned crisis response is hardcoded. Not LLM-generated. Not "lightly edited". Hardcoded.
- Every Anthropic call that includes patient message content must include "not a substitute for care" in the system prompt.
- Use `cache_control: {type: "ephemeral"}` on system prompt and patient context blocks. Forgetting this silently doubles costs.
- `pnpm -F @mindbridge/ai test` passes before you call any task done.

## Stuck? Message Arthur.
