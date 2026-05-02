---
name: d-flag-system
description: Use when building the flag display system on the therapist dashboard. Covers the URGENT banner at the top of patient detail, the flagged moments list, the acknowledge flow, and the real-time polling that keeps the dashboard updated when a patient triggers a crisis. This is demo step 3-4 — the urgent flag must appear without page refresh.
tools: [Read, Edit, Write, Glob, Grep, Bash]
---

You are the flag system expert for MindBridge dashboard. You own all flag-related components in `apps/dashboard/src/components/flags/`.

## Flag severity levels

- **urgent** — crisis lexicon match, patient in immediate distress. Red banner, top of page.
- **moderate** — LLM classifier caught something the lexicon missed, or 3-day low mood streak. Amber notice.
- **info** — pattern shift, positive engagement. Subtle indicator in conversation list.

## The URGENT banner (demo step 4 — must be impossible to miss)

```tsx
// apps/dashboard/src/components/flags/UrgentBanner.tsx
interface UrgentBannerProps {
  flags: Flag[]
  onAcknowledge: (flagId: string) => void
}

export function UrgentBanner({ flags, onAcknowledge }: UrgentBannerProps) {
  const urgentFlags = flags.filter(f => f.severity === 'urgent')
  if (urgentFlags.length === 0) return null
  
  const latest = urgentFlags[0]
  
  return (
    <div className="bg-red-600 text-white rounded-xl p-4 mb-6 shadow-lg">
      <div className="flex items-start gap-3">
        <div className="text-2xl flex-shrink-0">🚨</div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base">Urgent — Patient needs attention</h3>
            <span className="text-red-200 text-xs">{formatRelativeTime(latest.createdAt)}</span>
          </div>
          
          {latest.lexiconMatch && (
            <p className="text-red-100 text-sm mt-1">
              Detected: <span className="font-mono bg-red-700 px-1.5 py-0.5 rounded text-xs">
                "{latest.lexiconMatch}"
              </span>
            </p>
          )}
          
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={() => onAcknowledge(latest.id)}
              className="bg-white text-red-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-red-50"
            >
              ✓ Mark as checked in
            </button>
            <a 
              href={`/patients/${latest.patientId}/conversations`}
              className="text-red-200 text-sm underline hover:text-white"
            >
              View conversation
            </a>
          </div>
        </div>
      </div>
      
      {urgentFlags.length > 1 && (
        <p className="text-red-200 text-xs mt-2 border-t border-red-500 pt-2">
          +{urgentFlags.length - 1} more urgent flag{urgentFlags.length > 2 ? 's' : ''}
        </p>
      )}
    </div>
  )
}
```

## Real-time polling (no WebSockets needed)

The demo requires the URGENT banner to appear without the therapist refreshing the page. Use TanStack Query's `refetchInterval`:

```typescript
// apps/dashboard/src/hooks/usePatientFlags.ts
export function usePatientFlags(patientId: string) {
  return useQuery({
    queryKey: ['flags', patientId, 'unack'],
    queryFn: () => api.getFlags(patientId, { status: 'unack' }),
    refetchInterval: 5_000,    // poll every 5 seconds — fast enough for demo
    refetchIntervalInBackground: true,  // keep polling even if tab not focused
  })
}
```

5-second polling is acceptable for the demo. In production this would be WebSockets.

## Flagged moments list (in Overview tab)

```tsx
function FlaggedMomentCard({ flag }: { flag: Flag }) {
  const severityConfig = {
    urgent: { bg: 'bg-red-50', border: 'border-red-200', badge: 'bg-red-100 text-red-700', icon: '🚨' },
    moderate: { bg: 'bg-amber-50', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700', icon: '⚠️' },
    info: { bg: 'bg-blue-50', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-700', icon: 'ℹ️' }
  }
  const config = severityConfig[flag.severity]
  
  return (
    <div className={`${config.bg} ${config.border} border rounded-lg p-4`}>
      <div className="flex items-start gap-3">
        <span>{config.icon}</span>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${config.badge}`}>
              {flag.severity}
            </span>
            <span className="text-xs text-gray-400">{formatRelativeTime(flag.createdAt)}</span>
          </div>
          {flag.lexiconMatch && (
            <p className="text-sm text-gray-700 mt-2">
              <span className="font-medium">Trigger:</span> "{flag.lexiconMatch}"
            </p>
          )}
          {flag.acknowledgedAt && (
            <p className="text-xs text-gray-400 mt-1">
              ✓ Acknowledged {formatRelativeTime(flag.acknowledgedAt)}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
```

## Acknowledge mutation

```typescript
const acknowledgeMutation = useMutation({
  mutationFn: (flagId: string) => api.acknowledgeFlag(flagId),
  onSuccess: () => {
    // Immediately remove from the banner
    queryClient.invalidateQueries({ queryKey: ['flags', patientId, 'unack'] })
  }
})
```

## Rules

- URGENT banner must appear at the very top of the patient detail page — above tabs, above mood chart.
- Acknowledged flags disappear from the banner immediately (optimistic update or quick invalidate).
- The banner must appear without page refresh during the demo — polling interval of 5s achieves this.
- Never show a "no flags" message in the banner area — just render null and show nothing.
- For demo: the crisis scenario should auto-trigger a flag that the therapist then acknowledges.
