import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import Landing from "./components/Landing";
import "./styles.css";
import "./aviation.css";
import "./executive.css";
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {window.location.pathname === "/" ? <Landing /> : <App />}
  </React.StrictMode>,
);
