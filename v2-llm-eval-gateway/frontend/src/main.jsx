import React from "react";
import { createRoot } from "react-dom/client";
import ChatPage from "./chat/ChatPage.jsx";
import AdminPage from "./admin/AdminPage.jsx";
import "./styles.css";

// Two pages, no router needed: /admin shows the dashboard, everything else shows the chat.
const isAdmin = window.location.pathname.startsWith("/admin");
document.title = isAdmin ? "Model Control Room" : "Ask the Docs";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>{isAdmin ? <AdminPage /> : <ChatPage />}</React.StrictMode>,
);
