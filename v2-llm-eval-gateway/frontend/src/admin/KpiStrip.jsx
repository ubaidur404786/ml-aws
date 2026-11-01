import { shortModel } from "../api.js";

// Example: money(0.000213) -> "$0.000213";  money(1.5) -> "$1.50"
function money(value) {
  return value < 0.01 ? `$${value.toFixed(6)}` : `$${value.toFixed(2)}`;
}

// The five numbers an admin checks first.
// Example: <KpiStrip usage={{today: {questions: 3, cost_usd: 0.0002}, total_cost_usd: 0.001}} settings={...} report={...} />
export default function KpiStrip({ usage, settings, report }) {
  const limitUsed = settings.daily_question_limit
    ? Math.round((100 * usage.today.questions) / settings.daily_question_limit)
    : 100;
  const items = [
    ["Answering now", shortModel(settings.active_model), `max ${settings.max_tokens} tokens per answer`],
    ["Recommended", report?.recommended ? shortModel(report.recommended) : "None yet", report?.recommended ? "passes both quality bars" : "no model passes both bars"],
    ["Questions today", usage.today.questions, `${limitUsed}% of the ${settings.daily_question_limit} daily limit`],
    ["Cost today", money(usage.today.cost_usd), "client questions only"],
    ["Cost to date", money(usage.total_cost_usd), "since the first question"],
  ];
  return (
    <div className="kpis">
      {items.map(([label, value, note]) => (
        <div key={label} className="kpi">
          <p className="kpi-label">{label}</p>
          <p className="kpi-value">{value}</p>
          <p className="kpi-note">{note}</p>
        </div>
      ))}
    </div>
  );
}
