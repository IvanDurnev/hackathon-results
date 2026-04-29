import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";
import { applyTheme, getInitialTheme } from "./app/theme";
import "./styles.css";

applyTheme(getInitialTheme());

createRoot(document.getElementById("root") as HTMLElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
