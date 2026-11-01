import { Fragment, useState } from "react";
import { shortModel } from "../api.js";

// Example: Score({value: 5}) -> a green "5"; Score({value: 2}) -> a red "2"
function Score({ value }) {
  return <span className={`score-badge ${value >= 4 ? "pass" : "fail"}`}>{value}</span>;
}

// Every judged answer. Click a row to open the full answer, sources and the judge's reason.
// Example: <QuestionTable answers={[{id: 1, model: "...", question: "...", correctness: 5, ...}, ...]} />
export default function QuestionTable({ answers }) {
  const [openKey, setOpenKey] = useState("");
  const [modelFilter, setModelFilter] = useState("all");
  const models = [...new Set(answers.map((a) => a.model))];
  const shown = answers.filter((a) => modelFilter === "all" || a.model === modelFilter);

  if (answers.length === 0) {
    return <div className="panel"><h2>Question results</h2><p className="empty-note">Results appear here after the first evaluation.</p></div>;
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Question results</h2>
        <select value={modelFilter} onChange={(e) => setModelFilter(e.target.value)} aria-label="Show results for">
          <option value="all">All models</option>
          {models.map((m) => <option key={m} value={m}>{shortModel(m)}</option>)}
        </select>
      </div>
      <div className="table-scroll">
        <table className="questions">
          <thead>
            <tr>
              <th>Question</th>
              <th>Model</th>
              <th>Kind</th>
              <th className="num">Correct</th>
              <th className="num">Faithful</th>
              <th className="num">Refusal</th>
              <th className="num">Source</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((a) => {
              const key = `${a.model}|${a.id}`;
              const open = openKey === key;
              return (
                <Fragment key={key}>
                  <tr className="clickable" onClick={() => setOpenKey(open ? "" : key)} aria-expanded={open}>
                    <td>{a.question}</td>
                    <td>{shortModel(a.model)}</td>
                    <td>{a.type}</td>
                    <td className="num"><Score value={a.correctness} /></td>
                    <td className="num"><Score value={a.faithfulness} /></td>
                    <td className="num"><Score value={a.refusal} /></td>
                    <td className="num">{a.right_source ? "Found" : "Missed"}</td>
                  </tr>
                  {open && (
                    <tr className="detail-row">
                      <td colSpan="7">
                        <dl className="detail">
                          <dt>Expected</dt><dd>{a.expected_answer}</dd>
                          <dt>Answer</dt><dd>{a.answer}</dd>
                          <dt>Sources</dt><dd>{a.sources.join(", ")} (expected {a.source || "none"})</dd>
                          <dt>Judge</dt><dd>{a.reason}</dd>
                          <dt>Cost</dt><dd>{a.latency_ms} ms, {a.input_tokens} in and {a.output_tokens} out tokens, ${a.cost_usd.toFixed(6)}</dd>
                        </dl>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
