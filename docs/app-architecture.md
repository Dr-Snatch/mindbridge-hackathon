# MindBridge — App Architecture & Agentic Workflows

**Status:** v0 (hackathon target). Lives in the repo, evolves via PR. Companion to `/Users/arthur/.claude-account1/plans/can-we-make-a-snoopy-glacier.md` (team coordination plan) and the per-person briefs in `agentic-tasks/`.

---

## 0. The shape of the problem

Therapy is one hour out of 168. The other 167 are dark. MindBridge fills that gap with an AI companion that talks to the patient between sessions, then surfaces clinically useful structure to the therapist.

That problem requires three things to be true at once:

1. **The patient must feel safe and heard, fast.** A reply that takes 8 seconds while someone is panicking is a failure.
2. **The therapist must trust what they see.** Summaries that hallucinate, miss crises, or smuggle in clinical advice are worse than no summary.
3. **The system must be safe by construction.** Crisis handling cannot rely on an LLM's mood. Consent cannot be implicit.

The architecture below is shaped around those three constraints in that order.

---

## 1. System overview

Three layers, two LLM callers, one source of truth.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                           │
│   ┌─────────────────────┐                ┌───────────────────────────┐  │
│   │ Patient (Expo RN)   │                │ Therapist (Vite + React)  │  │
│   │  • Daily check-in   │                │  • Patient list           │  │
│   │  • AI chat (stream) │                │  • Mood + flags + themes  │  │
│   │  • Crisis fallback  │                │  • Coping plan editor     │  │
│   └──────────┬──────────┘                └─────────────┬─────────────┘  │
└──────────────│──────────────────────────────────────────│────────────────┘
               │ HTTPS                                     │ HTTPS
               ▼                                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     API LAYER (apps/api — Express + Prisma)               │
│   /checkin   /conversation/:id/message   /coping-plans   /flags          │
│   • thin controllers                                                      │
│   • auth middleware (mock JWT for hackathon)                             │
│   • imports apps/ai as a library                                         │
└────────────┬───────────────────────────────────────────┬─────────────────┘
             │ in-process function calls                  │ enqueue
             ▼                                            ▼
┌────────────────────────────────────┐   ┌──────────────────────────────────┐
│  apps/ai — ORCHESTRATION LIBRARY   │   │  ASYNC WORKERS (BullMQ on Redis) │
│  Synchronous (hot path):           │   │  • patternDetector               │
│   1. crisisGate                    │   │  • copingEffectivenessTracker    │
│   2. contextAssembler              │   │  • conversationSummariser        │
│   3. conversationAgent (streams)   │   │  • themeExtractor (nightly)      │
│  Returns: streamed reply           │   │  • flagEscalator (10-min watcher)│
└────────────┬───────────────────────┘   └────────────────┬─────────────────┘
             │                                             │
             └───────────────────┬─────────────────────────┘
                                 ▼
              ┌────────────────────────────────────┐
              │ PERSISTENCE                         │
              │  • Postgres (Prisma)                │
              │  • Redis (cache + job queue)        │
              │  • Object store: optional, for      │
              │    long-term encrypted transcripts  │
              └────────────────────────────────────┘
                                 │
                                 ▼
              ┌────────────────────────────────────┐
              │ EXTERNAL                            │
              │  • Anthropic API (conversation,     │
              │    pattern judge, summariser)       │
              │  • OpenAI embeddings (coping        │
              │    plan retrieval, theme cluster)   │
              │  • FCM (push notifications)         │
              │  • Twilio (crisis SMS — optional)   │
              └────────────────────────────────────┘
