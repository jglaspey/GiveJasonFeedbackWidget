// ABOUTME: Screenshot preview component with thumbnail gallery
// ABOUTME: Displays screenshots with upload and capture functionality

import React, { useRef } from 'react';
import { base64ToDataUrl } from '../lib/screenshot';

interface ScreenshotPreviewProps {
  screenshots: string[];
  onCapture: () => void;
  onUpload: (file: File) => void;
  onRemove: (index: number) => void;
}

export function ScreenshotPreview({
  screenshots,
  onCapture,
  onUpload,
  onRemove,
}: ScreenshotPreviewProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      // Reset input so same file can be selected again
      e.target.value = '';
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="screenshot-preview">
      <div className="screenshot-preview-header">
        <span>Screenshots ({screenshots.length})</span>
        <div className="screenshot-preview-actions">
          <button
            type="button"
            onClick={handleUploadClick}
            className="screenshot-preview-btn"
            aria-label="Upload a screenshot"
          >
            Upload screenshot
          </button>
          <button
            type="button"
            onClick={onCapture}
            className="screenshot-preview-btn"
            aria-label="Capture this page"
          >
            Capture this page
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
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
          No screenshots yet
        </p>
      )}
    </div>
  );
}
