# Person 4 — Brand & UX Designer (Role D)

**Your job in one sentence:** Define what MindBridge looks and feels like, and produce specs precise enough that Person 3 can implement them without any design conversations.

---

## What you own
- All design documentation in the vault: `10-spec/brand-guidelines.md`, `10-spec/ux-flows/`, `10-spec/component-specs/`, `10-spec/ui-copy.md`
- `packages/design-tokens/` in the repo — a single file of colour/spacing constants if Person 3 wants to import them directly

## What you do NOT own
- **Any code in `apps/`** — you write specs, Person 3 writes code. If you notice something wrong in the app, write a note in `20-tasks/T-XXX.md` with `owner: C`. Never edit `.tsx` or `.ts` files directly.
- API contract, data model — those are Person 1 + 5's territory
- The vault's `10-spec/api-contract.md` — read it, don't edit it

**Your output format is Markdown in the vault.** That's your deliverable. Be precise. "padding: 16px (Tailwind: p-4)" is useful. "add some padding" is not.

---

## Setup (do this first)

```
MB_ROLE=D
MB_VAULT=~/Obsidian/MindBridge-Vault
MB_REPO=~/mindbridge
```

Add to `~/.claude/settings.json` under `"env"`. Then:

1. Install Obsidian, sign in with Person 5's invite, connect to `mindbridge` vault with the E2EE password
2. Wait for sync. Verify all folders appear.
3. Write `40-handoffs/<today>-D.md` — "connected at HH:MM".
4. **Read `README.md` and `docs/app-architecture.md §4`** — understand what every screen does before you design it
5. Read `10-spec/api-contract.md` — know what data is available (you can't design a chart for data that doesn't exist)

---

## Who you're designing for

**Patients** — people in active therapy, often using the app in difficult emotional moments. They may have shaky hands, cognitive overload, or be in low-light environments. Design for:
- Calm over clever — nothing loud, bouncy, or exciting unless it's a genuine alarm
- One job per screen — never compete for attention
- Short sentences in all copy — people in distress don't read paragraphs
- Large, forgiving touch targets — 44px minimum, 64px on crisis actions

**Therapists** — busy clinicians switching between patients. They need:
- Fast cognitive scanning — colour signals, not just text
- Clear information hierarchy — what's urgent is obvious
- No friction on common actions (acknowledging a flag, writing a plan)

---

## Task queue — do these in order

### D1 — Brand guidelines
File: `10-spec/brand-guidelines.md`

Write a document covering:

**Colours (use these exactly — do not invent others):**
```
Primary:       #6366f1  (indigo-500)   — brand colour, buttons, active states
Primary dark:  #4f46e5  (indigo-600)   — hover states, pressed, text on white
Primary light: #e0e7ff  (indigo-100)   — tag backgrounds, subtle tints
Mood high:     #22c55e  (green-500)    — mood 7-10
Mood mid:      #f59e0b  (amber-500)    — mood 5-6
Mood low:      #ef4444  (red-500)      — mood 1-4
Urgent:        #dc2626  (red-600)      — urgent flag banner background
Text primary:  #111827  (gray-900)
Text secondary:#6b7280  (gray-500)
Border:        #e5e7eb  (gray-200)
Surface:       #f9fafb  (gray-50)
```

