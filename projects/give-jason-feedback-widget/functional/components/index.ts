// ABOUTME: Barrel export for feedback widget components
// ABOUTME: Re-exports main component and types for easy importing

export { FeedbackWidget } from './FeedbackWidget';
export { FeedbackForm } from './FeedbackForm';
export { ScreenshotPreview } from './ScreenshotPreview';

export type {
  FeedbackUser,
  FeedbackWidgetProps,
  FeedbackFormData,
  FeedbackType,
  UrgencyLevel,
  AirtableConfig,
} from '../lib/types';
