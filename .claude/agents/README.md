# MindBridge — Claude Code Agents

Specialized AI agents for the 5-person MindBridge hackathon team. Each agent has deep project context baked in — invoke one with `/agent <name>` or let Claude route to the right one automatically.

---

## Role A — Backend / API

| Agent | When to use |
|-------|-------------|
| `a-prisma-schema` | Designing or modifying the Prisma schema, adding entities, indexes, enums |
| `a-route-builder` | Implementing Express route handlers, auth, error handling |
| `a-contract-enforcer` | Auditing that implementation matches the API contract (read-only) |
| `a-railway-deployer` | Railway deployment, environment variables, Dockerfile, migration on deploy |

---

## Role B — AI / Patterns

| Agent | When to use |
|-------|-------------|
| `b-crisis-detector` | Building/testing the deterministic crisis lexicon and canned response |
| `b-prompt-engineer` | Designing the companion system prompt, CRISIS_MODE variant, disclaimer injection |
| `b-pattern-detector` | Building the cognitive pattern detection (rumination, catastrophising, etc.) |
| `b-summarizer` | Building the conversation summariser and theme extractor |
| `b-safety-auditor` | Auditing all 6 safety layers before demo (read-only) |
| `b-cache-optimizer` | Optimizing Anthropic prompt caching, debugging cache hit rates |
| `b-coping-injector` | Building coping plan retrieval and injection into the AI context |

---

## Role C — Patient Mobile App

| Agent | When to use |
|-------|-------------|
| `c-expo-component` | Building any Expo/React Native component, NativeWind styling, navigation |
| `c-checkin-flow` | The mood check-in screen — slider, notes, submission, success state |
| `c-chat-screen` | The AI chat interface — messages, typing indicator, sending, CRISIS_MODE |
| `c-crisis-modal` | The full-screen crisis modal — emergency contacts, tap-to-call, "I'm safe" |
| `c-mock-data` | Local fallback data and Zustand store — demo safety net if API is down |

---

## Role D — Therapist Dashboard

| Agent | When to use |
|-------|-------------|
| `d-recharts` | Mood trajectory chart, activity chart, chart empty states |
| `d-patient-overview` | Patient list sidebar, patient detail page, Overview tab |
| `d-coping-editor` | Coping plan form, plan list, crisis plan text editor |
| `d-flag-system` | URGENT banner, flagged moments list, acknowledge flow, polling |
| `d-tanstack-query` | QueryClient setup, API client, query keys, mutations, refetch intervals |

---

## Role E — Coordinator / Integrator

| Agent | When to use |
|-------|-------------|
| `e-task-triage` | Triaging blocked tasks, applying cut order, schedule checkpoints |
| `e-seed-generator` | Demo seed data — Alex's story, 7-day moods, conversations, crisis flag |
| `e-monorepo` | pnpm workspace config, inter-package imports, build order, common issues |
| `e-demo-rehearser` | Full 5-step demo validation, pre-demo checklist, what to do if something breaks |

---

## Design (non-technical roles)

| Agent | When to use |
|-------|-------------|
| `design-brand` | Brand identity, color palette, typography, logo direction, voice |
| `design-ux-flows` | User journey maps, screen flow diagrams, interaction notes |
| `design-spec-writer` | Component specifications for developers — anatomy, states, spacing |
| `design-accessibility` | Color contrast, touch targets, screen reader labels, WCAG audit |
| `design-copy` | UI text, microcopy, error messages, onboarding copy, placeholders |
| `design-pitch` | Pitch deck structure, 90-second demo script, judge-facing narrative |

---

## Shared (any role)

| Agent | When to use |
|-------|-------------|
| `shared-standup` | Generate 3-bullet standup from vault task state |
| `shared-advisor` | Architecture decisions, feature trade-offs, anything that doesn't fit a role |
| `shared-types` | Reference for TypeScript type shapes in `packages/types` |
| `shared-demo-validator` | Full integration check of all 5 demo steps with API commands |

---

## How agents relate to the demo path

```
Demo step 1 (mood check-in):   c-checkin-flow + a-route-builder
Demo step 2 (AI chat):         c-chat-screen + b-prompt-engineer + b-coping-injector
Demo step 3 (crisis):          c-crisis-modal + b-crisis-detector + a-route-builder
Demo step 4 (dashboard):       d-patient-overview + d-recharts + d-flag-system
Demo step 5 (coping plan):     d-coping-editor + b-coping-injector + a-route-builder
```

Safety audit before demo: `b-safety-auditor`
Full integration check: `shared-demo-validator`
Pre-demo rehearsal: `e-demo-rehearser`
