# Person 4 — Brand & UX Designer (Role D)

You define what MindBridge looks and feels like. Your output is Markdown files that Person 3 implements from — be precise enough that they never have to ask you a design question.

---

## You own
Design docs in the vault: `10-spec/brand-guidelines.md` · `10-spec/ux-flows/` · `10-spec/component-specs/` · `10-spec/ui-copy.md`
`packages/design-tokens/` in the repo — one file of colour/spacing constants

## You do NOT touch
Any code in `apps/` — you write specs, Person 3 writes code. If you notice a visual bug in the app, write a note and tag Person 3 directly.

---

## Who you're designing for

**Patients** — people in active therapy, often using the app in difficult emotional moments:
- Calm over clever — nothing loud or bouncy
- One job per screen
- Short sentences — people in distress don't read paragraphs
- Large touch targets — 44px minimum, 64px on crisis actions

**Therapists** — busy clinicians switching between patients:
- Colour signals, not just text
- Clear hierarchy — urgent is obvious instantly
- No friction on common actions

---

## Colours — use these exactly, do not invent others

```
Primary:       #6366f1  (indigo-500)   — buttons, active states
Primary dark:  #4f46e5  (indigo-600)   — hover, pressed
Primary light: #e0e7ff  (indigo-100)   — tag backgrounds
Mood high:     #22c55e  (green-500)    — mood 7–10
Mood mid:      #f59e0b  (amber-500)    — mood 5–6
Mood low:      #ef4444  (red-500)      — mood 1–4
Urgent:        #dc2626  (red-600)      — flag banner background
Text primary:  #111827  (gray-900)
Text secondary:#6b7280  (gray-500)
Border:        #e5e7eb  (gray-200)
Surface:       #f9fafb  (gray-50)
```

---

## Tasks — do in order

**1. Brand guidelines**
File: `10-spec/brand-guidelines.md`

Write:
- Full colour table above with Tailwind names and usage context
- Typography: Dashboard uses Inter (Google Fonts) at 12/14/16/20px. Mobile uses system font (SF on iOS, Roboto on Android) at 14/16/24px. Never pure black — use gray-900.
- Icons: Lucide only, 16px or 20px, never decorative
- AI companion name: pick something warm and short — Aria, Hana, or Sage. **Message Arthur to confirm before finalising** — it goes in the pitch too.
- Tone: calm, warm, never clinical, never alarming. One sentence max for every UI label.

→ Done when: Person 3 can open this file and know every colour and font without asking you.

**2. UX flow — patient mobile app**
File: `10-spec/ux-flows/patient-app.md`

Document every screen and how they connect. Use Mermaid diagrams + text description.

Onboarding: First launch → Welcome → Consent (both toggles required) → Check-in screen

Daily use:
```
App open → Check-in screen
  ├─ Not yet checked in → Slider + notes + Submit → Success + trend chart → Chat tab available
  └─ Already checked in → "You checked in: X/10" → prompt to chat
```

Chat:
```
Chat tab → [Create conversation if none] → Message input
  ├─ Normal → Typing indicator → AI reply → Continue
  └─ Crisis detected → Canned reply in chat → CRISIS MODAL (full screen)
       └─ "I'm safe" checkbox + Continue → Back to chat with post-crisis banner
```

Settings: toggle therapist sharing.

For every edge case: what shows when API is down, first-time user, no internet.

→ Done when: Person 3 has zero questions about which screen leads where.

**3. UX flow — therapist dashboard**
File: `10-spec/ux-flows/dashboard.md`

```
Dashboard loads → Patient list sidebar
  Click patient → Patient detail
    ├─ [Urgent flags] → Red banner TOP of page (always above tabs)
    ├─ Overview tab (default) → mood chart + AI summary snippets
    ├─ Conversations tab → conversation list + AI summaries
    └─ Coping Plans tab → plan list + new plan form
```

For each tab: what data shows, empty state, available actions.

→ Done when: Person 3 can build the dashboard navigation from this document alone.

**4. Component specs — demo path components first**
Create `10-spec/component-specs/<ComponentName>.md` for each. Include:
- Visual anatomy (ASCII or written)
- All states: default, hover, loading, error, empty, disabled
- Exact Tailwind spacing (p-4 = 16px, gap-3 = 12px, rounded-xl = 12px)
- Typography: size, weight, colour per text element
- Colours for each state
- Exact interaction: what happens on tap

Build in this order:
1. **MoodSlider** — thumb size, track height, colour gradient, value label
2. **DisclaimerBanner** — height, background, text, always top of chat
3. **CrisisModal** — full screen, 988 button minimum 64px, "I'm safe" checkbox
4. **UrgentFlagBanner** — red-600 background, white text, always above tabs
5. **MoodChart** — Recharts line chart, coloured dots, empty state
6. **CopingPlanCard** — active vs inactive visual, "last surfaced" label
7. **PatientListItem** — mood colour dot, flag count badge
8. **MessageBubble** — patient (right, indigo) vs AI (left, gray)

**Message Arthur or Person 3** when each spec is ready — they can start building immediately.

→ Done when: Person 3 can implement each component to pixel precision without asking you.

**5. UI copy**
File: `10-spec/ui-copy.md`

Write every piece of user-facing text. Group by screen.

Must include:
- Consent screen: headline, each toggle label + description, CTA
- Check-in: prompt text (3 rotation variants), success message, already-checked-in state
- Chat: empty state, disclaimer text (fixed: "AI companion — not a substitute for professional care"), typing indicator text, fallback reply text
- Crisis modal: all text — calm, no exclamation marks, no medical jargon
- Post-crisis banner text
- Error messages: network error, server error, validation failures
- Dashboard: column headers, tab labels, empty states, coping plan form labels, flag badge text

Copy rules:
- Max 2 sentences per UI element, prefer 1
- No exclamation marks in distress contexts
- Validate before directing: "That sounds hard. Please reach out to..." not "Call 988 immediately."
- Use the patient's first name when available: "How are you feeling, Alex?"
- Never use technical language: "network timeout" → "I'm having trouble connecting"

→ Done when: Person 3 has zero placeholder strings in the app.

---

## Rules

- Disclaimer banner text is fixed: "AI companion — not a substitute for professional care." Do not rephrase it.
- Crisis modal copy: no exclamation marks, no alarm language. Calm and anchoring.
- Every component spec includes an empty state — always answer "what do I show when there's no data?"
- Message Arthur to confirm the companion name before it goes anywhere — it's in the pitch deck.
- Specs are for Person 3, not for posterity. If it's not useful to them, don't write it.

## Stuck? Message Arthur.
