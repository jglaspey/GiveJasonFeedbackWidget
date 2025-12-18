// ABOUTME: Airtable API integration for submitting feedback
// ABOUTME: Creates record then uploads screenshots as proper attachments

import type { AirtableConfig, FeedbackSubmission } from './types';

const AIRTABLE_API_URL = 'https://api.airtable.com/v0';
const AIRTABLE_CONTENT_URL = 'https://content.airtable.com/v0';

interface AirtableRecordFields {
  Timestamp: string;
  'User Email': string;
  'User ID': string;
  'App Name': string;
  'Page URL': string;
  'Feedback Type': string;
  Urgency: string;
  Description: string;
}

interface CreateRecordResponse {
  id: string;
  createdTime: string;
  fields: AirtableRecordFields;
}

/**
 * Creates a feedback record in Airtable (without screenshots)
 */
async function createFeedbackRecord(
  config: AirtableConfig,
  submission: FeedbackSubmission
): Promise<{ success: boolean; recordId?: string; error?: string }> {
  const url = `${AIRTABLE_API_URL}/${config.baseId}/${encodeURIComponent(config.tableName)}`;

  const record = {
    fields: {
      Timestamp: submission.timestamp,
      'User Email': submission.user.email || '',
      'User ID': submission.user.id || '',
      'App Name': submission.appName,
      'Page URL': submission.pageUrl,
      'Feedback Type': submission.feedbackType,
      Urgency: submission.urgency,
      Description: submission.description,
    },
  };

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

  const data: CreateRecordResponse = await response.json();
  return { success: true, recordId: data.id };
}

/**
 * Uploads a single screenshot attachment to an existing record
 */
async function uploadAttachment(
  config: AirtableConfig,
  recordId: string,
  base64Image: string,
  index: number
): Promise<{ success: boolean; error?: string }> {
  const url = `${AIRTABLE_CONTENT_URL}/${config.baseId}/${recordId}/Screenshots/uploadAttachment`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${config.apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contentType: 'image/jpeg',
      file: base64Image,
      filename: `screenshot-${index + 1}.jpg`,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    return {
      success: false,
      error: errorData.error?.message || `HTTP ${response.status}`,
    };
  }

  return { success: true };
}

/**
 * Submits feedback to Airtable with proper attachment uploads
 * 1. Creates the feedback record
 * 2. Uploads each screenshot as an attachment
 */
export async function submitFeedback(
  config: AirtableConfig,
  submission: FeedbackSubmission
): Promise<{ success: boolean; error?: string }> {
  try {
    // Step 1: Create the feedback record
    const createResult = await createFeedbackRecord(config, submission);
    if (!createResult.success || !createResult.recordId) {
      return { success: false, error: createResult.error };
    }

    // Step 2: Upload each screenshot as an attachment
    for (let i = 0; i < submission.screenshots.length; i++) {
      const uploadResult = await uploadAttachment(
        config,
        createResult.recordId,
        submission.screenshots[i],
        i
      );
      if (!uploadResult.success) {
        // Record was created but attachment failed - log but don't fail entirely
        console.error(`Failed to upload screenshot ${i + 1}:`, uploadResult.error);
      }
    }

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}
