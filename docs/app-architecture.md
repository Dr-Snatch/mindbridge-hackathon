# MindBridge — App Architecture

**Status:** hackathon build. Keep it simple. Ship the demo.

---

## The problem in one sentence

Therapy is one hour out of 168. MindBridge fills the other 167 with an AI companion that talks to patients between sessions and surfaces useful structure to the therapist.

---

## What we're actually building

Three things:

1. A **patient mobile app** — daily mood check-in + AI chat
2. A **therapist dashboard** — see mood trends, flag alerts, write coping plans
3. An **API + AI library** that connects them

That's it. The AI does two things: pattern recognition (is this message a crisis? what's the conversational pattern?) and sentiment analysis (reframe the patient's distorted thinking with questions, not statements).

---

## System overview

```
┌──────────────────────┐       ┌──────────────────────────┐
│  Patient (Expo RN)   │       │  Therapist (Vite/React)  │
│  • mood check-in     │       │  • patient list           │
│  • AI chat           │       │  • mood chart + flags     │
│  • crisis modal      │       │  • coping plan editor     │
└──────────┬───────────┘       └────────────┬─────────────┘
           │ HTTPS                           │ HTTPS
           └──────────────┬─────────────────┘
                          ▼
           ┌──────────────────────────────────┐
           │  apps/api — Express + Prisma      │
           │  Port 4000                        │
           │  • thin route handlers            │
           │  • mock auth (X-Patient-Id header)│
           │  • imports apps/ai as a library   │
           └──────────────┬───────────────────┘
                          │ in-process function calls
                          ▼
           ┌──────────────────────────────────┐
           │  apps/ai — TypeScript library     │
           │  • crisis detection (sync)        │
           │  • conversation agent             │
           │  • pattern detection (keyword)    │
           │  • conversation summariser        │
           └──────────────┬───────────────────┘
                          │
                          ▼
           ┌──────────────────────────────────┐
           │  Postgres (Prisma)                │
           │  That's the only datastore.       │
           │  No Redis. No queues.             │
           └──────────────────────────────────┘
                          │
                          ▼
           ┌──────────────────────────────────┐
           │  Anthropic API                    │
           │  • claude-sonnet-4-6 (chat)       │
           │  • claude-haiku-4-5 (summaries)   │
           └──────────────────────────────────┘
```

**What we deliberately left out:**
- Redis / BullMQ job queue (not needed — everything runs in-process)
- pgvector / embeddings (LIKE-match on coping plan triggers is fine for a demo)
- OpenAI embeddings (we only use Anthropic)
- FCM push notifications (therapist dashboard just polls every 5s)
- Twilio SMS (not needed)
- Streaming SSE (typing indicator + non-streaming is fine)
- Nightly cron jobs (no theme extractor)
- Flag escalation timers (therapist sees flags, acknowledges them)
- Activity tracking / step counts (cut)

---

## What happens on each patient message

```
patient sends: "I just don't want to be here anymore"
  │
  ├─ [1] Crisis check — synchronous, no LLM, <10ms
  │      keyword regex with word boundaries
  │      "don't want to be here" → MATCH
  │
  │      → return hardcoded canned response (never LLM-generated)
  │      → POST /flags with severity=urgent
  │      → return { reply, isCrisis: true }
  │      → done. No Anthropic call.
  │
  └─ [not crisis path]
       │
       ├─ [2] Build context (~50ms)
       │      • last 20 messages from DB
       │      • coping plans matching message text (simple LIKE match)
       │      • inject into system prompt
       │
       ├─ [3] One Anthropic Sonnet call (1–3s)
       │      system: [core persona, patient context block]
       │      messages: history + current
       │      returns: reply text
       │
       ├─ [4] Persist messages to DB
       │
       └─ [5] After reply sent: detect patterns (keyword match, synchronous)
              rumination / catastrophising / mind-reading / anxiety / withdrawal
              persist pattern_tags to message
```

That's the entire AI flow. One DB read, one Anthropic call, one DB write.

---

## Crisis path

This is the most important path. It must never fail.

```
1. Crisis check fires synchronously before any LLM call
2. Lexicon-only — never an LLM on this path
3. Return hardcoded canned response:
     "I hear you, and what you're describing sounds really painful.
      I'm concerned about you right now.
      Please reach out: Crisis line: 988 (24/7) · Your therapist: [name]
      I've let your therapist know we're talking now."
4. Create Flag in DB: { patientId, severity: "urgent", lexiconMatch }
5. Client renders crisis modal — full screen, can only dismiss with "I'm safe" checkbox
6. Therapist dashboard shows urgent red banner (polled every 5s)
7. Therapist clicks "mark as checked in" → flag acknowledged
```

Hard rules:
- The canned response is hardcoded text. Not LLM-generated. Not editable via API.
- Crisis detection is synchronous and has no external dependencies.
- If Anthropic is down, the crisis path still works.

---

## Coping plan flow

```
1. Therapist writes a plan: trigger = "assumes others are judging them",
   strategy = "ask what evidence they have for that interpretation"
2. POST /coping-plans → persisted to DB
3. Next patient message: API does a simple LIKE match between message text
   and all active coping plans' trigger field
4. Matching plans are injected into the patient context block:
     "THERAPIST'S STRATEGIES:
      When: [trigger] → Approach: [strategy]"
5. AI weaves it naturally into its reply — never quotes it directly
```

No embeddings. No vector DB. LIKE match is good enough for a demo.

---

## Data model

### Entities

```
User
  id, email, name, role (patient | therapist), created_at

PatientProfile
  id, userId (FK), linkedTherapistId (FK), crisisPlanText, created_at

Conversation
  id, patientId (FK), startedAt, endedAt, aiSummary

Message
  id, conversationId (FK), role (patient | assistant), text, timestamp, patternTags (text[])

DailyCheckin
  id, patientId (FK), date, moodScore (1-10), notes, createdAt

CopingPlan
  id, patientId (FK), therapistId (FK), trigger, strategy, active (bool), lastSurfacedAt, createdAt

Flag
  id, patientId (FK), conversationId (FK), severity (info | moderate | urgent),
  lexiconMatch, acknowledgedAt, acknowledgedBy (FK User), createdAt

ConsentLog
  id, patientId (FK), scope, granted (bool), ts

AuditLog
  id, actorId (FK User), action, targetId, payload (jsonb), ts
```

### Indexes

```
Message         (conversationId, timestamp)
DailyCheckin    (patientId, date desc)
Conversation    (patientId, startedAt desc)
Flag            (patientId, acknowledgedAt) — partial WHERE acknowledgedAt IS NULL
CopingPlan      (patientId, active)
```

### What we cut from the data model

- `PatientProfile.adaptation_signals` (jsonb) — not needed
- `PatientProfile.pattern_profile` (jsonb cache) — not needed
- `CopingPlan.triggerEmbedding` (vector) — no pgvector
- `CopingPlan.effectivenessScore` — not tracking this
- `Flag.escalatedAt` — no escalation timers
- `ActivityLog` — activity tracking is cut
- `ActivitySharingPreference` — cut with activity tracking

---

## API surface

```
PATIENT (header: X-Patient-Id)
  POST   /checkin                    {moodScore, notes}           → DailyCheckin + weekTrend
  GET    /checkin?days=7                                           → DailyCheckin[]
  POST   /conversation                                             → Conversation
  POST   /conversation/:id/message   {text}                       → { message, isCrisis }
  GET    /conversation/:id                                         → Conversation + messages
  GET    /conversations                                            → Conversation[]

THERAPIST (header: X-Therapist-Id)
  GET    /patients                                                 → PatientProfile[]
  GET    /patients/:id                                             → PatientProfile + recent data
  GET    /patients/:id/flags?status=unack                          → Flag[]
  POST   /flags/:id/acknowledge                                    → Flag
  GET    /patients/:id/coping-plans                               → CopingPlan[]
  POST   /coping-plans               {patientId, trigger, strategy} → CopingPlan
  PATCH  /coping-plans/:id           {trigger?, strategy?, active?} → CopingPlan

INTERNAL (called by apps/ai)
  POST   /flags                      {patientId, severity, conversationId, lexiconMatch} → Flag

SYSTEM
  GET    /health                                                   → { status: "ok" }
```

---

## The 5-step demo path

This is the only thing that must work perfectly by H+44.

```
Step 1 — Mood check-in
  Patient opens app → slides mood to 3/10 → types "stressed about work" → Submit
  → Sees success state with 7-day mood chart (arc: 6→5→7→3→4→4→3)

Step 2 — AI chat and reframe
  Patient taps Chat → types "my friend hasn't replied, they hate me"
  → Typing indicator → AI reply validates feeling, asks reframing question
  → Disclaimer banner visible throughout

Step 3 — Crisis trigger
  Patient types "I just don't want to be here anymore"
  → Crisis modal covers screen: 988 number, "I've let your therapist know"
  → Therapist dashboard: urgent red banner appears (within 5s via polling)

Step 4 — Therapist dashboard
  Therapist opens dashboard → sees Alex with mood 3 in red → clicks through
  → Sees 7-day mood chart → Conversations tab shows AI summary
  → Acknowledges urgent flag → flag banner disappears

Step 5 — Coping plan round-trip
  Therapist writes plan: trigger "assumes others judging", strategy "ask for evidence"
  → Patient sends "I know everyone at the meeting was judging me"
  → AI reply naturally incorporates the strategy
```

---

## Safety rules (non-negotiable)

1. Crisis detection is **synchronous, deterministic, lexicon-only** — no LLM on this path, ever.
2. The canned crisis response is **hardcoded text** — not LLM-generated, not configurable via API.
3. Every screen with AI content shows the disclaimer: "AI companion — not a substitute for professional care."
4. The AI never diagnoses, never recommends medication, never discourages therapy.
5. Consent is explicit — both toggles required before first use.
6. Every therapist route runs `canTherapistSee(patientId, dataType)` before returning patient data.

---

## Deployment

- **API + Postgres:** Railway
- **Dashboard:** Vercel
- **Mobile:** Expo Go (for demo), TestFlight/APK if time allows
- Env vars: `DATABASE_URL`, `ANTHROPIC_API_KEY`, `PORT`, `CORS_ORIGIN`
- Start command: `prisma migrate deploy && node dist/index.js`

---

## Open decisions for hour 0

- **AI companion name?** Something warm and short — Aria, Hana, Sage. Person 4 decides with Arthur.
- **Crisis number** — US 988 or UK 116 123? Pick one for the demo. Document it's configurable.
- **Non-streaming is fine** — typing indicator with 2-3s wait is polished enough.
