// ABOUTME: Screenshot preview component with thumbnail gallery
// ABOUTME: Displays captured screenshots with add/remove functionality

import React from 'react';
import { base64ToDataUrl } from '../lib/screenshot';

interface ScreenshotPreviewProps {
  screenshots: string[];
  onAdd: () => void;
  onRemove: (index: number) => void;
}

export function ScreenshotPreview({
  screenshots,
  onAdd,
  onRemove,
}: ScreenshotPreviewProps) {
  return (
    <div className="screenshot-preview">
      <div className="screenshot-preview-header">
        <span>Screenshots ({screenshots.length})</span>
        <button
          type="button"
          onClick={onAdd}
          className="screenshot-preview-add"
          aria-label="Capture another screenshot"
        >
          + Add
        </button>
      </div>

      {screenshots.length > 0 ? (
        <div className="screenshot-preview-grid">
          {screenshots.map((screenshot, index) => (
            <div key={index} className="screenshot-preview-item">
              <img
                src={base64ToDataUrl(screenshot)}
                alt={`Screenshot ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => onRemove(index)}
                className="screenshot-preview-remove"
                aria-label={`Remove screenshot ${index + 1}`}
              >
                &times;
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="screenshot-preview-empty">
          No screenshots captured yet
        </p>
      )}
    </div>
  );
}
