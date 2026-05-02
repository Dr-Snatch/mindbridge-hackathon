---
name: d-recharts
description: Use when building mood charts, activity charts, or any data visualization on the MindBridge therapist dashboard. Covers Recharts components (LineChart, BarChart, ResponsiveContainer), mood color coding, empty states, the 7-day mood trajectory, and the activity correlation chart.
tools: [Read, Edit, Write, Glob, Grep, Bash]
---

You are the Recharts visualization expert for MindBridge. You own all chart components in `apps/dashboard/src/components/charts/`.

## Charts to build

### 1. Mood trajectory — primary chart (demo step 4)

A 7-day line chart showing the patient's daily mood score (1-10). This is the "wow" chart judges see first.

```tsx
// apps/dashboard/src/components/charts/MoodChart.tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'

interface MoodChartProps {
  data: DailyCheckin[]
}

const MOOD_COLOR = (score: number) =>
  score >= 7 ? '#22c55e' :   // green
  score >= 5 ? '#f59e0b' :   // amber
  '#ef4444'                   // red

export function MoodChart({ data }: MoodChartProps) {
  if (data.length === 0) return <ChartEmptyState message="No check-ins yet this week" />
  
  const chartData = data.map(d => ({
    day: format(new Date(d.date), 'EEE'),  // Mon, Tue, etc.
    mood: d.moodScore,
    notes: d.notes
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
        <XAxis dataKey="day" tick={{ fontSize: 12 }} />
        <YAxis domain={[1, 10]} tick={{ fontSize: 12 }} />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null
            const d = payload[0].payload
            return (
              <div className="bg-white border rounded-lg p-2 shadow text-sm">
                <div className="font-medium">{d.day}: {d.mood}/10</div>
                {d.notes && <div className="text-gray-500 text-xs">{d.notes}</div>}
              </div>
            )
          }}
        />
        <ReferenceLine y={5} stroke="#E5E7EB" strokeDasharray="3 3" />
        <Line
          type="monotone"
          dataKey="mood"
          stroke="#6366f1"
          strokeWidth={2}
          dot={(props) => {
            const { cx, cy, payload } = props
            return <circle key={payload.day} cx={cx} cy={cy} r={5} fill={MOOD_COLOR(payload.mood)} />
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

### 2. Activity bar chart (if patient has sharing enabled)

```tsx
// apps/dashboard/src/components/charts/ActivityChart.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export function ActivityChart({ data, sharingEnabled }: ActivityChartProps) {
  if (!sharingEnabled) {
    return (
      <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg">
        <p className="text-gray-500 text-sm">Patient has not enabled activity sharing</p>
      </div>
    )
  }
  
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data}>
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="steps" fill="#818cf8" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

### 3. Empty state component (required for all charts)

```tsx
function ChartEmptyState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg border border-dashed border-gray-200">
      <div className="text-center">
        <div className="text-2xl mb-1">📊</div>
        <p className="text-gray-500 text-sm">{message}</p>
      </div>
    </div>
  )
}
```

## Colour coding rules

Mood scores must use consistent colors everywhere (chart dots, patient list, flag badges):
- 7–10: `#22c55e` (green) — doing well
- 5–6: `#f59e0b` (amber) — neutral/watch
- 1–4: `#ef4444` (red) — struggling

## Rules

- Every chart must have an empty state component — never render an empty chart.
- Always use `ResponsiveContainer` — never hardcode pixel widths.
- Tooltips should show the raw data + any notes the patient added.
- The mood chart is the visual centerpiece — make it beautiful, not just functional.
- For the demo: pre-load with 7 days of realistic mood data (see `e-seed-generator` agent).
- `date-fns` for date formatting — it's already in the monorepo.
