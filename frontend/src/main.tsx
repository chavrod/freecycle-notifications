import { StrictMode } from "react";

import { createRoot } from "react-dom/client";
import * as Sentry from "@sentry/react";

import App from "./App.tsx";

Sentry.init({
  dsn:
    import.meta.env.VITE_ENV !== "DEV"
      ? import.meta.env.VITE_SENTRY_DSN
      : undefined,
  normalizeDepth: 5,
});

// createRoot(document.getElementById("root")!).render(
//   <StrictMode>
//     <App />
//   </StrictMode>
// );

createRoot(document.getElementById("root")!).render(<App />);
