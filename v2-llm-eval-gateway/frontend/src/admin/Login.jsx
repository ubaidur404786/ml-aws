import { useState } from "react";

// Sign-in form for the admin password.
// Example: <Login onSignIn={async (pass) => {...}} /> -> shows the error text if onSignIn throws
export default function Login({ onSignIn }) {
  const [pass, setPass] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await onSignIn(pass);
    } catch (err) {
      setError(err.message === "Wrong admin password" ? "That password is not correct. It is ADMIN_PASSWORD in the server's .env file." : err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">≡</span>
          <span>Model Control Room</span>
        </div>
        <h1>Sign in to compare models and set limits</h1>
        <label htmlFor="admin-password">Admin password</label>
        <input id="admin-password" type="password" value={pass} onChange={(e) => setPass(e.target.value)} autoFocus required />
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="primary-button" disabled={busy}>{busy ? "Signing in" : "Sign in"}</button>
      </form>
    </div>
  );
}
