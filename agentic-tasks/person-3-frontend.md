# Person 3 — Frontend Engineer (Role C)

**Your job in one sentence:** Build both the patient mobile app and the therapist dashboard — everything judges see and interact with is yours.

---

## What you own
- `apps/mobile/` — the Expo React Native patient app
- `apps/dashboard/` — the Vite/React therapist web app

## What you do NOT own (do not edit these)
- `apps/api/` → Person 1. If you need a new endpoint or a change to an existing one, write `20-tasks/T-XXX.md` with `owner: A`. Never edit API code.
- `apps/ai/` → Person 2. If the AI replies feel wrong, write `20-tasks/T-XXX.md` with `owner: B`.
- `packages/types/` → Person 1. Import types, never redefine them locally.
- Vault spec files → Person 4 writes design specs, Person 5 writes the API contract.

**Your single source of design truth:** `10-spec/component-specs/` and `10-spec/brand-guidelines.md` in the vault. Check there before making visual decisions. If a spec doesn't exist yet, write `20-tasks/T-XXX-spec-needed.md` with `owner: D` — then continue with a reasonable placeholder and note the TODO.

---

## Setup (do this first)

```
MB_ROLE=C
MB_VAULT=~/Obsidian/MindBridge-Vault
MB_REPO=~/mindbridge
```

Add to `~/.claude/settings.json` under `"env"`. Then:

1. Clone the repo: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. Install Obsidian, sign in with Person 5's invite email, connect to `mindbridge` vault with E2EE password
3. Wait for vault sync. Verify all folders appear.
4. Write `40-handoffs/<today>-C.md` — "connected at HH:MM".
5. Run `/board` in Claude Code.
6. **Read `10-spec/api-contract.md`** — every API call you'll make is defined here
7. **Check `10-spec/component-specs/`** — Person 4 will be writing component specs as you build

---

## The API mock pattern — use this everywhere

The demo cannot fail because the API is down. Every API call you make must have a local fallback:

```typescript
// apps/mobile/src/api/client.ts  (same pattern for dashboard)
export async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { 
        'Content-Type': 'application/json',
        'X-Patient-Id': PATIENT_ID,   // or X-Therapist-Id on dashboard
        ...options?.headers 
      },
      signal: AbortSignal.timeout(8000)   // never hang the demo
    })
    if (!res.ok) throw new Error(`${res.status}`)
    return res.json()
  } catch (e) {
    console.warn('API unavailable, using mock:', e)
    return getMockResponse(path) as T    // always returns plausible data
  }
}
```

Write `apps/mobile/src/api/mocks.ts` and `apps/dashboard/src/api/mocks.ts` with realistic fallback data matching the seed story (Alex, Dr Sarah Chen, 7-day mood arc, crisis flag, coping plan).

---

## Task queue — do these in order

### C1 — Scaffold both apps

**Mobile:**
- `apps/mobile/` with Expo Router, NativeWind v4, Zustand store, API client stub
- Tab structure: `(tabs)/index.tsx` (check-in), `(tabs)/chat.tsx` (AI chat), `(tabs)/settings.tsx`
- Root layout with SafeAreaProvider, QueryClient

**Dashboard:**
- `apps/dashboard/` with Vite + React + Tailwind + shadcn/ui + TanStack Query
- Route structure: `/patients` (list), `/patients/:id` (detail)
- API client with `X-Therapist-Id: therapist-1` header

**Done when:** `pnpm dev:mobile` and `pnpm dev:dashboard` both start without errors. The Expo QR code loads in Expo Go on your phone.

### C2 — Mobile: consent + check-in screen

**Consent screen** (`app/(auth)/consent.tsx`) — required on first launch, cannot be skipped:
- App name + "MindBridge — support between sessions"
- Two toggles, both must be ON before proceeding: "Share my conversations with Dr Sarah Chen" + "Allow urgent moments to be flagged"
- "I understand this is not a substitute for therapy" acknowledgement checkbox
- "Get started" CTA — disabled until all three are checked

