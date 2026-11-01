import { useState } from "react";
import { adminApi } from "../api.js";
import Login from "./Login.jsx";
import KpiStrip from "./KpiStrip.jsx";
import Leaderboard from "./Leaderboard.jsx";
import Charts from "./Charts.jsx";
import RunEval from "./RunEval.jsx";
import SettingsForm from "./SettingsForm.jsx";
import QuestionTable from "./QuestionTable.jsx";

const SECTIONS = [
  ["overview", "Overview"],
  ["evaluate", "Run evaluation"],
  ["settings", "Model and limits"],
  ["questions", "Question results"],
];

// Admin dashboard. The password lives only in memory and is sent as a header on every call.
// Example: <AdminPage /> -> sign-in form, then the dashboard
export default function AdminPage() {
  const [password, setPassword] = useState("");
  const [data, setData] = useState(null); // {results, settings, usage}

  // Example: loadAll("secret") -> fetches results, settings and usage in parallel
  async function loadAll(pass = password) {
    const [results, settings, usage] = await Promise.all([
      adminApi(pass, "GET", "/admin/results"),
      adminApi(pass, "GET", "/admin/settings"),
      adminApi(pass, "GET", "/admin/usage"),
    ]);
    setData({ results, settings, usage });
  }

  async function signIn(pass) {
    await loadAll(pass); // throws on a wrong password, Login shows the message
    setPassword(pass);
  }

  if (!data) return <Login onSignIn={signIn} />;

  const { results, settings, usage } = data;
  const report = results.report;

  return (
    <div className="admin-shell">
      <aside className="admin-side">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">≡</span>
          <span>Model Control Room</span>
        </div>
        <nav>
          {SECTIONS.map(([id, label]) => <a key={id} href={`#${id}`}>{label}</a>)}
        </nav>
        <div className="side-foot">
          {report && <p>Last run {report.run_id || "from the command line"}, {report.mode} mode</p>}
          <a href="/">Open the chat</a>
        </div>
      </aside>

      <main className="admin-main">
        <section id="overview">
          <h1>Which model should answer customers?</h1>
          <p className="lead">Every candidate answers the same golden questions with the same documents. A separate judge model scores them; the cheapest model that clears both quality bars is recommended.</p>
          <KpiStrip usage={usage} settings={settings} report={report} />
          {report ? (
            <>
              <Leaderboard report={report} activeModel={settings.active_model} />
              <Charts leaderboard={report.leaderboard} />
              <p className="agreement">
                {results.agreement
                  ? `The judge agreed with hand scoring on ${results.agreement.agreement_pct}% of ${results.agreement.scored} answers.`
                  : "Judge agreement not measured yet. Score 20 answers by hand with python -m eval.human_check."}
              </p>
            </>
          ) : (
            <p className="empty-note">No evaluation has run yet. Start one in Run evaluation below.</p>
          )}
        </section>

        <section id="evaluate">
          <RunEval password={password} candidates={results.candidates} onDone={() => loadAll()} />
        </section>

        <section id="settings">
          <SettingsForm
            password={password}
            settings={settings}
            candidates={results.candidates}
            recommended={report?.recommended}
            onSaved={() => loadAll()}
          />
        </section>

        <section id="questions">
          <QuestionTable answers={results.answers} />
        </section>
      </main>
    </div>
  );
}
