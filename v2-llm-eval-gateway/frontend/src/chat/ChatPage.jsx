import { useEffect, useRef, useState } from "react";
import { askQuestion, shortModel } from "../api.js";
import Message from "./Message.jsx";

const STARTER_QUESTIONS = [
  "How many days do I have to ask for a refund?",
  "How long does standard shipping take?",
  "When is customer support open?",
  "Can I get a refund for a downloaded e-book?",
];

// Chat page: question box at the bottom, conversation above, starter questions when empty.
// Example: <ChatPage /> -> full-screen chat that calls POST /ask
export default function ChatPage() {
  const [messages, setMessages] = useState([]); // [{role: "user"|"assistant"|"error", text, data?}]
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [lastModel, setLastModel] = useState("");
  const endRef = useRef(null);

  // Keep the newest message in view. The braces matter: an effect must not return a value.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  // Example: send("How long does shipping take?") -> adds the question, then the answer (or an error)
  async function send(question) {
    const text = question.trim();
    if (!text || busy) return;
    setMessages((old) => [...old, { role: "user", text }]);
    setDraft("");
    setBusy(true);
    try {
      const data = await askQuestion(text);
      setLastModel(data.model);
      setMessages((old) => [...old, { role: "assistant", text: data.answer, data }]);
    } catch (error) {
      setMessages((old) => [...old, { role: "error", text: error.message }]);
    } finally {
      setBusy(false);
    }
  }

  // Enter sends, Shift+Enter adds a new line.
  function onKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send(draft);
    }
  }

  return (
    <div className="chat-shell">
      <header className="chat-top">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">?</span>
          <span>Ask the Docs</span>
        </div>
        <div className="chat-top-right">
          {lastModel && <span className="model-pill">Answered by {shortModel(lastModel)}</span>}
          {messages.length > 0 && (
            <button className="ghost-button" onClick={() => setMessages([])}>New chat</button>
          )}
        </div>
      </header>

      <main className="chat-scroll">
        <div className="chat-column">
          {messages.length === 0 ? (
            <section className="chat-empty">
              <h1>Questions about orders, refunds and support</h1>
              <p>Answers come only from the Acme Store policy documents, with the page they came from. If the documents don't cover it, you'll be told.</p>
              <div className="starters">
                {STARTER_QUESTIONS.map((question) => (
                  <button key={question} className="starter" onClick={() => send(question)}>{question}</button>
                ))}
              </div>
            </section>
          ) : (
            messages.map((message, index) => <Message key={index} message={message} />)
          )}
          {busy && <div className="typing" aria-live="polite"><span /><span /><span /> Searching the documents</div>}
          <div ref={endRef} />
        </div>
      </main>

      <footer className="composer-wrap">
        <form className="composer" onSubmit={(event) => { event.preventDefault(); send(draft); }}>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask a question about refunds, shipping or support"
            rows={1}
            maxLength={1000}
            aria-label="Your question"
          />
          <button className="send-button" disabled={busy || !draft.trim()} aria-label="Send question">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 12h14M12 5l7 7-7 7" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </button>
        </form>
        <p className="composer-note">Enter to send, Shift+Enter for a new line</p>
      </footer>
    </div>
  );
}
