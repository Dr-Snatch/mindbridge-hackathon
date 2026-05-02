# Person 3 — Frontend Engineer (Role C)

You own **both client apps**: the patient mobile app and the therapist dashboard. You build the entire visible surface of MindBridge — what judges see and touch. Work the mobile app and dashboard in parallel; they share patterns and both hit the same API.

## Setup

- `MB_ROLE=C`
- Mobile stack: Expo SDK 51, React Native, TypeScript, NativeWind, Zustand, Expo Router
- Dashboard stack: Vite, React, TypeScript, Tailwind, shadcn/ui, Recharts, TanStack Query
- You own: `apps/mobile/`, `apps/dashboard/`

Before any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

1. Install Obsidian from obsidian.md. Sign in with the email Person 5 invited you on.
2. Settings → Sync → "Available remote vaults" → `mindbridge`.
3. Paste the E2EE password from team password manager. Local path: `~/Obsidian/MindBridge-Vault`.
4. Wait for first sync — verify you see `00-meta/`, `10-spec/`, `20-tasks/`.
5. Set env vars in `~/.claude/settings.json`: `MB_ROLE=C`, `MB_VAULT=~/Obsidian/MindBridge-Vault`, `MB_REPO=~/mindbridge`.
6. Sync check: write `40-handoffs/<today>-C.md` — "connected at HH:MM". Person 5 confirms within 30s.
7. Run `/board` — should see the live task board.
8. Read `10-spec/api-contract.md` — all the endpoints you'll call are defined there.
9. Check `10-spec/component-specs/` — Person 4 (Designer) is writing component specs for you to implement.

## Task queue (do in order)

### C1 — Scaffold both apps
Expo app with Expo Router tab navigation. Vite + React + Tailwind dashboard. Both have an API client with mock auth headers and local fallback pattern. **Done when:** both dev servers start without errors.

### C2 — Mobile: consent + check-in screen
Consent screen (required before any AI features). Mood check-in: slider 1–10 with emoji/color feedback, notes field, submit → success state with 7-day mini trend. Calls `POST /checkin`. **Done when:** demo step 1 works (log mood 3/10, "stressed about work").

### C3 — Dashboard: patient list + mood chart
Patient list sidebar with last mood (colour-coded) and flag count badge. Patient detail with 7-day Recharts line chart. Calls `GET /patients` and `GET /patients/:id`. **Done when:** therapist can open dashboard and see Alex's mood arc.

### C4 — Mobile: AI chat screen
Message list, input bar, typing indicator, send to `POST /conversation/:id/message`. Disclaimer banner always visible. Optimistic message display. Fallback reply if API times out. **Done when:** demo step 2 works (chat with mind-reading message, see reframe reply).

### C5 — Dashboard: patient detail tabs
URGENT flag banner (top of page, impossible to miss, 5s polling). Conversations tab with AI summaries. Coping Plans tab with the new-plan form. **Done when:** demo steps 4+5 work (therapist sees urgent banner, writes coping plan).

### C6 — Mobile: crisis modal
Full-screen crisis modal with emergency number (large, tap-to-call), therapist contact, "I'm safe" checkbox confirmation to dismiss. Triggered when API returns `isCrisis: true`. **Done when:** demo step 3 works (crisis trigger → modal appears).

### C7 — Connect the coping plan round-trip
After therapist saves a coping plan (C5), the next mobile chat with a matching message should surface it. Verify `POST /coping-plans` → next `POST /conversation/:id/message` response. **Done when:** demo step 5 works end-to-end.

### C8 — Polish pass + demo prep
Colour-code mood scores consistently (red/amber/green). Empty states for all lists. Loading skeletons. Pre-load seed data so the demo doesn't start on blank screens. Test the full 5-step demo path manually. **Done when:** you can run all 5 demo steps without a hitch.

## Cut lines

Activity tab (step counts) → settings tab → mobile step-count tracking → streaming SSE (non-streaming JSON is fine with a typing indicator delay). Never cut: check-in, chat, crisis modal, dashboard mood chart, urgent banner, coping plan editor.

## Hard rules

- Disclaimer banner is always visible on any screen with AI content — never hide it.
- Activity tracking defaults to OFF. Never request location, microphone, or camera permissions.
- Every API call has a local fallback — the demo cannot fail due to a network issue.
- All screens must work in Expo Go — no bare workflow native modules.
- Use `AbortSignal.timeout(8000)` on all fetch calls.
- Minimum touch target: 44×44px on mobile. Crisis call button: 64px minimum height.
- Never show stale activity data — if sharing is off, show "Patient hasn't enabled activity sharing".

## Colour system (match these everywhere)

```
Mood 7-10: #22c55e (green)   Mood 5-6: #f59e0b (amber)   Mood 1-4: #ef4444 (red)
Brand:     #6366f1 (indigo)  Urgent:   #dc2626 (red-600)
```

## Useful agents

`c-expo-component` · `c-checkin-flow` · `c-chat-screen` · `c-crisis-modal` · `c-mock-data` · `d-recharts` · `d-patient-overview` · `d-flag-system` · `d-coping-editor` · `d-tanstack-query` · `shared-demo-validator`