```

**Why this shape:**
- `apps/ai` is a *library*, not a service. The API imports it. No HTTP between API and AI = no extra latency, no extra ops surface for 48h.
- The hot path (patient sends message → reply) goes through one LLM call. Every other LLM call is async.
- Async work runs on a job queue, not "fire-and-forget setTimeout". Failures get retried, the queue is observable, no work is lost.

---

## 2. Agentic architecture

The "agentic" surface is small but layered. Six components, each with one job.

| Component | Trigger | Latency budget | Model | Lives in |
|---|---|---|---|---|
| **Crisis Gate** | Every patient message, synchronous | <10 ms | Deterministic (regex + lexicon) | `apps/ai/src/crisis/detect.ts` |
| **Context Assembler** | Every patient message, synchronous | <100 ms | None — pure DB + Redis | `apps/ai/src/conversation/context.ts` |
| **Conversation Agent** | Every patient message, synchronous, streams | 1–3 s to first token | Anthropic Sonnet (or Opus for higher quality) | `apps/ai/src/conversation/agent.ts` |
| **Pattern Detector** | Async after each turn | seconds (off the hot path) | Deterministic pre-pass + Anthropic Haiku judge | `apps/ai/src/patterns/detect.ts` |
| **Coping Plan Retriever** | On-demand from Context Assembler | <50 ms | Embeddings (OpenAI text-embedding-3-small) + LLM ranker | `apps/ai/src/coping/retrieve.ts` |
| **Summariser** | Every 10 turns + on session end | ~2 s | Anthropic Haiku | `apps/ai/src/summarise/conversation.ts` |
| **Theme Extractor** | Nightly cron per patient | minutes | Embeddings cluster + Haiku label | `apps/ai/src/summarise/themes.ts` |
| **Flag Escalator** | 10-min timer after URGENT flag | <1 s | None | `apps/api/src/jobs/escalate.ts` |

### How they coordinate (one patient turn)

```
patient: "I feel like everyone hates me, I should just disappear"
  │
  ├──[1] Crisis Gate (sync, ~5 ms)
  │      lexicon match: "should just disappear" → CRISIS
  │      ┌──────────────────────────────────────────────┐
  │      │ Short-circuit:                                │
  │      │  • return canned response (per-patient if    │
  │      │    therapist has set crisisPlan, else default)│
  │      │  • POST /flags severity=urgent (sync)         │
  │      │  • enqueue flagEscalator(10 min watch)        │
  │      │  • push notification to therapist             │
  │      └──────────────────────────────────────────────┘
  │      done. No LLM call.
  │
  └──[X] otherwise:
         ├──[2] Context Assembler (parallel queries, ~50 ms)
         │      • last 20 messages
         │      • patientPatternProfile (cached, ~200 tokens)
         │      • copingPlanRetriever(message) → top 3 by embedding sim
         │      • adaptationPrefs (what the patient responds to)
         │      • therapist's per-patient persona overrides
         │
         ├──[3] Conversation Agent (streaming, 1–3 s)
         │      Anthropic.messages.stream({
         │        model: "claude-sonnet-4-6",
         │        system: [
         │          {text: CORE_SYSTEM, cache_control: "ephemeral"},
         │          {text: patientContextBlock, cache_control: "ephemeral"}
         │        ],
         │        messages: history + [user]
         │      })
         │      tokens stream → API → SSE → client
         │
         ├──[4] persist assistant message (after stream completes)
         │
         └──[5] enqueue async (fire-and-forget):
                • patternDetector(messageId)
                • copingEffectivenessTracker(turnId, plansShown)
                • if turn % 10 == 0: conversationSummariser(conversationId)