**Typography:**
- Dashboard: Inter (Google Fonts). Sizes: 12px labels, 14px body, 16px emphasis, 20px headings.
- Mobile: System font (San Francisco on iOS, Roboto on Android). Sizes: 14px body, 16px messages, 24px headings.
- Never use pure black (#000) — use gray-900.

**Iconography:** Lucide icons only — one library, consistent weight. 16px or 20px, never decorative.

**Companion name:** Recommend a name for the AI (e.g. Aria, Hana, Sage). Coordinate with Person 5 — it affects the pitch and all UI copy. Pick something warm, short, not robotic.

**Done when:** Person 3 can open this file and know every colour and font to use without asking you.

### D2 — UX flow: patient mobile app
File: `10-spec/ux-flows/patient-app.md`

Document every screen and how they connect. Use Mermaid diagrams + text description. Cover:

**Onboarding flow:**
```
First launch → Welcome screen → Consent screen (all toggles required) → Check-in screen
```

**Daily use flow:**
```
App open → Check-in screen
  ├─ Not yet checked in → Slider + notes + Submit → Success with trend chart → [Chat tab available]
  └─ Already checked in → "You checked in: X/10" → prompt to chat
```

**Chat flow:**
```
Chat tab → [Create conversation if none] → Message input
  ├─ Normal message → Typing indicator → AI reply → Continue
  └─ Crisis trigger detected → Canned reply in chat → CRISIS MODAL (full screen)
       └─ "I'm safe" checkbox + Continue → Back to chat with post-crisis banner
```

**Settings flow:** toggle activity tracking (default OFF), toggle therapist sharing.

For every edge case write what should appear: API down, first-time user, returning user, no internet.

**Done when:** Person 3 has zero questions about which screen leads to which.

### D3 — UX flow: therapist dashboard
File: `10-spec/ux-flows/dashboard.md`

```
Dashboard loads → Patient list sidebar
  Click patient → Patient detail
    ├─ [Urgent flags] → Red banner TOP of page (always above tabs)
    ├─ Overview tab (default) → mood chart + themes + flagged moments
    ├─ Conversations tab → list of conversations + AI summaries
    ├─ Coping Plans tab → plan list + new plan form
    └─ Activity tab → step counts (if patient has enabled sharing)
```

For each tab: what data is shown, what the empty state looks like, what actions are available.

**Done when:** Person 3 can build the dashboard navigation from this document alone.

### D4 — Component specs (priority order: demo path first)

For each component, create a separate file in `10-spec/component-specs/<ComponentName>.md`. Include:
- Visual anatomy (ASCII diagram or written description)
- All states: default, hover/pressed, loading, error, empty, disabled
- Exact spacing in Tailwind scale (p-4 = 16px, gap-3 = 12px, rounded-xl = 12px)
- Typography: font size, weight, colour per text element
- Colours: background, border, text for each state
- Exact interaction: what happens on tap/click

Build these in demo path order:

1. **MoodSlider** — thumb size, track height, colour gradient, value label above
2. **DisclaimerBanner** — height, background, text, always at top of chat screens
3. **CrisisModal** — full screen, emergency button minimum size (64px), checkbox confirm
4. **UrgentFlagBanner** — red-600 background, white text, always above tabs, shadow
5. **MoodChart** — line chart with coloured dots, empty state, tooltip
6. **CopingPlanCard** — active vs inactive visual difference, "last surfaced" label
7. **PatientListItem** — mood colour dot, flag count badge
8. **MessageBubble** — patient (right, indigo) vs AI (left, gray)

**Done when:** Person 3 can implement each component to pixel precision without asking you a single question.

### D5 — UI copy
File: `10-spec/ui-copy.md`

Write every piece of user-facing text in the product. Group by screen.

Must include:
- Consent screen: headline, each toggle label + description, CTA
- Check-in screen: prompt (5 rotation variants), success message, already-checked-in state
- Chat screen: empty state, disclaimer banner text, typing indicator text, fallback reply text
- Crisis modal: all text (must be calm — no exclamation marks, no jargon)
- Post-crisis banner text
- All error messages (network error, server error, validation failures)
- Dashboard: patient list column headers, all tab labels, all empty states, coping plan form labels, flag badge text, "mark as checked in" button

**Copy rules:**
- Maximum 2 sentences per UI element, prefer 1
- No exclamation marks in distress contexts
- Validate before directing: "That sounds hard. Please reach out to..." not "Call 988 immediately."
- Use the patient's first name when available ("How are you feeling, Alex?")
- Never use technical language for errors ("network timeout" → "I'm having trouble connecting")

**Done when:** Person 3 has zero placeholder strings in the app ("Lorem ipsum", "TODO: copy here", etc.).

### D6 — Accessibility review
File: `50-flags/accessibility-D.md`

After Person 3 has the main screens built, review:

- **Colour contrast** — check every text/background combination against WCAG AA (4.5:1 for normal text, 3:1 for large text). The `design-accessibility` agent has pre-checked the core palette.
- **Touch targets** — every tappable element must be ≥44px. The crisis call button must be ≥64px.
- **Screen reader labels** — interactive elements without visible text labels need `accessibilityLabel` (mobile) or `aria-label` (dashboard)
- **Urgent banner** — must use `role="alert"` on the dashboard so screen readers announce it automatically

Write each finding as: component name + issue + fix recommendation. Tag Person 3 for each FAIL.

**Done when:** no WCAG AA failures on the demo path screens.

### D7 — Demo visual polish
Write `40-handoffs/<date>-D.md` after reviewing the built app:
- Open the mobile app on a real device (or Expo Go on your phone)
- Open the dashboard in a browser
- Note anything that looks wrong, feels off, or would embarrass the team in front of judges
- For each issue: describe it precisely, reference the component spec it violates, and tag Person 3 with a vault task

**Done when:** you'd be comfortable handing a judge an iPhone and walking away.

---

## How to communicate with Person 3

**Your spec is ready for a component:**
Write a note in `40-handoffs/<today>-D.md`: "Component spec ready: [ComponentName], see 10-spec/component-specs/[name].md". Person 3 will pick it up.

**Person 3 built something that doesn't match your spec:**
Create `20-tasks/T-XXX-visual-fix.md` with `owner: C`. Include: component name, what the spec says, what was built, screenshot or description of the difference.

**You need to know what data a screen has access to:**
Read `10-spec/api-contract.md` or ask Person 1 in the team chat. Don't design a feature around data that doesn't exist.

**You want to change a design decision after specs are written:**
Update the spec file AND write a `40-handoffs/<today>-D.md` note so Person 3 knows to re-check their implementation.

**Something needs a decision (e.g. the companion name):**
Write `50-flags/decision-D-<topic>.md`. Person 5 will triage and facilitate.

---

## Cut order

Drop in this order if behind:
1. Dark mode specs
2. Advanced animation specs
3. Marketing copy or app store copy
4. Accessibility review (D6) — still note critical issues but skip exhaustive audit

**Never cut:** brand guidelines (D1), component specs for demo path components (D4), UI copy (D5). Without these Person 3 is guessing, and guessing shows.

---

## Hard rules

- Disclaimer banner text is fixed: "AI companion — not a substitute for professional care". Don't rephrase it.
- Crisis modal copy: no exclamation marks, no alarm language. Calm and anchoring.
- Every component spec includes an empty state. "What do I show when there's no data?" must always have an answer.
- Coordinate with Person 5 before finalising the companion name — it's in the pitch deck too.
- Specs are written for Person 3, not for posterity. If it's not useful to them, don't write it.

---

## Useful agents

`design-brand` · `design-ux-flows` · `design-spec-writer` · `design-accessibility` · `design-copy` · `shared-advisor`
