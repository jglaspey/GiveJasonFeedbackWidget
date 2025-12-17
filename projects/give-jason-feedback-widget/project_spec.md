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
- Simple form with:
  - 2-3 dropdown questions
  - Text field for open feedback
  - Submit button
- Identifies which user is logged in

## Technical Requirements
- Drop-in React component
- Configuration via environment variables
- Clear documentation for easy setup across apps
- Must work with existing Tailwind/shadcn styling

## Inputs
- User identity (from app's existing auth)
- Form responses (dropdowns + text)
- App identifier (which app sent the feedback)

## Outputs
[To be discovered - where does feedback go?]

## Constraints
[To be discovered]

## Workflow Steps
[To be discovered]

## Validation Results
| Assumption | Tested | Result | Impact |
|------------|--------|--------|--------|

## Open Questions
- Where should feedback be stored/sent?
- What are the specific dropdown questions?
- How is user identity passed to the widget?
- npm package vs copy-paste code?
