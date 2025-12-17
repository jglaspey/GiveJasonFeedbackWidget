// ABOUTME: Feedback form component with dropdowns and textarea
// ABOUTME: Handles feedback type, urgency, and description fields

import React, { useState } from 'react';
import type { FeedbackFormData, FeedbackType, UrgencyLevel } from '../lib/types';

interface FeedbackFormProps {
  onSubmit: (data: FeedbackFormData) => void;
  isSubmitting: boolean;
}

const FEEDBACK_TYPES: FeedbackType[] = ['Bug', 'Feature request', 'Other'];
const URGENCY_LEVELS: UrgencyLevel[] = ['High', 'Medium', 'Low'];

export function FeedbackForm({ onSubmit, isSubmitting }: FeedbackFormProps) {
  const [feedbackType, setFeedbackType] = useState<FeedbackType>('Bug');
  const [urgency, setUrgency] = useState<UrgencyLevel>('Medium');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    onSubmit({
      feedbackType,
      urgency,
      description: description.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="feedback-form">
      {/* Feedback Type */}
      <div className="feedback-form-field">
        <label htmlFor="feedback-type">Type</label>
        <select
          id="feedback-type"
          value={feedbackType}
          onChange={(e) => setFeedbackType(e.target.value as FeedbackType)}
          disabled={isSubmitting}
        >
          {FEEDBACK_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Urgency */}
      <div className="feedback-form-field">
        <label htmlFor="feedback-urgency">Urgency</label>
        <select
          id="feedback-urgency"
          value={urgency}
          onChange={(e) => setUrgency(e.target.value as UrgencyLevel)}
          disabled={isSubmitting}
        >
          {URGENCY_LEVELS.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </div>

      {/* Description */}
      <div className="feedback-form-field">
        <label htmlFor="feedback-description">Description</label>
        <textarea
          id="feedback-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your feedback..."
          rows={4}
          disabled={isSubmitting}
          required
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="feedback-form-submit"
        disabled={isSubmitting || !description.trim()}
      >
        {isSubmitting ? 'Sending...' : 'Send Feedback'}
      </button>
    </form>
  );
}
