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
 * Converts oklch/modern CSS colors to rgb before html2canvas runs
 * html2canvas doesn't support oklch() colors used by Tailwind CSS 4
 * Returns a restore function to revert the DOM changes
 */
function convertColorsToRgb(): () => void {
  const elementsWithStyles: Array<{
    el: HTMLElement;
    original: string;
    computed: {
      color: string;
      backgroundColor: string;
      borderColor: string;
      borderTopColor: string;
      borderRightColor: string;
      borderBottomColor: string;
      borderLeftColor: string;
      outlineColor: string;
      textDecorationColor: string;
      boxShadow: string;
      caretColor: string;
    };
  }> = [];
  const removedStyleElements: Array<{ el: Element; parent: Node; nextSibling: Node | null }> = [];

  // Step 1: Capture ALL computed styles BEFORE removing stylesheets
  document.querySelectorAll('*').forEach((el) => {
    const htmlEl = el as HTMLElement;
    const computed = window.getComputedStyle(el);

    elementsWithStyles.push({
      el: htmlEl,
      original: htmlEl.getAttribute('style') || '',
      computed: {
        color: computed.color,
        backgroundColor: computed.backgroundColor,
        borderColor: computed.borderColor,
        borderTopColor: computed.borderTopColor,
        borderRightColor: computed.borderRightColor,
        borderBottomColor: computed.borderBottomColor,
        borderLeftColor: computed.borderLeftColor,
        outlineColor: computed.outlineColor,
        textDecorationColor: computed.textDecorationColor,
        boxShadow: computed.boxShadow,
        caretColor: computed.caretColor,
      },
    });
  });

  // Step 2: REMOVE all style and link[rel=stylesheet] elements from DOM
  // html2canvas reads these directly, disabling CSSStyleSheet isn't enough
  document.querySelectorAll('style, link[rel="stylesheet"]').forEach((el) => {
    if (el.parentNode) {
      removedStyleElements.push({
        el,
        parent: el.parentNode,
        nextSibling: el.nextSibling,
      });
      el.parentNode.removeChild(el);
    }
  });

  // Step 3: Apply the captured computed styles inline
  elementsWithStyles.forEach(({ el, computed }) => {
    el.style.color = computed.color;
    el.style.backgroundColor = computed.backgroundColor;
    el.style.borderColor = computed.borderColor;
    el.style.borderTopColor = computed.borderTopColor;
    el.style.borderRightColor = computed.borderRightColor;
    el.style.borderBottomColor = computed.borderBottomColor;
    el.style.borderLeftColor = computed.borderLeftColor;
    el.style.outlineColor = computed.outlineColor;
    el.style.textDecorationColor = computed.textDecorationColor;
    el.style.boxShadow = computed.boxShadow;
    el.style.caretColor = computed.caretColor;
  });

  // Return restore function
  return () => {
    // Restore inline styles
    elementsWithStyles.forEach(({ el, original }) => {
      if (original) {
        el.setAttribute('style', original);
      } else {
        el.removeAttribute('style');
      }
    });

    // Re-insert style elements in original positions
    removedStyleElements.forEach(({ el, parent, nextSibling }) => {
      try {
        parent.insertBefore(el, nextSibling);
      } catch {
        // Ignore errors if parent no longer exists
      }
    });
  };
}

/**
 * Captures the current page as a compressed JPG
 * Resizes to max 800px width and 60% quality to fit Airtable limits
 * Returns base64 encoded string (without data URI prefix)
 */
export async function capturePageScreenshot(): Promise<string> {
  // Convert oklch colors to rgb BEFORE html2canvas parses styles
  const restoreColors = convertColorsToRgb();

  try {
    const canvas = await html2canvas(document.body, {
      useCORS: true,
      allowTaint: true,
      scrollY: -window.scrollY,
      windowHeight: document.documentElement.scrollHeight,
    });

    const resizedCanvas = resizeCanvas(canvas);
    const dataUrl = resizedCanvas.toDataURL('image/jpeg', JPEG_QUALITY);
    return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
  } finally {
    // Restore original styles
    restoreColors();
  }
}

/**
 * Captures a specific element as a compressed JPG
 * Returns base64 encoded string (without data URI prefix)
 */
export async function captureElementScreenshot(
  element: HTMLElement
): Promise<string> {
  // Convert oklch colors to rgb BEFORE html2canvas parses styles
  const restoreColors = convertColorsToRgb();

  try {
    const canvas = await html2canvas(element, {
      useCORS: true,
      allowTaint: true,
    });

    const resizedCanvas = resizeCanvas(canvas);
    const dataUrl = resizedCanvas.toDataURL('image/jpeg', JPEG_QUALITY);
    return dataUrl.replace(/^data:image\/jpeg;base64,/, '');
  } finally {
    // Restore original styles
    restoreColors();
  }
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
