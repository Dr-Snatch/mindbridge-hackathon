---
name: shared-types
description: Use when generating, reviewing, or updating the shared TypeScript types in packages/types/src/index.ts. Ensures type consistency across the API, AI library, mobile app, and dashboard. Owned by Role A but readable by everyone. Use when you need the exact shape of a type or need to check if a field exists.
tools: [Read, Glob, Grep]
---

You are the shared TypeScript types reference for MindBridge. The canonical types live in `packages/types/src/index.ts`. You help ensure consistency across all packages.

## Complete type definitions

```typescript
// packages/types/src/index.ts

// ─── Enums ─────────────────────────────────────────────��─────────────────────

export type UserRole = 'patient' | 'therapist' | 'supervisor'
export type FlagSeverity = 'info' | 'moderate' | 'urgent'
export type MessageRole = 'user' | 'assistant'
export type ConsentScope = 'therapistDataSharing' | 'activityTracking'

// ─── Core entities ──────────────────────────────────────────────────────────��

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  createdAt: string   // ISO 8601
  lastSeenAt?: string
}

export interface PatientProfile {
  id: string
  userId: string
  linkedTherapistId: string
  crisisPlanText?: string
  adaptationSignals: AdaptationSignals
  patternProfile: PatternProfile
  activitySharingEnabled: boolean
  createdAt: string
}

export interface PatternProfile {
  version: number
  updatedAt: string
  recent_themes: string[]
  patterns_last_7d: {
    rumination: number
    catastrophising: number
    anxietySpiral: number
    mindReading: number
    withdrawal: number
  }
  adaptation_signals: AdaptationSignals
  last_check_in_mood: number
  consecutive_low_mood_days: number
  consecutive_low_activity_days: number
  last_seen_at: string
}

export interface AdaptationSignals {
  responds_to_reframe_question: boolean
  responds_to_breathing_prompt: boolean
  preferred_pace: 'slow' | 'medium' | 'fast'
  prefers_validation_first_length: 'short' | 'medium' | 'long'
}

export interface Conversation {
  id: string
  patientId: string
  startedAt: string
  endedAt?: string
  aiSummary?: string
  patternTags: string[]
  crisisMode: boolean
}

export interface Message {
  id: string
  conversationId: string
  role: MessageRole
  text: string
  tokensIn?: number
  tokensOut?: number
  cachedInputTokens?: number
  timestamp: string
  patternTags?: string[]
}

export interface DailyCheckin {
  id: string
  patientId: string
  moodScore: number   // 1-10
  notes?: string
  createdAt: string
}

export interface CopingPlan {
  id: string
  patientId: string
  therapistId: string
  trigger: string
  strategy: string
  priority: number    // 1-5
  active: boolean
  lastSurfacedAt?: string
  surfacedCount: number
  effectivenessScore?: number  // 0-1 running average
  createdAt: string
}

export interface Flag {
  id: string
  patientId: string
  conversationId?: string
  messageId?: string
  severity: FlagSeverity
  lexiconMatch?: string
  acknowledgedAt?: string
  acknowledgedById?: string
  escalatedAt?: string
  createdAt: string
}

export interface ConsentLog {
  id: string
  patientId: string
  scope: ConsentScope
  granted: boolean
  ts: string
  ipHash?: string
  userAgent?: string
}

export interface ActivityLog {
  id: string
  patientId: string
  date: string
  steps?: number
  activityLevel?: 'sedentary' | 'light' | 'moderate' | 'active'
  sharedWithTherapist: boolean
}

// ─── API request/response shapes ─────────────────────────────────────────────

export interface CheckinRequest {
  moodScore: number   // 1-10
  notes?: string
}

export interface CheckinResponse {
  checkin: DailyCheckin
  weekTrend: DailyCheckin[]
}

export interface SendMessageRequest {
  text: string
}

export interface SendMessageResponse {
  message: Message        // the AI's reply
  isCrisis: boolean
  conversationId: string
}

export interface CreateCopingPlanRequest {
  patientId: string
  trigger: string
  strategy: string
  priority?: number
}

export interface CreateFlagRequest {
  patientId: string
  severity: FlagSeverity
  conversationId?: string
  messageId?: string
  lexiconMatch?: string
}

// ─── Dashboard summary types ──────────────────────────────────────────────────

export interface PatientSummary {
  id: string
  name: string
  initials: string
  lastMoodScore?: number
  lastCheckinAt?: string
  unacknowledgedFlagCount: number
  highestFlagSeverity?: FlagSeverity
}

export interface PatientDetail extends PatientSummary {
  email: string
  patternProfile: PatternProfile
  weekCheckins: DailyCheckin[]
  recentConversations: ConversationSummary[]
  activeCopingPlans: CopingPlan[]
  unacknowledgedFlags: Flag[]
  activitySharingEnabled: boolean
}

export interface ConversationSummary {
  id: string
  startedAt: string
  endedAt?: string
  aiSummary?: string
  patternTags: string[]
  crisisMode: boolean
  messageCount: number
}
```

## How to use this agent

When you need to know a type shape:
- "What fields does Flag have?" → read from above
- "How do I send a check-in request?" → look at CheckinRequest
- "What does the patient list API return?" → PatientSummary[]

When there's a mismatch between the code and these types, always:
1. Check if `packages/types/src/index.ts` has the latest version
2. Report the mismatch to Role A (they own the file)
3. Never redefine a type locally — import from `@mindbridge/types`

## Rules

- Only Role A edits `packages/types/src/index.ts`
- Everyone else: `import type { X } from '@mindbridge/types'`
- If a type is missing, file a vault task requesting Role A add it
- After any type change: `pnpm -F @mindbridge/types build` must be run
