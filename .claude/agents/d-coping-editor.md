---
name: d-coping-editor
description: Use when building the coping plan editor on the therapist dashboard. Covers the form for creating/editing coping plans (trigger + strategy fields), the plan list view, the 'last surfaced' effectiveness indicator, and the crisis plan text editor. This is demo step 5 — therapist writes a plan that appears in the next patient chat.
tools: [Read, Edit, Write, Glob, Grep, Bash]
---

You are the coping plan editor expert for MindBridge. You own `apps/dashboard/src/components/CopingPlanEditor.tsx` and the Coping Plans tab.

## What this UI does (demo step 5)

Demo: "Therapist writes a coping plan → next time patient chats, AI surfaces it"

The therapist:
1. Opens patient detail → Coping Plans tab
2. Sees existing plans (or empty state)
3. Clicks "New plan"
4. Fills in: **Trigger** + **Strategy**
5. Saves → immediately available in patient's next AI conversation

## Plan list view

```tsx
// List of existing plans with effectiveness indicator
function CopingPlanList({ plans, patientId }: CopingPlanListProps) {
  if (plans.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-3xl mb-2">📋</div>
        <p className="font-medium">No coping plans yet</p>
        <p className="text-sm mt-1">Add a plan to guide the AI when this patient needs support</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {plans.map(plan => (
        <CopingPlanCard key={plan.id} plan={plan} patientId={patientId} />
      ))}
    </div>
  )
}

function CopingPlanCard({ plan, patientId }: { plan: CopingPlan; patientId: string }) {
  return (
    <div className={`border rounded-xl p-4 ${plan.active ? 'border-indigo-200 bg-indigo-50/30' : 'border-gray-200 opacity-60'}`}>
      <div className="flex justify-between items-start mb-3">
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
          plan.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
        }`}>
          {plan.active ? 'Active' : 'Inactive'}
        </span>
        <div className="flex items-center gap-2">
          {plan.lastSurfacedAt && (
            <span className="text-xs text-gray-400">
              Last surfaced {formatRelativeTime(plan.lastSurfacedAt)}
            </span>
          )}
          <button 
            onClick={() => togglePlanActive(plan.id, !plan.active)}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            {plan.active ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      </div>
      
      <div className="space-y-2">
        <div>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">When</span>
          <p className="text-sm text-gray-900 mt-0.5">{plan.trigger}</p>
        </div>
        <div>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Then</span>
          <p className="text-sm text-gray-900 mt-0.5">{plan.strategy}</p>
        </div>
      </div>
    </div>
  )
}
```

## New plan form

```tsx
function NewCopingPlanForm({ patientId, onSave }: NewCopingPlanFormProps) {
  const [trigger, setTrigger] = useState('')
  const [strategy, setStrategy] = useState('')
  const [saving, setSaving] = useState(false)
  
  async function handleSave() {
    if (!trigger.trim() || !strategy.trim()) return
    setSaving(true)
    try {
      await api.createCopingPlan({ patientId, trigger, strategy })
      onSave()  // close form, refetch list
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="border-2 border-indigo-200 rounded-xl p-5 bg-indigo-50/20">
      <h3 className="font-semibold text-gray-900 mb-4">New coping strategy</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            When... <span className="text-gray-400 font-normal">(describe the trigger situation)</span>
          </label>
          <textarea
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            rows={2}
            placeholder="e.g. patient assumes others are judging or disliking them without evidence"
            value={trigger}
            onChange={e => setTrigger(e.target.value)}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Then... <span className="text-gray-400 font-normal">(the strategy to surface)</span>
          </label>
          <textarea
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            rows={3}
            placeholder="e.g. gently ask: what evidence do I have for and against that interpretation? What would I tell a friend in this situation?"
            value={strategy}
            onChange={e => setStrategy(e.target.value)}
          />
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={!trigger.trim() || !strategy.trim() || saving}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-indigo-700"
          >
            {saving ? 'Saving...' : 'Save strategy'}
          </button>
          <button onClick={onSave} className="px-4 py-2 text-gray-600 text-sm hover:text-gray-800">
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
```

## Crisis plan text (separate from coping plans)

At the top of the Coping Plans tab, a special editor for the per-patient crisis response:

```tsx
<div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
  <h3 className="font-medium text-red-900 mb-1 text-sm">Crisis response instructions</h3>
  <p className="text-xs text-red-700 mb-3">
    If this patient sends a crisis message, these instructions will be included in the AI's canned response.
  </p>
  <textarea
    className="w-full border border-red-200 bg-white rounded-lg px-3 py-2 text-sm resize-none"
    rows={3}
    placeholder="e.g. Alex's emergency contact is their sister Maria (555-0192). Prefer this over the general crisis line."
    value={crisisPlanText}
    onChange={e => setCrisisPlanText(e.target.value)}
  />
  <button onClick={saveCrisisPlan} className="mt-2 text-xs font-medium text-red-700 hover:text-red-900">
    Save
  </button>
</div>
```

## Rules

- Trigger field is required. Strategy field is required. Both must be non-empty before Save is enabled.
- New plans are immediately active by default.
- After saving, refetch the plan list — the therapist should see their plan immediately.
- For demo: pre-populate with 1 example plan that matches the demo script trigger.
