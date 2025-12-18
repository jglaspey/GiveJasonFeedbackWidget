import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Point to the widget source files in parent directory
      '@widget': path.resolve(__dirname, '../'),
    },
  },
});