**Check-in screen** (`app/(tabs)/index.tsx`):
- Mood slider 1–10 (emoji feedback: 😰 at 1, 😐 at 5, 😄 at 10; colour: red→amber→green)
- Free text field: "What's on your mind today?" (optional, max 500 chars)
- Submit button → calls `POST /checkin` → success state with 7-day mini mood chart
- If already checked in today: show today's score + "How are things going?" prompt

**Done when:** demo step 1 works: set slider to 3, type "stressed about work", tap Submit, see the success state with a trend chart. Test with API down too — must succeed with local fallback.

### C3 — Dashboard: patient list + mood chart

**Patient list** (`/patients`):
- Sidebar with patient cards: name, last mood score coloured (red/amber/green), flag count badge
- Click → navigates to patient detail

**Patient detail overview** (`/patients/:id`):
- 7-day Recharts line chart showing mood scores — use `d-recharts` agent for exact implementation
- Dots colour-coded: red for low scores, green for high
- Empty state: "No check-ins yet this week"

**Done when:** the dashboard loads, shows Alex in the sidebar with mood 3/10 in red, click opens the mood chart showing the 7-day arc. Works with mock data if API is down.

### C4 — Mobile: AI chat screen

**Chat screen** (`app/(tabs)/chat.tsx`):
- Disclaimer banner always visible at top: "AI companion — not a substitute for professional care" (amber, small, can't be hidden)
- Message list (FlatList, newest at bottom)
- Patient messages: right-aligned, indigo background
- AI messages: left-aligned, gray background
- Typing indicator (animated dots) while waiting for reply
- Input bar with send button — disabled while waiting for reply
- On send: optimistic UI (show message immediately), then wait for API

**API call flow:**
1. If no active conversation, POST /conversation first
2. POST /conversation/:id/message with `{text}`
3. On response: if `isCrisis: true` → navigate to crisis modal immediately
4. If `isCrisis: false` → add AI message to list

**Done when:** demo step 2 works: type "my friend hasn't replied, they hate me" → see typing indicator → see a reply that validates then asks a reframing question. Disclaimer banner visible throughout.

### C5 — Dashboard: patient detail tabs

**URGENT flag banner** — top of patient detail, above all tabs:
- Red background, white text, 🚨 emoji, "impossible to miss" design
- Shows the lexicon match text: `Flagged: "don't want to be here anymore"`
- "Mark as checked in" button — removes banner immediately on click
- Polls every 5 seconds via TanStack Query `refetchInterval: 5000`
- Renders null (nothing) when no unacknowledged urgent flags — no "no flags" message

**Conversations tab:**
- List of conversation cards: date, AI summary text, pattern tags chips
- If `aiSummary` is null: show "Summary not yet available"
- Expand to see full transcript

**Coping Plans tab:**
- List of existing plans: trigger text, strategy text, active/inactive toggle, "last surfaced X ago"
- "New plan" form: "When..." textarea + "Then..." textarea + Save button
- Calls `POST /coping-plans` on save, refetches list

**Done when:** demo steps 4 + 5 work: urgent banner appears for Alex, conversations tab shows the AI summary, therapist can write a new coping plan and see it appear.

### C6 — Mobile: crisis modal

Full-screen overlay (`app/crisis-modal.tsx`), presented when API returns `isCrisis: true`.

Requirements:
- Full screen — not a small card, not a bottom sheet
- Emergency number (988) in large text, tap-to-call: `Linking.openURL('tel:988')`
- Therapist contact, also tap-to-call
- "Your therapist has been notified" confirmation message
- "I am safe right now" checkbox — user must check this before the Continue button activates
- No swipe-to-dismiss, no back button — only exit is the confirmed "I'm safe" flow

**Done when:** demo step 3 works: type "I just don't want to be here anymore" → crisis modal appears immediately covering the screen → emergency number is visible and tappable → "I'm safe" + Continue dismisses it.

### C7 — Coping plan round-trip verification

After the therapist saves a coping plan in C5, the next patient chat message matching the trigger should produce an AI reply that naturally incorporates the strategy.

This is mostly a Person 2 + Person 1 integration, but you need to verify it from the frontend:
- Save a coping plan with trigger "assumes others are judging them"
- Send a chat message like "I know everyone was judging me at the meeting"
- The AI reply should ask something like "what evidence do you have for that interpretation?"

If it doesn't work: write `50-flags/coping-roundtrip-C.md` and tag Person 2.

**Done when:** the coping plan appears in the AI reply. Demo step 5 complete.

### C8 — Polish pass + demo prep

- Colour consistency: every mood score shown anywhere (mobile or dashboard) uses the exact same red/amber/green values
- Empty states: every list has a friendly empty state, never a blank screen
- Loading skeletons on dashboard patient detail (not spinners — they look janky)
- Pre-loaded seed data: open the apps for the first time and see Alex's story, not blank screens
- Manually run the full 5-step demo path. Note anything that feels slow, confusing, or fragile.

**Done when:** you can run all 5 demo steps from scratch, including API down (mobile fallback) and API up (real data), without anything breaking or looking bad.

---

## Colour system — use these values everywhere, no variations

```
Mood 7–10: #22c55e (Tailwind: green-500)
Mood 5–6:  #f59e0b (Tailwind: amber-500)
Mood 1–4:  #ef4444 (Tailwind: red-500)
Brand:     #6366f1 (Tailwind: indigo-500)
Urgent:    #dc2626 (Tailwind: red-600)   ← slightly darker for the banner
```

---

## Balancing mobile vs dashboard

You own both apps — this is a lot, but they share a lot too. Recommended split of attention:

- Hours 2–10: scaffold both, then focus on mobile check-in + dashboard mood chart (they prove the core loop)
- Hours 10–20: mobile chat screen + dashboard patient detail (the heart of the demo)
- Hours 20–28: crisis modal + coping plan editor (the emotional peak of the demo)
- Hours 28–36: round-trip verification + polish
- Hours 36+: demo prep

When in doubt, prioritise **whatever the next demo step needs** over polish on something already done.

---

## If you want to make a change

**Need a new API endpoint:**
Write `20-tasks/T-XXX-new-endpoint.md` with `owner: A`. Include the exact method, URL, request body, and response shape you need. In the meantime, use mock data.

**The AI reply doesn't feel right (wrong tone, doesn't reframe, etc.):**
Write `20-tasks/T-XXX-prompt-fix.md` with `owner: B`. Describe exactly what you sent and what you got vs what you expected. Don't try to fix the AI library yourself.

**Person 4's component spec says something different from what you built:**
Build what the spec says. If the spec is wrong or missing, flag it: write `20-tasks/T-XXX-spec-update.md` with `owner: D`. Document what you built in the meantime.

**API endpoint shape changed:**
Person 1 should have flagged this. Check `40-handoffs/` for recent notes from A. Update your API client to match. If it broke silently, write `50-flags/api-shape-change-C.md`.

---

## Hard rules

- Disclaimer banner visible at all times on any screen with AI content. Never hidden.
- Activity tracking defaults to OFF. Never request location, microphone, or camera permissions.
- Every API call has a local fallback. The demo cannot fail because the API is unavailable.
- All screens work in Expo Go — no bare workflow native modules.
- `AbortSignal.timeout(8000)` on every fetch call.
- Crisis call button: minimum 64px height. All other interactive elements: minimum 44×44px touch target.
- Never show stale or missing activity data — show "Patient hasn't enabled activity sharing".

---

## Useful agents

`c-expo-component` · `c-checkin-flow` · `c-chat-screen` · `c-crisis-modal` · `c-mock-data` · `d-recharts` · `d-patient-overview` · `d-flag-system` · `d-coping-editor` · `d-tanstack-query` · `shared-demo-validator`
