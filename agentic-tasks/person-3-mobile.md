# Person 3 — Patient Mobile App (Role C)

You are Person 3. You own the **patient-facing mobile app**. The judges will see this first, so polish matters more than feature count.

## Setup

- `MB_ROLE=C`
- Stack: Expo (React Native) + TypeScript + NativeWind (Tailwind for RN) + Zustand for state. Demo on Expo Go (iOS).
- API base URL: read from `10-spec/api-contract.md` (Person 1 writes it).
- Shared types: `import type {...} from '@mindbridge/types'`.

Before starting any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

Person 5 has set up the remote `mindbridge` vault on Obsidian Sync. You connect to it — Sync runs over HTTPS so it works fine on uni wifi.

1. **Install Obsidian** desktop from obsidian.md. Sign in / create an account using the email Person 5 invited you on.
2. **Find the invited vault**: Settings → Sync → "Available remote vaults" → `mindbridge`.
3. **Connect**: paste the **end-to-end encryption password** from the team's 1Password / Bitwarden. Local path **`~/Obsidian/MindBridge-Vault`** — exact path matters because your `MB_VAULT` env var depends on it.
4. **Wait for first sync**. You should see `00-meta/`, `10-spec/`, `20-tasks/`, `30-decisions/`, `40-handoffs/`, `50-flags/`, `.claude/`.
5. **Set env vars** in `~/.claude/settings.json` per plan §3.1: `MB_ROLE=C`, `MB_VAULT=/Users/<me>/Obsidian/MindBridge-Vault`, `MB_REPO=/Users/<me>/mindbridge`. Restart Claude Code.
6. **Sync check**: create `40-handoffs/<YYYY-MM-DD>-C.md` with `connected at HH:MM, sync working`. Save. Within 30s Person 5 sees it.
7. **Slash command check**: `/board` prints the live task board.
8. **Orient yourself (role-specific)**: open `10-spec/api-contract.md` — those endpoints are what your screens will call. Note the staging API URL at the top of the doc — that's what you point Expo at. Read before claiming C1.

If any step fails, write `50-flags/onboard-C.md` and ping Person 5. Do not start the task queue with broken sync.

## Task queue (do in order)

### C1 — Scaffold `apps/mobile`
`pnpm create expo-app apps/mobile --template tabs`. Add NativeWind, set up Zustand store with `patientId` (mock to a seeded ID for the demo). **Done when:** Expo Go runs the empty app on your phone.

### C2 — Disclaimer + consent screen (one-time)
First-launch screen: "MindBridge is not a substitute for professional mental health care. In a crisis, contact [number]." Two buttons: I understand / Crisis line. Persist consent locally. **Done when:** restarting after consent skips this screen.

### C3 — Daily check-in flow
Tab 1. Mood slider 1–10 (large, friendly), single text field "what's on your mind today?", submit → `POST /checkin`. After submit: show today's entry + last 7 days as small mood dots. **Done when:** Person 1's seed data shows up and new submissions persist.

### C4 — AI chat screen
Tab 2. Single conversation thread (start a new `Conversation` on first message). Show typing indicator while AI replies. Auto-scroll. Pull system disclaimer banner on top. **Done when:** end-to-end chat with Person 2's AI service works against staging.

### C5 — Crisis fallback UI
If the AI reply contains a crisis flag (Person 2 returns `{isCrisis: true}` in metadata), show a modal with: emergency number (large, tap-to-call), therapist's contact, "I'm safe" dismiss button. **Done when:** typing a crisis fixture triggers the modal.

### C6 — Settings tab
Tab 3. Toggle: share data with therapist (default on, links to `ActivitySharingPreference`). Toggle: track activity passively (default off — opt-in only, see spec §7.3). Account info. **Done when:** toggling persists locally and POSTs to API.

### C7 — Polish pass
Loading skeletons, empty states, error toasts, smooth transitions. iconography consistent. **Done when:** the app feels finished in a 90-second demo run-through.

## Cut lines
Activity tracking (HealthKit/GoogleFit) → medication reminders UI → push notifications → session booking. The minimum demo is C1–C5.

## Hard rules
- Never request location permission. Step count only (and only if C7+ activity feature ships).
- Default activity-sharing to OFF. The toggle copy must be neutral, never coercive.
- The disclaimer banner stays visible somewhere on every screen with AI content.
- If the API is down, fall back to a "demo mode" that uses local mock data — never crash. The demo cannot fail because of network.
