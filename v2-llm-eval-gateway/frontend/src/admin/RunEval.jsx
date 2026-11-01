import { useState } from "react";
import { adminApi, shortModel } from "../api.js";

// Start a small evaluation from the browser (1-10 golden questions).
// Example: <RunEval password="secret" candidates={["amazon.nova-micro-v1:0", ...]} onDone={() => reload()} />
export default function RunEval({ password, candidates, onDone }) {
  const [models, setModels] = useState(candidates);
  const [sampleSize, setSampleSize] = useState(5);
  const [status, setStatus] = useState({ kind: "", text: "" });
  const [busy, setBusy] = useState(false);

  // Example: toggle("amazon.nova-pro-v1:0") -> adds it to or removes it from the selected models
  function toggle(model) {
    setModels((old) => (old.includes(model) ? old.filter((m) => m !== model) : [...old, model]));
  }

  async function run(event) {
    event.preventDefault();
    setBusy(true);
    setStatus({ kind: "", text: `Asking ${sampleSize} questions to ${models.length} models, then judging each answer` });
    try {
      const report = await adminApi(password, "POST", "/admin/eval", { models, sample_size: Number(sampleSize) });
      setStatus({ kind: "good", text: `Evaluation ${report.run_id} finished. The overview above now shows it.` });
      onDone();
    } catch (error) {
      setStatus({ kind: "bad", text: error.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="panel" onSubmit={run}>
      <div className="panel-head">
        <h2>Run evaluation</h2>
        <p className="panel-note">Each question costs one call per model plus one judge call</p>
      </div>
      <fieldset className="choice-row">
        <legend>Models to compare</legend>
        {candidates.map((model) => (
          <label key={model} className="choice">
            <input type="checkbox" checked={models.includes(model)} onChange={() => toggle(model)} />
            {shortModel(model)}
          </label>
        ))}
      </fieldset>
      <div className="field-row">
        <label className="field">
          Golden questions
          <input type="number" min="1" max="10" value={sampleSize} onChange={(e) => setSampleSize(e.target.value)} />
        </label>
        <button className="primary-button" disabled={busy || models.length === 0}>
          {busy ? "Running evaluation" : "Run evaluation"}
        </button>
      </div>
      {status.text && <p className={`status ${status.kind}`} aria-live="polite">{status.text}</p>}
    </form>
  );
}