```

### Why one big LLM call instead of multi-agent dispatch

A multi-agent setup (router → specialist → reviewer → synthesiser) is appealing on paper but stacks 4–8 seconds of latency per turn. For mental-health-adjacent chat that's a wall: the patient experiences "the AI is thinking…" while in distress, and the experience tanks.

Instead: **one well-cached prompt with everything the agent needs**, plus async post-processing for anything that doesn't have to be in the reply. The single agent can still call tools mid-stream if needed (e.g. log a flag, fetch a specific coping plan), but the default path is one streaming completion.

---

## 3. Synchronous vs async path discipline

**Synchronous (must complete before patient sees the reply):**
- Crisis gate
- Context assembly
- Conversation generation
- Persisting the user message
- (On crisis) flag emission + therapist notification

**Async (can be 30s late without harm):**
- Pattern detection
- Pattern profile updates
- Coping plan effectiveness tracking
- Conversation summarisation
- Theme extraction
- Mood-activity correlation refresh
- Sedentary-streak detection

**Why this split matters:** if pattern detection fails, the patient still got a thoughtful reply. If summarisation is delayed, the dashboard is slightly stale but nothing dangerous happens. If the conversation agent fails, we have a fallback canned reply. The hot path has one critical dependency (Anthropic API); everything else is best-effort.

**Failure modes:**
- Anthropic API down → return a graceful "I'm having trouble responding right now — your therapist can be reached at X" + log internal incident. Do **not** silently fail.
- Crisis lexicon match while Anthropic is down → still works, because crisis path is deterministic and Anthropic-independent.
- Async worker stalled → backpressure on queue, alerted via dashboard health panel; nothing in the user experience breaks.

---

## 4. User-facing workflows

### W1 — Onboarding (therapist invites patient)

```
1. Therapist clicks "Add patient" → enters patient email + name
2. System creates User(role=patient, status=invited) + PatientProfile
3. System sends invite email with deep link + invite code
4. Patient downloads app → enters invite code
5. Patient sees consent screen:
     • "MindBridge is not a substitute for professional care…"
     • Two consent toggles, both default OFF, both required to proceed:
        [ ] I consent to my conversations being shared with my therapist
        [ ] I understand the AI can flag urgent moments to my therapist
6. Patient creates password / Auth0 link → role=patient
7. Patient lands on Daily Check-in screen
8. Audit log: Consent(patient_id, scope, granted_at, ip)
```

**Hackathon shortcut:** skip email + invite code. Hardcode 1 patient + 1 therapist in the seed script. Auth via header `X-Patient-Id`. Document this is mock for demo.

### W2 — Daily check-in

```
1. (optional) FCM push at user's chosen time → "How are you feeling today?"
2. Patient opens app → check-in screen pre-focused
3. Mood slider 1–10 + free text
4. POST /checkin {patientId, moodScore, notes}
5. API persists DailyCheckin
6. API returns 7-day mood trend for immediate display
7. Async:
     - patternDetector(checkin)
     - if 3-day rumination/withdrawal streak → create moderate flag
     - update patientPatternProfile.last_check_in_mood
