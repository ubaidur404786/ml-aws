import { useState } from "react";
import ChurnForm from "./components/ChurnForm.jsx";
import Result from "./components/Result.jsx";
import { predictChurn } from "./api.js";

export default function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handlePredict(customer) {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await predictChurn(customer));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header>
        <h1>Customer Churn Prediction</h1>
        <p>Enter a telecom customer's details to estimate how likely they are to leave.</p>
      </header>

      <main className="layout">
        <ChurnForm onSubmit={handlePredict} loading={loading} />
        <Result result={result} error={error} loading={loading} />
      </main>

      <footer>
        Model trained on the IBM Telco Customer Churn dataset (Apache 2.0).
      </footer>
    </div>
  );
}
