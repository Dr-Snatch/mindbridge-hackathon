# Person 3 — Frontend Engineer (Role C)

You build everything judges see and tap. Both apps: the patient's mobile check-in and chat, and the therapist's dashboard. They share the same API — use mock fallbacks so the demo never fails because the API is down.

---

## You own
`apps/mobile/` · `apps/dashboard/`

## You do NOT touch
`apps/api/` · `apps/ai/` · `packages/types/` · `prisma/`

---

## Setup

1. Clone: `git clone https://github.com/Dr-Snatch/mindbridge-hackathon ~/mindbridge`
2. `cd ~/mindbridge && pnpm install`
3. Copy `.env.example` to `.env` — fill in `VITE_API_URL=http://localhost:4000` (dashboard) and `EXPO_PUBLIC_API_URL=http://localhost:4000` (mobile)
4. `pnpm dev:dashboard` and `pnpm dev:mobile` — both should start
5. Read `docs/app-architecture.md` before writing any API calls

---

## The mock pattern — use this everywhere

The demo cannot fail because the API is down. Every API call needs a local fallback:

```typescript
// apps/mobile/src/api/client.ts  (same pattern for dashboard)
export async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Patient-Id': PATIENT_ID,
        ...options?.headers
      },
      signal: AbortSignal.timeout(8000)
    })
    if (!res.ok) throw new Error(`${res.status}`)
    return res.json()
  } catch (e) {
    console.warn('API unavailable, using mock:', e)
    return getMockResponse(path) as T
  }
}
```

Write `apps/mobile/src/api/mocks.ts` and `apps/dashboard/src/api/mocks.ts` with realistic fallback data matching Alex's story: mood arc 6→5→7→3→4→4→3, one urgent crisis flag, one conversation with an AI summary, one coping plan.

---

## Colour system — use these everywhere, no variations

```
Mood 7–10:  #22c55e  (Tailwind: green-500)
Mood 5–6:   #f59e0b  (Tailwind: amber-500)
Mood 1–4:   #ef4444  (Tailwind: red-500)
Brand:      #6366f1  (Tailwind: indigo-500)
Urgent:     #dc2626  (Tailwind: red-600)
```

---

## Tasks — do in order

**1. Scaffold both apps**

Mobile (`apps/mobile/`):
- Expo Router + NativeWind v4 + Zustand + API client
- Tabs: `(tabs)/index.tsx` (check-in), `(tabs)/chat.tsx` (AI chat), `(tabs)/settings.tsx`
- Root layout with SafeAreaProvider and QueryClient

Dashboard (`apps/dashboard/`):
- Vite + React + Tailwind + shadcn/ui + TanStack Query
- Routes: `/patients` (list), `/patients/:id` (detail with tabs)
- API client with `X-Therapist-Id: therapist-1` header

→ Done when: `pnpm dev:mobile` and `pnpm dev:dashboard` both start without errors. QR code loads in Expo Go.

**2. Mobile: consent screen + check-in**

Consent screen (`app/(auth)/consent.tsx`) — first launch only, cannot be skipped:
- Two toggles both required: "Share my conversations with Dr Sarah Chen" + "Allow urgent moments to be flagged"
- One checkbox: "I understand this is not a substitute for therapy"
- "Get started" button disabled until all three are checked

Check-in screen (`app/(tabs)/index.tsx`):
- Mood slider 1–10 (emoji: 😰 at 1, 😐 at 5, 😄 at 10 — colour: red → amber → green)
- Free text field: "What's on your mind today?" (optional, max 500 chars)
- Submit → POST /checkin → success with 7-day mini mood chart
- If already checked in today: show today's score + "How are things going?" prompt

→ Done when: demo step 1 works — slide to 3, type "stressed about work", Submit, see trend chart. Test with API down too.

**3. Dashboard: patient list + mood chart**

Patient list (`/patients`):
- Sidebar: patient cards with name, last mood coloured red/amber/green, flag count badge
- Click → patient detail

Patient detail overview (`/patients/:id`):
- Recharts line chart — 7-day mood scores, dots coloured red/amber/green
- Empty state: "No check-ins yet this week"

→ Done when: dashboard loads, shows Alex in sidebar with mood 3 in red, click opens the mood chart. Works with mock data if API is down. **Message Arthur.**

**4. Mobile: AI chat screen**

Chat screen (`app/(tabs)/chat.tsx`):
- Disclaimer banner always visible at top: "AI companion — not a substitute for professional care" (amber, small, can never be hidden)
- Message list (FlatList, newest at bottom)
- Patient messages: right-aligned, indigo background
- AI messages: left-aligned, gray background
- Typing indicator (animated dots) while waiting
- Input bar + send button — disabled while waiting
- Optimistic UI: show message immediately, then wait for reply

API flow:
1. If no active conversation, POST /conversation first
2. POST /conversation/:id/message `{text}`
3. If response `isCrisis: true` → navigate to crisis modal immediately
4. If `isCrisis: false` → add AI message to list

→ Done when: demo step 2 works — type "my friend hasn't replied, they hate me" → typing indicator → validating reply → disclaimer visible throughout. **Message Arthur.**

**5. Dashboard: patient detail tabs**

Urgent flag banner (above all tabs):
- Red background, white text, "Flagged: [lexicon match text]"
- "Mark as checked in" button — removes banner on click (calls POST /flags/:id/acknowledge)
- Poll every 5s via TanStack Query `refetchInterval: 5000`
- Renders nothing when no unacknowledged urgent flags

Conversations tab:
- List of conversation cards: date, AI summary text
- If `aiSummary` is null: "Summary not yet available"
- Expand to see full transcript

Coping Plans tab:
- List of plans: trigger, strategy, active/inactive toggle, "last surfaced" label
- "New plan" form: "When..." textarea + "Then..." textarea + Save
- Calls POST /coping-plans on save, refetches list

→ Done when: demo steps 4 + 5 work — urgent banner shows for Alex, conversations tab shows summary, therapist writes a coping plan and it appears. **Message Arthur.**

**6. Mobile: crisis modal**

Full-screen overlay (`app/crisis-modal.tsx`) when API returns `isCrisis: true`.

Requirements:
- Full screen — not a card, not a bottom sheet
- 988 in large text, tap-to-call: `Linking.openURL('tel:988')`
- Therapist contact, also tap-to-call
- "Your therapist has been notified" message
- "I am safe right now" checkbox — Continue button only activates after this
- No swipe-to-dismiss, no back button — only exit is "I'm safe" + Continue

→ Done when: demo step 3 works — "I just don't want to be here anymore" → crisis modal covers screen → 988 visible and tappable → "I'm safe" + Continue dismisses it.

**7. Polish pass + demo prep**

- Every mood score everywhere uses the same red/amber/green values — no variations
- Every list has a friendly empty state, never a blank screen
- Loading skeletons on dashboard (not spinners)
- Open both apps fresh — Alex's story visible immediately from seed data
- Run the full 5-step demo path manually. Note anything that feels slow or fragile.

→ Done when: you can run all 5 demo steps from scratch, with both API up and API down. **Message Arthur.**

---

## Rules

- Disclaimer banner visible at all times on any screen with AI content. Never hidden.
- Every API call has a local fallback. The demo cannot fail because the API is unavailable.
- All screens work in Expo Go — no bare workflow native modules.
- `AbortSignal.timeout(8000)` on every fetch.
- Crisis modal: 988 button minimum 64px height. All interactive elements: minimum 44×44px.
- Activity tracking defaults to OFF. Never request location, microphone, or camera.

## Stuck? Message Arthur.