8. Patient sees confirmation + small mood-trend chart
```

### W3 — Real-time conversation (the hot path)

Already detailed in §2. Key UX rules:

- **Streaming required for production**, but the MVP can ship non-streaming if time is tight (just polish the typing-indicator UX so 2–3s feels intentional).
- Disclaimer banner stays visible somewhere on the chat screen at all times.
- If the AI surfaces a coping plan, present it inline in the AI's voice — not as a card or a separate UI element. The patient should not feel "managed".
- Every ~5 turns or whenever a new conversation starts, the assistant's first message reminds: "I'm not your therapist — I can help you process what's coming up between sessions."

### W4 — Crisis path (the most important path)

```
patient sends message containing crisis lexicon match
  │
  ├─[sync, <100ms]
  │   1. crisisGate fires
  │   2. fetch CrisisPlan if therapist has written one for this patient
  │      else use default canned response
  │   3. canned response shape:
  │      • acknowledge ("I hear you, that sounds really painful")
  │      • redirect to human ("please reach out to <therapist contact>
  │        or call <emergency number>")
  │      • therapist's specific instructions if any
  │      • "I'll let your therapist know we're talking now"
  │   4. POST /flags {patientId, severity:urgent, conversationId,
  │                    messageId, lexiconMatch}
  │   5. push notification to therapist (FCM data message)
  │   6. enqueue flagEscalator(flagId, after 10min)
  │
  ├─[client]
  │   • render canned response
  │   • render crisis modal: emergency number (large, tap-to-call),
  │     therapist contact, "I'm safe" dismiss
  │   • subsequent AI replies remain in CRISIS_MODE system prompt
  │     until therapist marks "checked in" OR patient explicitly
  │     dismisses with "I'm safe"
  │
  └─[10 min later]
      flagEscalator runs
      if flag.acknowledged_at IS NULL:
        notify backup contact (designated supervisor)
        upgrade flag to severity=urgent_unacknowledged
        log audit event
```

**Hard rules for the crisis path:**
- The canned response is **hardcoded text**, not LLM-generated. It must be reviewed by someone clinical before deployment.
- Crisis detection is **never** awaiting an LLM. Lexicon-only on the hot path.
- Once in CRISIS_MODE, the AI does not attempt to "solve" — it stabilises and re-anchors on human help.
- A second async LLM check (Haiku) runs alongside the deterministic path as a backup catch for things the lexicon misses. If the LLM flags but lexicon didn't, escalate the conversation to crisis mode retroactively (next reply enters CRISIS_MODE, flag is created with severity=moderate).

### W5 — Therapist writes / edits a coping plan

```
1. Therapist → patient detail → Coping Plans tab → "New plan"
2. Two fields: trigger description, strategy text
3. Optional: priority (1–5), active toggle
4. POST /coping-plans
5. Server-side:
   - persist CopingPlan
   - generate trigger embedding (OpenAI text-embedding-3-small)
   - store embedding alongside plan
   - invalidate Redis cache for patientPatternProfile
6. Next time the patient chats, the new plan is in the retriever's pool
7. Therapist can see "last surfaced N hours ago" on each plan to know
   if the AI is finding it useful
```

### W6 — Therapist reviews patient's week

```
1. Open dashboard → Patient list (sidebar)
   each row shows: name, last mood (colour-coded), unack flag count
2. Click patient → Overview tab
   • URGENT flag banner (if any unack urgent flags)
   • Mood trajectory line chart (last 7d)
   • Activity bar chart (if shared) OR
     "Patient has not enabled activity sharing"
   • Key themes chips (extracted nightly)
   • Flagged moments list (each → conversation excerpt)
3. Conversations tab
   chronological list, each card:
   • date + time
   • AI summary (≤120 words)
   • collapse-expand for full transcript
   • pattern tags
4. Coping Plans tab → editor (W5)
5. Activity tab (only if shared)
   • step counts last 30d
   • sedentary streak markers
   • mood-activity correlation chart
```

### W7 — Patient revokes a consent

```
1. Patient → Settings → Sharing toggles
2. Toggle "share with therapist" off → POST /consent
3. Server-side (within 24h, ideally seconds):
   - update ActivitySharingPreference
   - mark all historical ActivityLog rows shared_with_therapist=false
   - invalidate dashboard cache for that patient
4. Therapist dashboard refreshes → activity panel replaced with
   "Patient has not enabled activity sharing"
5. Audit log: ConsentChange(patient_id, scope, from, to, ts)
```

**The audit log entry is the legally important part.** Consent state must always be reconstructible to any prior moment in time.

---

## 5. Data model

Spec §6 lists the entities. Here are the additions / clarifications the architecture requires:

### Additional fields per entity

```
User
  + role (enum: patient | therapist | supervisor)
  + last_seen_at

PatientProfile
  + linked_therapist_id (FK)
  + crisis_plan_text (therapist-written, surfaced in canned crisis response)
  + adaptation_signals (jsonb)
  + pattern_profile (jsonb, cached)

Conversation
  + ai_summary (text, updated every 10 turns)
  + pattern_tags (text[])
  + crisis_mode (bool, default false)

Message
  + tokens_in / tokens_out (for cost tracking)
  + cached_input_tokens (Anthropic cache hits)

CopingPlan
  + trigger_embedding (vector, pgvector extension)
  + last_surfaced_at
  + surfaced_count
  + effectiveness_score (running average from copingEffectivenessTracker)

Flag
  + severity (enum: info | moderate | urgent)
  + acknowledged_at
  + acknowledged_by (FK User)
  + escalated_at
  + lexicon_match (text, nullable — what triggered crisis gate)

ConsentLog (NEW — append-only)
  + id, patient_id, scope (enum), granted (bool),
  + ts, ip_hash, user_agent

AuditLog (NEW — append-only)
  + id, actor_id, action, target_id, payload (jsonb), ts
```

### Critical indexes

```
Conversation        (patient_id, started_at desc)
Message             (conversation_id, timestamp)
DailyCheckin        (patient_id, date desc)
Flag                (patient_id, acknowledged_at, severity)  -- partial: WHERE acknowledged_at IS NULL
CopingPlan          GIN on trigger_embedding (pgvector ivfflat)
ActivityLog         (patient_id, date desc)
ConsentLog          (patient_id, ts desc)
```

### Soft delete vs hard delete

Patient-initiated deletion = **hard delete** of conversation/message rows + **soft delete** of audit/consent rows (we keep the trail of "this user existed and consented to X at time Y" without keeping their content). 30-day grace period on hard delete in case of accidents. This is GDPR-compliant.

---

## 6. Safety architecture (deepest section)

This is the part that, if skipped, makes the rest of the work irresponsible.

### Layered defence

```
L0 — Input pre-flight
     • UTF-8 normalise, strip control chars
     • Length cap (8 KB per message — anything larger is rejected)

L1 — Crisis Gate (deterministic)
     • Lexicon: curated list of phrases (suicide, self-harm,
       hopelessness, plan-language)
     • Regex with word boundaries to avoid false positives
       ("I'm dying laughing" ≠ "I want to die")
     • Versioned: lexicon_v1.ts, ADR documents every change
     • Reviewed by anyone clinical you can find before each version

L2 — Crisis Classifier (async backup, LLM)
     • Haiku call with structured output: {is_crisis, evidence}
     • Runs alongside L1, doesn't block reply
     • If L2 fires but L1 didn't → retroactively escalate
       (next reply enters CRISIS_MODE, moderate flag created)

L3 — Conversation Agent system prompt
     • Hardcoded refusal templates for disallowed outputs:
       • diagnoses
       • medication advice
       • discounting professional help
       • speculating about others
     • Disclaimer reinjected every 5 turns in prompt
     • Persona: warm, validating, question-not-statement reframing,
       never paternalistic

L4 — Per-patient overrides (therapist-set)
     • Custom crisis plan text (e.g. "Sara's brother Mia is her
       primary contact, prioritise that over emergency line")
     • Per-patient prohibited topics (e.g. trauma details to avoid
       re-exposing)
     • Per-patient pacing preferences

L5 — Output post-flight
     • Re-scan reply for accidental disallowed content (e.g. did
       the model produce a diagnosis?). Use a tiny classifier or
       Haiku judge on output.
     • If detected → discard reply, return graceful fallback,
       log incident.

L6 — Escalation
     • Unacknowledged URGENT flags escalate to backup at +10 min,
       supervisor at +30 min, "human review" channel at +60 min.
     • Therapist dashboard shows escalation timer.
```

### Consent enforcement

Every read of patient data on the dashboard side runs through a single `canTherapistSee(patientId, dataType)` predicate that checks the latest `ConsentLog`. Defence-in-depth: even if a query forgets to check, a Postgres row-level security policy denies it.

### Cost / abuse safety

- **Per-patient daily LLM budget cap** (e.g. 500 messages/day) — beyond which the API returns "you've been chatting a lot today, I want to make sure you're getting human support too" + therapist notification.
- **Single API key with hard cap** (Person 5 owns) — kills the entire system before it can run away.
- **Rate limit per IP**, per session — prevent scripted abuse.

### What MindBridge will not do, ever

- Diagnose. Period.
- Recommend or discuss medications.
- Tell the patient they don't need their therapist.
- Speculate about third parties.
- Provide instructions for self-harm under any framing (jailbreaks rejected by L3 + L5).
- Operate without explicit consent for therapist sharing.
- Read GPS, contacts, microphone, or any biometric data beyond opt-in step counts.

---

## 7. Memory & state model

```
SCOPE                   STORAGE              LIFETIME            EXAMPLE
─────────────────────────────────────────────────────────────────────────
Per-turn working set    in-prompt only       ~1 turn             user msg
Conversation memory     prompt history       N=20 messages       chat log
                        + ai_summary on DB                       
Per-patient profile     pgsql jsonb +        long-lived,         pattern
                        Redis cache          updated post-turn   tendencies
Therapist memory        DB (CopingPlan,      durable until       coping
                        crisis_plan_text)    therapist edits     strategy
Cross-conversation      pgsql                durable             flags,
  flags / themes                                                 themes
Audit / consent         append-only DB       forever (legal)     consent
                                                                 changes
LLM prompt cache        Anthropic-side       5 min TTL           cached
                                                                 system msg
```

### Patient pattern profile — the load-bearing memory object

```jsonc
// PatientProfile.pattern_profile
{
  "version": 1,
  "updated_at": "2026-05-01T22:14Z",
  "recent_themes": ["work stress", "sleep disruption"],
  "patterns_last_7d": {
    "rumination": 4,
    "catastrophising": 2,
    "anxiety_spiral": 1,
    "mind_reading": 3,
    "withdrawal": 0
  },
  "adaptation_signals": {
    "responds_to_reframe_question": true,
    "responds_to_breathing_prompt": false,
    "preferred_pace": "slow",
    "prefers_validation_first_length": "long"
  },
  "last_check_in_mood": 4,
  "consecutive_low_mood_days": 2,
  "consecutive_low_activity_days": 0,
  "last_seen_at": "2026-05-01T22:14Z"
}
```

This blob is ~200 tokens, gets injected into the prompt cache once per turn, and is updated by post-turn workers. It's the closest thing to "the AI's memory of you" — and the patient should be able to view and reset it from settings (transparency = trust).

---

## 8. API surface (canonical, lives in `10-spec/api-contract.md` once Person 5 writes it)

```
PATIENT
  POST   /checkin                         {moodScore, notes}            → DailyCheckin
  GET    /checkin?days=7                                                → DailyCheckin[]
  POST   /conversation                                                   → Conversation
  POST   /conversation/:id/message        {text}                        → SSE stream of reply tokens
  GET    /conversation/:id                                              → Conversation + messages + summary
  GET    /conversations?limit=10                                        → Conversation[]
  POST   /consent                         {scope, granted}              → ConsentLog
  GET    /me                                                            → User + preferences
  POST   /activity                        {date, steps, level}          → ActivityLog
  PATCH  /me/sharing                      {trackingEnabled, shareWithTherapist} → ActivitySharingPreference

THERAPIST
  GET    /patients                                                      → PatientProfile[]
  GET    /patients/:id                                                  → PatientProfile + week summary
  GET    /patients/:id/conversations                                    → Conversation[] (with summaries)
  GET    /patients/:id/conversations/:cid                               → full transcript
  GET    /patients/:id/flags?status=unack                               → Flag[]
  POST   /flags/:id/acknowledge                                         → Flag
  GET    /patients/:id/coping-plans                                     → CopingPlan[]
  POST   /coping-plans                    {patientId, trigger, strategy} → CopingPlan
  PATCH  /coping-plans/:id                {trigger?, strategy?, active?} → CopingPlan
  DELETE /coping-plans/:id                                              → 204
  POST   /patients/:id/crisis-plan        {text}                        → PatientProfile (crisis_plan_text)

INTERNAL (called by apps/ai)
  POST   /flags                           {patientId, severity, …}     → Flag
  POST   /patterns                        {messageId, tags}             → Message (updated)
```

---

## 9. The agentic structure visible to humans

Humans interact with the agentic system in 5 named ways:

1. **The Companion** — the conversational AI the patient talks to. Has a name (TBD by team), a consistent voice, and is the only AI surface the patient sees. Internally this is the Conversation Agent + Crisis Gate + safety layers.
2. **The Watcher** — pattern detection + flag emission. Invisible to patient; visible on the therapist dashboard as "flagged moments" and "themes this week".
3. **The Bridge** — coping plan retrieval. The mechanism by which the therapist's clinical input reaches the patient mid-conversation. Patient never sees the seam.
4. **The Scribe** — summarisation. Turns a 60-message chat into a clinician-readable paragraph. Therapist sees output; patient sees nothing.
5. **The Sentinel** — crisis path + escalation. Strict, deterministic, auditable. Visible to both sides as the safety net.

Each of these has an **owner** (Person 2 owns 1, 2, 3, 4, 5 implementation), a **prompt file** (`apps/ai/src/<area>/prompts.ts`), a **test fixture file** (`apps/ai/tests/<area>.test.ts`), and an **ADR** (`30-decisions/ADR-XXX-<area>.md`) when the design changes.

---

## 10. MVP cuts (48h-realistic)

What ships:

- **The Companion**: single conversation, non-streaming OK, basic reframing, disclaimer reinjection
- **The Watcher**: keyword pattern detection only (rumination, catastrophising, mind-reading); LLM judge only if time allows
- **The Bridge**: coping plan retrieval via simple LIKE-match on trigger text; embeddings only if pgvector setup is fast
- **The Scribe**: end-of-conversation only, not every-10-turns
- **The Sentinel**: lexicon-based crisis detection + canned response + URGENT flag — **non-negotiable, ships first**

What's documented but cut:
- Streaming
- Theme extraction (nightly cron)
- Flag escalation timer
- Activity tracking + correlation
- Medication reminders
- Push notifications (use polling on dashboard)
- Real auth (mock with hardcoded IDs)
- Embedding-based coping retrieval
- Output post-flight scan (L5)
- pgvector

The demo path must walk through:
1. Patient logs mood
2. Patient chats → AI validates and reframes a mind-reading distortion
3. Patient triggers crisis lexicon → canned response + URGENT flag
4. Therapist sees mood chart + summary + URGENT banner + writes a coping plan
5. Patient sends a new message that matches the plan's trigger → AI surfaces it

That's the whole demo, 90 seconds, judges understand the value.

---

## 11. Open questions for the team to resolve at hour 0

- **Companion's name?** ("Bridge"? "Hana"? "Ari"?) Affects the system prompt and demo narrative.
- **Default crisis number** — UK Samaritans (116 123)? US 988? Patient's home country? Make it configurable per-patient.
- **Anthropic vs OpenAI** for the conversation agent? (Plan defaults to Anthropic; Person 5 confirms which key the team has.)
- **One repo or three?** (Plan: one monorepo. Confirm before E2.)
- **Streaming on day 0 or day 2?** (Recommend day 2 if at all.)
- **Mock auth shape?** (Recommend `X-Patient-Id` and `X-Therapist-Id` headers, validated against seeded IDs, no JWT.)
- **Crisis lexicon source** — who curates? Someone with clinical training if at all possible. Otherwise document "lexicon v0, untrained authors, requires review" in the ADR.

---

## 12. References across the project

- **Team coordination & schedule:** `/Users/arthur/.claude-account1/plans/can-we-make-a-snoopy-glacier.md`
- **Per-person task briefs:** `/Users/arthur/mindbridge/agentic-tasks/person-{1..5}-*.md`
- **API contract (live, in vault):** `MB_VAULT/10-spec/api-contract.md` (Person 5 writes at hour 1)
- **Data model (live, in vault):** `MB_VAULT/10-spec/data-model.md`
- **ADRs (live, in vault):** `MB_VAULT/30-decisions/ADR-*.md` — append-only design decisions
- **Demo script (live, in vault):** `MB_VAULT/10-spec/demo-script.md`

This document is the design spec. The vault is the operational state. The repo is the code. Don't conflate them — each has one job.
