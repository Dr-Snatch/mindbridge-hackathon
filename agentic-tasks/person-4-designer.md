# Person 4 — Brand & UX Designer (Role D)

You own the **look, feel, and language** of MindBridge. You define the visual identity, design the user experience, write the UI copy, and produce component specs that Person 3 implements. You work in the Obsidian vault and design tools — you don't write code.

## Setup

- `MB_ROLE=D`
- Your tools: Obsidian vault, Figma (or pen + paper), this Claude Code session for research and spec writing
- You own: `packages/design-tokens/` (if created), all vault docs in `10-spec/brand-guidelines.md`, `10-spec/ux-flows/`, `10-spec/component-specs/`, `10-spec/ui-copy.md`
- You do NOT write code in `apps/` — you write specs that Person 3 implements

Before any task: `/claim <task-id>`. After: `/handoff <task-id>`.

## Obsidian Sync onboarding (do this BEFORE hour 0)

1. Install Obsidian from obsidian.md. Sign in with the email Person 5 invited you on.
2. Settings → Sync → "Available remote vaults" → `mindbridge`.
3. Paste the E2EE password from team password manager. Local path: `~/Obsidian/MindBridge-Vault`.
4. Wait for first sync — verify you see `00-meta/`, `10-spec/`, `20-tasks/`.
5. Set env vars in `~/.claude/settings.json`: `MB_ROLE=D`, `MB_VAULT=~/Obsidian/MindBridge-Vault`, `MB_REPO=~/mindbridge`.
6. Sync check: write `40-handoffs/<today>-D.md` — "connected at HH:MM". Person 5 confirms within 30s.
7. Read `README.md` and `docs/app-architecture.md §4` (user workflows) — understand what each screen does before designing it.

## Your priorities

MindBridge is used by people in moments of vulnerability. Design must be:
1. **Calm** — nothing loud, bouncy, or alarming unless it IS an alarm (the urgent banner)
2. **Clear** — one job per screen, one action per moment
3. **Warm** — feels like a supportive companion, not a clinical form
4. **Trustworthy** — patients share dark moments; the design must earn that

## Task queue (do in order)

### D1 — Brand guidelines
Define: primary color (indigo), semantic colors (red=crisis, amber=warning, green=positive), neutral palette, typography scale, icon library (Lucide), companion name recommendation. Write to `10-spec/brand-guidelines.md`. **Done when:** Person 3 can open this and know exactly which colours/fonts to use without asking.

### D2 — UX flows (patient app)
Document the 4 key flows: onboarding/consent, daily check-in, AI chat + crisis path, settings. ASCII diagrams or Mermaid in the vault. Include edge cases (API down, first-time vs returning user). Write to `10-spec/ux-flows/patient-app.md`. **Done when:** Person 3 has no questions about how screens connect.

### D3 — UX flows (therapist dashboard)
Document: patient list → patient detail, Overview tab, Conversations tab, Coping Plans tab. Include the URGENT banner behaviour. Write to `10-spec/ux-flows/dashboard.md`. **Done when:** Person 3 can build the dashboard navigation without asking you.

### D4 — Component specs (priority: demo path)
Write developer-ready specs for these components (in order): MoodSlider, DisclaimerBanner, CrisisModal, UrgentFlagBanner, MoodChart, CopingPlanCard+Form. For each: visual anatomy, states (default/pressed/loading/error/empty), spacing, typography, colours, interactions. Write to `10-spec/component-specs/<name>.md`. **Done when:** Person 3 can implement each without a design conversation.

### D5 — UI copy
Write all user-facing text: onboarding/consent copy, check-in prompts (5 rotation variants), chat empty state, fallback reply, disclaimer banner, crisis modal text, all error messages, therapist dashboard labels and empty states. Write to `10-spec/ui-copy.md`. **Done when:** there are zero placeholder strings ("Lorem ipsum", "TODO: copy") in the app.

### D6 — Accessibility review
Review Person 3's implementation for: colour contrast (WCAG AA), minimum touch targets (44px mobile), screen reader labels on interactive elements, keyboard navigation on dashboard. Write findings to `50-flags/accessibility-D.md`. **Done when:** no WCAG AA failures in the demo path.

### D7 — Demo visual polish
Collaborate with Person 3 on the final polish pass. Review the app on a real device / browser. Flag anything that looks wrong for the demo. Write a short "visual QA" note in `40-handoffs/<date>-D.md`. **Done when:** you'd be comfortable showing this to a judge.

## Cut lines

Dark mode → advanced animation specs → marketing site copy. Never cut: brand guidelines (D1), component specs for the demo path (D4), UI copy (D5).

## Hard rules

- The disclaimer banner copy is non-negotiable — it must be visible and readable on every AI screen.
- Crisis modal copy must be calm, not alarming. No exclamation marks. No jargon.
- Component specs must include empty states — Person 3 needs to know what to show when there's no data.
- Coordinate with Person 5 on the companion's name — it appears everywhere and affects the pitch.

## Working style

You produce Markdown specs in the vault — that's your code. Be precise: "padding: 16px (p-4)" is more useful than "add some space". Person 3 will implement exactly what you spec, so if you're vague they'll guess.

Communicate blockers quickly. If you need to know what a screen does before you can spec it, ask Person 1 or 3 rather than guessing.

## Useful agents

`design-brand` · `design-ux-flows` · `design-spec-writer` · `design-accessibility` · `design-copy` · `shared-advisor`
