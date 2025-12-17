// ABOUTME: Screenshot capture utility using html2canvas
// ABOUTME: Captures full page and compresses to 70% quality JPG

import html2canvas from 'html2canvas';

const JPEG_QUALITY = 0.7;

/**
 * Captures the current page as a 70% quality JPG
 * Returns base64 encoded string (without data URI prefix)
 */
export async function capturePageScreenshot(): Promise<string> {
  const canvas = await html2canvas(document.body, {
    useCORS: true,
    allowTaint: true,
    scrollY: -window.scrollY,
    windowHeight: document.documentElement.scrollHeight,
  });

  // Convert to 70% quality JPG and strip data URI prefix
  const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
}

/**
 * Captures a specific element as a 70% quality JPG
 * Returns base64 encoded string (without data URI prefix)
 */
export async function captureElementScreenshot(
  element: HTMLElement
): Promise<string> {
  const canvas = await html2canvas(element, {
    useCORS: true,
    allowTaint: true,
  });

  const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
}

/**
 * Converts a base64 string to a data URL for display
 */
export function base64ToDataUrl(base64: string): string {
  return `data:image/jpeg;base64,${base64}`;
}
