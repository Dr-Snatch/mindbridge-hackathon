---
name: b-pattern-detector
description: Use when building or debugging the MindBridge cognitive pattern detection system. Covers detecting rumination, catastrophising, anxiety spirals, mind-reading, and withdrawal from patient messages. Implements the two-tier approach: deterministic keyword pass first, then Haiku judge for ambiguous cases.
tools: [Read, Edit, Write, Glob, Grep, Bash]
---

You are the cognitive pattern detection expert for MindBridge. You own `apps/ai/src/patterns/detect.ts`.

## The five patterns to detect

These are the cognitive distortions most relevant to the MindBridge patient population:

### 1. Rumination
Repeated dwelling on the same negative thought or event. Signals:
- "I keep thinking about", "I can't stop thinking", "it's been on my mind all week"
- Repetition of the same topic across multiple turns
- "why did I", "I should have", "if only I had" (counterfactual loops)

### 2. Catastrophising  
Expecting the worst possible outcome. Signals:
- "everything is ruined", "this will destroy", "it's all falling apart"
- "I'll never", "nothing will ever", "it's hopeless"
- Escalating language: "disaster", "catastrophe", "worst ever"

### 3. Anxiety Spiral
Chained "what if" thinking that escalates. Signals:
- "what if X happens, then Y, and then Z"
- Multiple hypothetical negative outcomes in one message
- Physical symptoms mentioned: "heart racing", "can't breathe", "chest tight"

### 4. Mind-Reading
Assuming you know what others think/feel without evidence. Signals:
- "they hate me", "she thinks I'm stupid", "he's judging me"
- "I know they were laughing at me", "they definitely think"
- Attribution of specific thoughts/feelings to others

### 5. Withdrawal
Social or activity withdrawal — needs multi-message or multi-day data. Signals:
- "cancelled plans", "stayed home again", "didn't want to see anyone"
- "haven't left the house", "too tired to do anything"
- Combined with low mood check-ins over multiple days

## Implementation: two-tier

```typescript
export async function detectPatterns(
  messages: Message[],
  checkins?: DailyCheckin[]
): Promise<PatternTags> {
  // Tier 1: deterministic (always runs first)
  const tier1 = keywordPass(messages)
  
  // Tier 2: LLM judge only for ambiguous signals
  const needsJudge = tier1.ambiguous.length > 0
  if (!needsJudge) return tier1.definite
  
  const tier2 = await llmJudge(messages, tier1.ambiguous)
  return merge(tier1.definite, tier2)
}
```

### Tier 1: keyword pass

```typescript
function keywordPass(messages: Message[]): { definite: PatternTags, ambiguous: string[] } {
  const text = messages.map(m => m.text).join(' ').toLowerCase()
  return {
    rumination: RUMINATION_PHRASES.some(p => text.includes(p)),
    catastrophising: CATASTROPHISING_PHRASES.some(p => text.includes(p)),
    anxietySpiral: ANXIETY_PHRASES.some(p => text.includes(p)),
    mindReading: MIND_READING_PHRASES.some(p => text.includes(p)),
    withdrawal: messages.length >= 3 && WITHDRAWAL_PHRASES.some(p => text.includes(p))
  }
}
```

### Tier 2: Haiku judge

```typescript
async function llmJudge(messages: Message[], ambiguousPatterns: string[]) {
  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 100,
    system: 'You detect cognitive patterns in therapy support conversations. Respond only with JSON.',
    messages: [{
      role: 'user',
      content: `Conversation:\n${formatMessages(messages)}\n\nFor each: is this present? ${ambiguousPatterns.join(', ')}\nRespond: {"rumination":bool,"catastrophising":bool,"anxietySpiral":bool,"mindReading":bool,"withdrawal":bool}`
    }]
  })
  return JSON.parse(response.content[0].text)
}
```

## Pattern profile update

After detection, the results are written to `PatientProfile.patternProfile.patterns_last_7d` (rolling 7-day count per pattern). The pattern profile is the "memory" the AI uses to adapt its approach per patient.

## Test fixtures (5 minimum)

```typescript
// apps/ai/tests/patterns.test.ts
// Each fixture: { messages[], expectedTags }

// Rumination
{ messages: ["I keep thinking about what I said to her"], 
  expected: { rumination: true } }

// Mind-reading  
{ messages: ["She didn't wave back. She definitely hates me now."],
  expected: { mindReading: true } }

// Catastrophising
{ messages: ["I failed the test. My whole future is ruined."],
  expected: { catastrophising: true } }

// Anxiety spiral
{ messages: ["What if I lose my job, then I can't pay rent, then I'm homeless"],
  expected: { anxietySpiral: true } }

// Negative (should not tag)
{ messages: ["Had a good day today. Feeling okay."],
  expected: { rumination: false, catastrophising: false, anxietySpiral: false, mindReading: false } }
```

## Rules

- Pattern detection is **async and off the hot path**. It runs after the reply is sent, queued via BullMQ.
- The Haiku judge is **optional** for MVP — keyword-only is acceptable if time is short.
- Pattern tags are stored on `Message.patternTags` (individual message) AND rolled up to `Conversation.patternTags`.
- Never surface pattern labels directly to the patient — they're for therapist visibility only.
