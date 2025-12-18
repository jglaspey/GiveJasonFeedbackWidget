// ABOUTME: Main feedback widget component with slide-in panel
// ABOUTME: Orchestrates form, screenshots, and submission to Airtable

import React, { useState, useCallback, useEffect } from 'react';
import type {
  FeedbackWidgetProps,
  FeedbackFormData,
  FeedbackSubmission,
} from '../lib/types';
import { capturePageScreenshot } from '../lib/screenshot';
import { submitFeedback } from '../lib/airtable';
import { FeedbackForm } from './FeedbackForm';
import { ScreenshotPreview } from './ScreenshotPreview';
import '../styles/feedback-widget.css';

type WidgetState = 'closed' | 'open' | 'submitting' | 'success' | 'error';

export function FeedbackWidget({
  user,
  appName,
  airtableConfig,
}: FeedbackWidgetProps) {
  const [state, setState] = useState<WidgetState>('closed');
  const [screenshots, setScreenshots] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleOpen = useCallback(async () => {
    setState('open');
    // Auto-capture screenshot when opening
    try {
      const screenshot = await capturePageScreenshot();
      setScreenshots([screenshot]);
    } catch (error) {
      console.error('Failed to capture screenshot:', error);
      // Continue without screenshot - not a blocking error
      setScreenshots([]);
    }
  }, []);

  const handleClose = useCallback(() => {
    setState('closed');
    setScreenshots([]);
    setErrorMessage('');
  }, []);

  const handleCaptureScreenshot = useCallback(async () => {
    try {
      const screenshot = await capturePageScreenshot();
      setScreenshots((prev) => [...prev, screenshot]);
    } catch (error) {
      console.error('Failed to capture screenshot:', error);
    }
  }, []);

  const handleUploadScreenshot = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      // Strip data URI prefix to get just the base64
      const base64 = result.replace(/^data:image\/\w+;base64,/, '');
      setScreenshots((prev) => [...prev, base64]);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleRemoveScreenshot = useCallback((index: number) => {
    setScreenshots((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = useCallback(
    async (formData: FeedbackFormData) => {
      setState('submitting');
      setErrorMessage('');

      const submission: FeedbackSubmission = {
        timestamp: new Date().toISOString(),
        user,
        appName,
        pageUrl: window.location.href,
        feedbackType: formData.feedbackType,
        urgency: formData.urgency,
        description: formData.description,
        screenshots,
      };

      const result = await submitFeedback(airtableConfig, submission);

      if (result.success) {
        setState('success');
        // Auto-close after success
        setTimeout(() => {
          handleClose();
        }, 2000);
      } else {
        setState('error');
        setErrorMessage(result.error || 'Failed to submit feedback');
      }
    },
    [user, appName, screenshots, airtableConfig, handleClose]
  );

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && state !== 'closed') {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state, handleClose]);

  return (
    <>
      {/* Trigger button - always visible on right edge */}
      {state === 'closed' && (
        <button
          onClick={handleOpen}
          className="feedback-widget-trigger"
          aria-label="Open feedback form"
        >
          Give Jason Feedback
        </button>
      )}

      {/* Slide-in panel */}
      {state !== 'closed' && (
        <div className="feedback-widget-overlay" onClick={handleClose}>
          <div
            className="feedback-widget-panel"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="feedback-widget-header">
              <h2>Send Feedback</h2>
              <button
                onClick={handleClose}
                className="feedback-widget-close"
                aria-label="Close feedback form"
              >
                &times;
              </button>
            </div>

            {/* Content */}
            <div className="feedback-widget-content">
              {state === 'success' ? (
                <div className="feedback-widget-success">
                  <p>Thanks for your feedback!</p>
                </div>
              ) : state === 'error' ? (
                <div className="feedback-widget-error">
                  <p>Error: {errorMessage}</p>
                  <button
                    onClick={() => setState('open')}
                    className="feedback-widget-retry"
                  >
                    Try Again
                  </button>
                </div>
              ) : (
                <>
                  <ScreenshotPreview
                    screenshots={screenshots}
                    onCapture={handleCaptureScreenshot}
                    onUpload={handleUploadScreenshot}
                    onRemove={handleRemoveScreenshot}
                  />
                  <FeedbackForm
                    onSubmit={handleSubmit}
                    isSubmitting={state === 'submitting'}
                  />
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
