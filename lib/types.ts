// ABOUTME: TypeScript interfaces for the feedback widget
// ABOUTME: Defines user, submission, and component prop types

export interface FeedbackUser {
  id?: string;
  email?: string;
  name?: string;
}

export type FeedbackType = 'Bug' | 'Feature request' | 'Other';
export type UrgencyLevel = 'High' | 'Medium' | 'Low';

export interface FeedbackSubmission {
  timestamp: string;
  user: FeedbackUser;
  appName: string;
  pageUrl: string;
  feedbackType: FeedbackType;
  urgency: UrgencyLevel;
  description: string;
  screenshots: string[]; // base64 JPGs
}

export interface AirtableConfig {
  apiKey: string;
  baseId: string;
  tableName: string;
}

export interface FeedbackWidgetProps {
  user: FeedbackUser;
  appName: string;
  airtableConfig: AirtableConfig;
}

export interface FeedbackFormData {
  feedbackType: FeedbackType;
  urgency: UrgencyLevel;
  description: string;
}
