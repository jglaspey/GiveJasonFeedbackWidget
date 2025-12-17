# Give Jason Feedback Widget

A drop-in React component for collecting user feedback with automatic screenshot capture.

## Features

- Slide-in panel from right edge
- Auto-captures full page screenshot on open
- Add multiple screenshots
- Feedback type (Bug/Feature request/Other) and urgency (High/Medium/Low) dropdowns
- Sends feedback to Airtable
- TypeScript support
- Tailwind-compatible styles

## Installation

### 1. Copy the files

Copy the following directories into your project:

```
components/
├── FeedbackWidget.tsx
├── FeedbackForm.tsx
├── ScreenshotPreview.tsx
└── index.ts

lib/
├── types.ts
├── screenshot.ts
└── airtable.ts

styles/
└── feedback-widget.css
```

### 2. Install dependencies

```bash
npm install html2canvas
```

### 3. Import the CSS

In your app's entry point (e.g., `_app.tsx` or `layout.tsx`):

```tsx
import './path/to/styles/feedback-widget.css';
```

### 4. Set up Airtable

Create a table in Airtable with these fields:

| Field Name | Field Type | Notes |
|------------|------------|-------|
| Timestamp | Date/Time | |
| User Email | Email | |
| User ID | Single line text | |
| App Name | Single line text | |
| Page URL | URL | |
| Feedback Type | Single select | Options: Bug, Feature request, Other |
| Urgency | Single select | Options: High, Medium, Low |
| Description | Long text | |
| Screenshots | Long text | Stores base64 JSON array |

### 5. Configure environment variables

Add to your `.env`:

```
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=your_base_id_here
AIRTABLE_TABLE_NAME=Feedback
```

## Usage

### With NextAuth

```tsx
import { FeedbackWidget } from './components';
import { useSession } from 'next-auth/react';

export default function App() {
  const { data: session } = useSession();

  return (
    <div>
      {/* Your app content */}

      {session?.user && (
        <FeedbackWidget
          user={session.user}
          appName="My App"
          airtableConfig={{
            apiKey: process.env.NEXT_PUBLIC_AIRTABLE_API_KEY!,
            baseId: process.env.NEXT_PUBLIC_AIRTABLE_BASE_ID!,
            tableName: process.env.NEXT_PUBLIC_AIRTABLE_TABLE_NAME!,
          }}
        />
      )}
    </div>
  );
}
```

### With BetterAuth

```tsx
import { FeedbackWidget } from './components';
import { useAuth } from '@better-auth/react';

export default function App() {
  const { user } = useAuth();

  return (
    <div>
      {/* Your app content */}

      {user && (
        <FeedbackWidget
          user={user}
          appName="My App"
          airtableConfig={{
            apiKey: process.env.NEXT_PUBLIC_AIRTABLE_API_KEY!,
            baseId: process.env.NEXT_PUBLIC_AIRTABLE_BASE_ID!,
            tableName: process.env.NEXT_PUBLIC_AIRTABLE_TABLE_NAME!,
          }}
        />
      )}
    </div>
  );
}
```

## Customizing Styles

The widget uses CSS variables that you can override to match your theme:

```css
:root {
  --feedback-primary: #2563eb;
  --feedback-primary-hover: #1d4ed8;
  --feedback-bg: #ffffff;
  --feedback-text: #1f2937;
  --feedback-text-muted: #6b7280;
  --feedback-border: #e5e7eb;
  --feedback-error: #dc2626;
  --feedback-success: #16a34a;
  --feedback-overlay: rgba(0, 0, 0, 0.5);
}
```

## Props

### FeedbackWidgetProps

| Prop | Type | Description |
|------|------|-------------|
| `user` | `FeedbackUser` | Current logged-in user |
| `appName` | `string` | Name of your app (included in feedback) |
| `airtableConfig` | `AirtableConfig` | Airtable connection settings |

### FeedbackUser

```typescript
interface FeedbackUser {
  id?: string;
  email?: string;
  name?: string;
}
```

### AirtableConfig

```typescript
interface AirtableConfig {
  apiKey: string;
  baseId: string;
  tableName: string;
}
```

## Security Note

The Airtable API key is used client-side. For production apps, consider:

1. Creating a proxy API route that handles Airtable requests server-side
2. Using a restricted API key with only create permissions on the feedback table
