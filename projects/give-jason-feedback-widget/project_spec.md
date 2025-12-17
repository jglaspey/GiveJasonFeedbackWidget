---
created_at: 2025-12-17T13:10:39-0800
last_updated: 2025-12-17T13:11:00-0800
timezone: America/Los_Angeles
type: prd
tags: [feedback, widget, react, typescript]
summary: "Drop-in React feedback widget for collecting user feedback across multiple SaaS apps"
---

# Give Jason Feedback Widget

## Purpose
Collect simple user feedback from beta testers across multiple SaaS applications. Provides a lightweight, drop-in solution that avoids external feedback tools while keeping implementation trivial.

## Target Apps
- Multiple small SaaS tools in beta testing
- Hosted on Railway and Vercel
- Tech stack: React, Node, TypeScript, Tailwind, shadcn/ui

## Current Process
No formal feedback collection - this is greenfield.

## UI/UX Requirements
- Slide-in overlay from the right side of screen
- Trigger: clickable tab/button always visible on edge
- Form fields:
  1. **Feedback type** (dropdown): Bug, Feature request, Other
  2. **Urgency** (dropdown): High, Medium, Low
  3. **Description** (text area): Explain the feedback
  4. **Screenshot**: Auto-captured on open + option to add more
  5. Submit button

### Auto-Captured Data (no user input needed)
- Current page URL
- Timestamp
- User identity (from app auth)
- Full page screenshot (auto-captured when widget opens)

## Technical Requirements
- Drop-in React component (copy-paste distribution)
- Configuration via environment variables
- Clear documentation for easy setup across apps
- Must work with existing Tailwind/shadcn styling
- Screenshots compressed to 70% quality JPG before upload

## Inputs
- **User identity**: Passed as React prop (`user` object with `email` and/or `id`)
  - Works with NextAuth (`session.user`) and BetterAuth (`useAuth().user`)
- Form responses (dropdowns + text)
- App identifier (config prop or env var)

## Outputs
- **Destination**: Airtable (existing base with auth already configured)
- **Screenshot storage**: Airtable attachment field (compressed 70% JPG)
- **Fields per record**:
  - Timestamp (auto)
  - User ID/email (auto from app auth)
  - App name (config)
  - Page URL (auto)
  - Feedback type (Bug/Feature request/Other)
  - Urgency (High/Medium/Low)
  - Description (text)
  - Screenshots (attachment field - 1 or more compressed JPGs)

## Constraints
- Must use existing Airtable base/auth (env var for API key + base ID)

## Workflow Steps

### User Flow
1. User clicks feedback tab on right edge of screen
2. Widget slides in, auto-captures full page screenshot
3. User sees screenshot thumbnail, can add more if needed
4. User selects feedback type (Bug/Feature/Other)
5. User selects urgency (High/Medium/Low)
6. User writes description
7. User clicks Submit
8. Widget compresses screenshots to 70% JPG
9. Widget POSTs to Airtable API
10. Widget shows success message, slides closed

### Integration Flow (for developers)
1. Copy widget component files into app
2. Add env vars: `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME`
3. Import component and render with `user` prop
4. Done

## Validation Results
| Assumption | Tested | Result | Impact |
|------------|--------|--------|--------|

## Open Questions
None - ready for validation and implementation planning.

## Technical Assumptions to Validate
- `html2canvas` captures full page screenshots reliably
- Canvas can export to 70% quality JPG
- Airtable API accepts base64 image uploads to attachment fields
