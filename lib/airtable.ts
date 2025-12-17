// ABOUTME: Airtable API integration for submitting feedback
// ABOUTME: POSTs feedback data including base64 screenshots to Airtable

import type { AirtableConfig, FeedbackSubmission } from './types';

const AIRTABLE_API_URL = 'https://api.airtable.com/v0';

interface AirtableRecord {
  fields: {
    Timestamp: string;
    'User Email': string;
    'User ID': string;
    'App Name': string;
    'Page URL': string;
    'Feedback Type': string;
    Urgency: string;
    Description: string;
    Screenshots: string;
  };
}

/**
 * Submits feedback to Airtable
 * Screenshots are stored as JSON array of base64 strings in a Long Text field
 */
export async function submitFeedback(
  config: AirtableConfig,
  submission: FeedbackSubmission
): Promise<{ success: boolean; error?: string }> {
  const url = `${AIRTABLE_API_URL}/${config.baseId}/${encodeURIComponent(config.tableName)}`;

  const record: AirtableRecord = {
    fields: {
      Timestamp: submission.timestamp,
      'User Email': submission.user.email || '',
      'User ID': submission.user.id || '',
      'App Name': submission.appName,
      'Page URL': submission.pageUrl,
      'Feedback Type': submission.feedbackType,
      Urgency: submission.urgency,
      Description: submission.description,
      Screenshots: JSON.stringify(submission.screenshots),
    },
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(record),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.error?.message || `HTTP ${response.status}`,
      };
    }

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}
