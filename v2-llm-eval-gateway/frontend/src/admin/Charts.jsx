import { shortModel } from "../api.js";

const WIDTH = 420;
const HEIGHT = 240;
const PAD = { left: 44, right: 16, top: 16, bottom: 36 };

// Quality vs cost: each model is a dot. Top-left (cheap and correct) is where you want to be.
// Example: <QualityChart leaderboard={[{model: "...", cost_per_1000_usd: 0.07, correctness_pct: 90}, ...]} />
function QualityChart({ leaderboard }) {
  const maxCost = Math.max(...leaderboard.map((row) => row.cost_per_1000_usd), 0.0001) * 1.15;
  const x = (cost) => PAD.left + (cost / maxCost) * (WIDTH - PAD.left - PAD.right);
  const y = (pct) => HEIGHT - PAD.bottom - (pct / 100) * (HEIGHT - PAD.top - PAD.bottom);
  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="chart" role="img" aria-label="Correctness against cost per model">
      <rect x={PAD.left} y={y(100)} width={WIDTH - PAD.left - PAD.right} height={y(85) - y(100)} className="chart-pass-zone" />
      <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(85)} y2={y(85)} className="chart-pass-line" />
      <text x={WIDTH - PAD.right} y={y(85) - 6} textAnchor="end" className="chart-label">85% pass line</text>
      {[0, 50, 100].map((pct) => (
        <text key={pct} x={PAD.left - 8} y={y(pct) + 4} textAnchor="end" className="chart-axis">{pct}%</text>
      ))}
      <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(0)} y2={y(0)} className="chart-axis-line" />
      <text x={(WIDTH + PAD.left) / 2} y={HEIGHT - 8} textAnchor="middle" className="chart-axis">Cost per 1,000 questions</text>
      {leaderboard.map((row, i) => {
        const dotX = x(row.cost_per_1000_usd);
        const onRight = dotX > WIDTH / 2; // labels on the right half go to the left of the dot, so they never clip
        return (
          <g key={row.model}>
            <circle cx={dotX} cy={y(row.correctness_pct)} r="6" className="chart-dot" />
            {/* labels step down 14px per model so dots at the same spot stay readable */}
            <text
              x={onRight ? dotX - 10 : dotX + 10}
              y={y(row.correctness_pct) + 20 + i * 14}
              textAnchor={onRight ? "end" : "start"}
              className="chart-label"
            >
              {shortModel(row.model)}, ${row.cost_per_1000_usd}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// Latency: p50 (typical) and p95 (slow tail) per model, as horizontal bars.
// Example: <LatencyChart leaderboard={[{model: "...", p50_latency_ms: 600, p95_latency_ms: 900}, ...]} />
function LatencyChart({ leaderboard }) {
  const maxMs = Math.max(...leaderboard.map((row) => row.p95_latency_ms), 1);
  const barWidth = (ms) => (ms / maxMs) * (WIDTH - 150);
  const rowHeight = (HEIGHT - 20) / Math.max(leaderboard.length, 1);
  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="chart" role="img" aria-label="Latency per model">
      {leaderboard.map((row, i) => {
        const top = 10 + i * rowHeight;
        return (
          <g key={row.model}>
            <text x="0" y={top + 18} className="chart-label">{shortModel(row.model)}</text>
            <rect x="100" y={top + 6} width={barWidth(row.p95_latency_ms)} height="16" rx="3" className="chart-bar-tail" />
            <rect x="100" y={top + 6} width={barWidth(row.p50_latency_ms)} height="16" rx="3" className="chart-bar" />
            <text x={104 + barWidth(row.p95_latency_ms)} y={top + 18} className="chart-axis">
              {row.p50_latency_ms} / {row.p95_latency_ms} ms
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// Example: <Charts leaderboard={report.leaderboard} /> -> the two charts side by side
export default function Charts({ leaderboard }) {
  return (
    <div className="chart-grid">
      <div className="panel">
        <div className="panel-head"><h2>Quality against cost</h2></div>
        <QualityChart leaderboard={leaderboard} />
      </div>
      <div className="panel">
        <div className="panel-head">
          <h2>Response time</h2>
          <p className="panel-note"><span className="key key-p50" /> typical (p50) <span className="key key-p95" /> slowest 5% (p95)</p>
        </div>
        <LatencyChart leaderboard={leaderboard} />
      </div>
    </div>
  );
}
