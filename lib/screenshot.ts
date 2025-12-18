// ABOUTME: Screenshot capture utility using html2canvas
// ABOUTME: Captures full page, resizes to max 800px width, and compresses to 60% JPG

import html2canvas from 'html2canvas';

const JPEG_QUALITY = 0.6;
const MAX_WIDTH = 800;

/**
 * Resizes a canvas to fit within max dimensions while preserving aspect ratio
 */
function resizeCanvas(sourceCanvas: HTMLCanvasElement): HTMLCanvasElement {
  const { width, height } = sourceCanvas;

  if (width <= MAX_WIDTH) {
    return sourceCanvas;
  }

  const scale = MAX_WIDTH / width;
  const newWidth = MAX_WIDTH;
  const newHeight = Math.round(height * scale);

  const resizedCanvas = document.createElement('canvas');
  resizedCanvas.width = newWidth;
  resizedCanvas.height = newHeight;

  const ctx = resizedCanvas.getContext('2d');
  if (ctx) {
    ctx.drawImage(sourceCanvas, 0, 0, newWidth, newHeight);
  }

  return resizedCanvas;
}

/**
 * Converts oklch/modern CSS colors to rgb in a cloned document
 * html2canvas doesn't support oklch() colors used by Tailwind CSS 4
 */
function convertColorsToRgb(clonedDoc: Document): void {
  const allElements = clonedDoc.querySelectorAll('*');
  allElements.forEach((el) => {
    const computed = window.getComputedStyle(el as Element);
    const htmlEl = el as HTMLElement;
    htmlEl.style.color = computed.color;
    htmlEl.style.backgroundColor = computed.backgroundColor;
    htmlEl.style.borderColor = computed.borderColor;
  });
}

/**
 * Captures the current page as a compressed JPG
 * Resizes to max 800px width and 60% quality to fit Airtable limits
 * Returns base64 encoded string (without data URI prefix)
 */
export async function capturePageScreenshot(): Promise<string> {
  const canvas = await html2canvas(document.body, {
    useCORS: true,
    allowTaint: true,
    scrollY: -window.scrollY,
    windowHeight: document.documentElement.scrollHeight,
    onclone: (clonedDoc) => convertColorsToRgb(clonedDoc),
  });

  const resizedCanvas = resizeCanvas(canvas);
  const dataUrl = resizedCanvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
}

/**
 * Captures a specific element as a compressed JPG
 * Returns base64 encoded string (without data URI prefix)
 */
export async function captureElementScreenshot(
  element: HTMLElement
): Promise<string> {
  const canvas = await html2canvas(element, {
    useCORS: true,
    allowTaint: true,
    onclone: (clonedDoc) => convertColorsToRgb(clonedDoc),
  });

  const resizedCanvas = resizeCanvas(canvas);
  const dataUrl = resizedCanvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
}

/**
 * Resizes an uploaded image file to fit within max dimensions
 * Returns base64 encoded string (without data URI prefix)
 */
export function resizeImageFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();

    reader.onload = (e) => {
      img.src = e.target?.result as string;
    };

    img.onload = () => {
      const canvas = document.createElement('canvas');
      let { width, height } = img;

      if (width > MAX_WIDTH) {
        const scale = MAX_WIDTH / width;
        width = MAX_WIDTH;
        height = Math.round(height * scale);
      }

      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(img, 0, 0, width, height);
      }

      const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
      resolve(dataUrl.replace(/^data:image\/jpeg;base64,/, ''));
    };

    img.onerror = () => reject(new Error('Failed to load image'));
    reader.onerror = () => reject(new Error('Failed to read file'));

    reader.readAsDataURL(file);
  });
}

/**
 * Converts a base64 string to a data URL for display
 */
export function base64ToDataUrl(base64: string): string {
  return `data:image/jpeg;base64,${base64}`;
}
