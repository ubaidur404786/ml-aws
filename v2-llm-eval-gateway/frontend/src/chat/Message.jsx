import { shortModel } from "../api.js";

// One chat message. Assistant answers show their source pages and which model answered.
// Example: <Message message={{role: "assistant", text: "3 to 5 days.", data: {sources: ["shipping_guide.pdf p.1"], ...}}} />
export default function Message({ message }) {
  if (message.role === "user") {
    return <div className="msg msg-user">{message.text}</div>;
  }
  if (message.role === "error") {
    return <div className="msg msg-error" role="alert">{message.text}</div>;
  }

  const { sources, model, latency_ms: latency } = message.data;
  return (
    <div className="msg msg-assistant">
      <p className="msg-text">{message.text}</p>
      <div className="sources" aria-label="Sources">
        {sources.map((source) => (
          <span key={source} className="source-chip" title="Document and page this answer was built from">
            {source.replace(".pdf", "").replaceAll("_", " ")}
          </span>
        ))}
      </div>
      <p className="msg-meta">{shortModel(model)}, {latency} ms</p>
    </div>
  );
}
