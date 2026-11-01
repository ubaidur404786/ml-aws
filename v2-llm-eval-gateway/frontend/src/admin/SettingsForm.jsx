import { useState } from "react";
import { adminApi, shortModel } from "../api.js";

// Choose which model answers customers, and the limits that protect the budget.
// Example: <SettingsForm password="secret" settings={{active_model: "...", ...}} candidates={[...]} recommended="..." onSaved={...} />
export default function SettingsForm({ password, settings, candidates, recommended, onSaved }) {
  const [form, setForm] = useState(settings);
  const [status, setStatus] = useState({ kind: "", text: "" });

  // Example: update("max_tokens", 400) -> form.max_tokens becomes 400
  function update(key, value) {
    setForm((old) => ({ ...old, [key]: value }));
  }

  // Example: toggleAllowed("amazon.nova-pro-v1:0") -> adds or removes it from allowed_models
  function toggleAllowed(model) {
    const allowed = form.allowed_models.includes(model)
      ? form.allowed_models.filter((m) => m !== model)
      : [...form.allowed_models, model];
    update("allowed_models", allowed);
  }

  async function save(event) {
    event.preventDefault();
    try {
      await adminApi(password, "PUT", "/admin/settings", {
        ...form,
        max_tokens: Number(form.max_tokens),
        daily_question_limit: Number(form.daily_question_limit),
      });
      setStatus({ kind: "good", text: `Saved. ${shortModel(form.active_model)} now answers customer questions.` });
      onSaved();
    } catch (error) {
      setStatus({ kind: "bad", text: error.message });
    }
  }

  return (
    <form className="panel" onSubmit={save}>
      <div className="panel-head">
        <h2>Model and limits</h2>
        {recommended && recommended !== form.active_model && (
          <button type="button" className="link-button" onClick={() => update("active_model", recommended)}>
            Use the recommended model ({shortModel(recommended)})
          </button>
        )}
      </div>
      <div className="field-row">
        <label className="field">
          Model that answers customers
          <select value={form.active_model} onChange={(e) => update("active_model", e.target.value)}>
            {form.allowed_models.map((model) => <option key={model} value={model}>{shortModel(model)}</option>)}
          </select>
        </label>
        <label className="field">
          Max tokens per answer
          <input type="number" min="50" max="2000" value={form.max_tokens} onChange={(e) => update("max_tokens", e.target.value)} />
        </label>
        <label className="field">
          Questions per day
          <input type="number" min="0" value={form.daily_question_limit} onChange={(e) => update("daily_question_limit", e.target.value)} />
        </label>
      </div>
      <fieldset className="choice-row">
        <legend>Models the admin may switch to</legend>
        {candidates.map((model) => (
          <label key={model} className="choice">
            <input type="checkbox" checked={form.allowed_models.includes(model)} onChange={() => toggleAllowed(model)} />
            {shortModel(model)}
          </label>
        ))}
      </fieldset>
      <div className="field-row">
        <button className="primary-button">Save changes</button>
        {status.text && <p className={`status ${status.kind}`} aria-live="polite">{status.text}</p>}
      </div>
    </form>
  );
}
