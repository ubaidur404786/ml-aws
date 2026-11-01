import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During `npm run dev` (port 5173), API calls are forwarded to FastAPI on port 8000.
// "^/admin/.+" forwards the admin API (/admin/results, ...) but not the /admin page itself.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/ask": "http://localhost:8000",
      "/health": "http://localhost:8000",
      "^/admin/.+": "http://localhost:8000",
    },
  },
});
