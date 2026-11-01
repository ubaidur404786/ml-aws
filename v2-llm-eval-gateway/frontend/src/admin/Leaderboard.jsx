import { shortModel } from "../api.js";

const CORRECTNESS_BAR = 85;
const REFUSAL_BAR = 90;

// A score bar with a tick at the pass line, so you see at a glance how far a model is from passing.
// Example: <ScoreBar value={72} passAt={85} /> -> bar filled to 72%, tick at 85%, shown as "below the bar"
function ScoreBar({ value, passAt }) {
  const passed = value >= passAt;
  return (
    <div className="score">
      <div className="score-track" role="img" aria-label={`${value}%, pass line ${passAt}%`}>
        <div className={`score-fill ${passed ? "pass" : "fail"}`} style={{ width: `${value}%` }} />
        <div className="score-tick" style={{ left: `${passAt}%` }} />
      </div>
      <span className={`score-value ${passed ? "pass" : "fail"}`}>{value}%</span>
    </div>
  );
}

// Leaderboard: one row per model. The recommended model is marked; so is the one answering now.
// Example: <Leaderboard report={{leaderboard: [...], recommended: "amazon.nova-micro-v1:0"}} activeModel="amazon.nova-lite-v1:0" />
export default function Leaderboard({ report, activeModel }) {
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Leaderboard</h2>
        <p className="panel-note">Pass lines: correctness {CORRECTNESS_BAR}%, refusal {REFUSAL_BAR}%</p>
      </div>
      <div className="table-scroll">
        <table className="board">
          <thead>
            <tr>
              <th>Model</th>
              <th>Correctness</th>
              <th>Refusal</th>
              <th className="num">Faithfulness</th>
              <th className="num">Right source</th>
              <th className="num">p50 / p95 ms</th>
              <th className="num">$ per 1,000</th>
            </tr>
          </thead>
          <tbody>
            {report.leaderboard.map((row) => (
              <tr key={row.model} className={row.model === report.recommended ? "is-recommended" : ""}>
                <td>
                  <span className="model-name">{shortModel(row.model)}</span>
                  {row.model === report.recommended && <span className="tag tag-good">Recommended</span>}
                  {row.model === activeModel && <span className="tag">Answering now</span>}
                </td>
                <td><ScoreBar value={row.correctness_pct} passAt={CORRECTNESS_BAR} /></td>
                <td><ScoreBar value={row.refusal_pct} passAt={REFUSAL_BAR} /></td>
                <td className="num">{row.faithfulness_avg} / 5</td>
                <td className="num">{row.right_source_pct}%</td>
                <td className="num">{row.p50_latency_ms} / {row.p95_latency_ms}</td>
                <td className="num">${row.cost_per_1000_usd}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
