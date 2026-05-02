---
name: d-patient-overview
description: Use when building the therapist dashboard patient views — the patient list sidebar and the patient detail page with its tabs (Overview, Conversations, Coping Plans, Activity). Covers the URGENT flag banner, mood summary, key themes display, and flagged moments list.
tools: [Read, Edit, Write, Glob, Grep, Bash]
---

You are the therapist dashboard page expert for MindBridge. You own `apps/dashboard/src/pages/` and the patient detail components.

## Page structure

```
/patients                    → PatientListPage (sidebar + outlet)
/patients/:id                → PatientDetailPage
/patients/:id?tab=overview   → Overview tab (default)
/patients/:id?tab=conversations  → Conversations tab
/patients/:id?tab=coping-plans   → Coping Plans tab
/patients/:id?tab=activity       → Activity tab
```

## Patient list (sidebar)

```tsx
// apps/dashboard/src/components/PatientList.tsx
function PatientListItem({ patient }: { patient: PatientSummary }) {
  const moodColor = getMoodColor(patient.lastMoodScore)
  const hasUrgentFlag = patient.unacknowledgedFlagCount > 0 && patient.highestFlagSeverity === 'urgent'
  
  return (
    <Link to={`/patients/${patient.id}`}>
      <div className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 rounded-lg cursor-pointer">
        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
          <span className="text-indigo-700 font-medium text-sm">{patient.initials}</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-900 truncate">{patient.name}</span>
            {hasUrgentFlag && (
              <span className="flex-shrink-0 w-2 h-2 rounded-full bg-red-500" />
            )}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span 
              className="text-xs font-medium"
              style={{ color: moodColor }}
            >
              {patient.lastMoodScore}/10
            </span>
            {patient.unacknowledgedFlagCount > 0 && (
              <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded-full">
                {patient.unacknowledgedFlagCount} flag{patient.unacknowledgedFlagCount > 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
```

## Patient detail — Overview tab (demo step 4)

This is what judges see: mood chart, urgent banner, themes, flagged moments.

```tsx
// apps/dashboard/src/pages/PatientOverview.tsx

// URGENT FLAG BANNER — must be impossible to miss
{urgentFlags.length > 0 && (
  <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 mb-6">
    <div className="flex items-start gap-3">
      <span className="text-2xl">🚨</span>
      <div className="flex-1">
        <h3 className="font-bold text-red-800 text-base">Urgent — Patient in Distress</h3>
        <p className="text-red-700 text-sm mt-1">
          {urgentFlags[0].lexiconMatch 
            ? `Flagged phrase: "${urgentFlags[0].lexiconMatch}"` 
            : 'Crisis keywords detected in conversation'}
          {' · '}{formatRelativeTime(urgentFlags[0].createdAt)}
        </p>
        <button 
          onClick={() => acknowledgeFlag(urgentFlags[0].id)}
          className="mt-2 text-sm font-medium text-red-700 underline"
        >
          Mark as checked in
        </button>
      </div>
    </div>
  </div>
)}

// Mood chart (see d-recharts agent)
<MoodChart data={weekCheckins} />

// Key themes (extracted nightly)
<div className="flex flex-wrap gap-2 mt-4">
  {patient.patternProfile.recent_themes.map(theme => (
    <span key={theme} className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-sm">
      {theme}
    </span>
  ))}
</div>

// Flagged moments
{flags.map(flag => (
  <FlaggedMomentCard key={flag.id} flag={flag} />
))}
```

## Conversations tab

Each conversation card:
```tsx
<div className="border rounded-lg p-4 hover:border-indigo-300 transition-colors">
  <div className="flex justify-between items-start">
    <span className="text-sm font-medium">{format(conversation.startedAt, 'EEE MMM d, h:mm a')}</span>
    <div className="flex gap-1">
      {conversation.patternTags.map(tag => (
        <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
          {tag}
        </span>
      ))}
    </div>
  </div>
  {conversation.aiSummary && (
    <p className="text-sm text-gray-600 mt-2 leading-relaxed">{conversation.aiSummary}</p>
  )}
  <button className="text-xs text-indigo-600 mt-2 font-medium">View full conversation →</button>
</div>
```

## Data fetching with TanStack Query

```typescript
// Patient detail data
const { data: patient } = useQuery({
  queryKey: ['patient', patientId],
  queryFn: () => api.getPatient(patientId),
  refetchInterval: 30_000  // poll every 30s (no websockets needed)
})

const { data: flags } = useQuery({
  queryKey: ['flags', patientId, 'unack'],
  queryFn: () => api.getFlags(patientId, { status: 'unack' }),
  refetchInterval: 10_000  // poll more frequently for urgent flags
})
```

## Rules

- URGENT flag banner must be at the TOP of the page — above everything else.
- Never show stale activity data — if sharing is off, show the "not enabled" message.
- All tabs must have empty states — never a broken empty page.
- Patient list mood color must match the chart colors exactly (use the shared `getMoodColor` util).
- Refetch interval is the substitute for WebSockets — 30s for general data, 10s for flags.
