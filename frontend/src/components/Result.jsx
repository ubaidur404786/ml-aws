export default function Result({ result, error, loading }) {
  if (loading) {
    return <section className="card result muted">Running the model...</section>;
  }

  if (error) {
    return (
      <section className="card result">
        <h2>Something went wrong</h2>
        <p className="error">{error}</p>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="card result muted">
        Fill in the form and click <strong>Predict churn</strong> to see the result.
      </section>
    );
  }

  const percent = Math.round(result.churn_probability * 100);
  const riskClass = result.churn ? "high" : "low";

  return (
    <section className="card result">
      <h2>Prediction</h2>
      <p className={`label ${riskClass}`}>{result.label}</p>

      <p className="probability">
        Churn probability: <strong>{percent}%</strong>
      </p>
      <div className="bar" aria-label={`Churn probability ${percent}%`}>
        <div className={`bar-fill ${riskClass}`} style={{ width: `${percent}%` }} />
      </div>

      <p className="hint">
        Customers with a probability of 50% or more are flagged as likely to churn.
      </p>
    </section>
  );
}
