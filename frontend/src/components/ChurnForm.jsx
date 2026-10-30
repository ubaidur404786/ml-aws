import { useState } from "react";

// Options for each dropdown. Values must match what the backend accepts.
const YES_NO = ["Yes", "No"];
const INTERNET_OPTION = ["Yes", "No", "No internet service"];

const SELECT_FIELDS = [
  { name: "gender", label: "Gender", options: ["Female", "Male"] },
  { name: "SeniorCitizen", label: "Senior citizen", options: ["0", "1"], labels: ["No", "Yes"] },
  { name: "Partner", label: "Has partner", options: YES_NO },
  { name: "Dependents", label: "Has dependents", options: YES_NO },
  { name: "PhoneService", label: "Phone service", options: YES_NO },
  { name: "MultipleLines", label: "Multiple lines", options: ["Yes", "No", "No phone service"] },
  { name: "InternetService", label: "Internet service", options: ["DSL", "Fiber optic", "No"] },
  { name: "OnlineSecurity", label: "Online security", options: INTERNET_OPTION },
  { name: "OnlineBackup", label: "Online backup", options: INTERNET_OPTION },
  { name: "DeviceProtection", label: "Device protection", options: INTERNET_OPTION },
  { name: "TechSupport", label: "Tech support", options: INTERNET_OPTION },
  { name: "StreamingTV", label: "Streaming TV", options: INTERNET_OPTION },
  { name: "StreamingMovies", label: "Streaming movies", options: INTERNET_OPTION },
  { name: "Contract", label: "Contract", options: ["Month-to-month", "One year", "Two year"] },
  { name: "PaperlessBilling", label: "Paperless billing", options: YES_NO },
  {
    name: "PaymentMethod",
    label: "Payment method",
    options: [
      "Electronic check",
      "Mailed check",
      "Bank transfer (automatic)",
      "Credit card (automatic)",
    ],
  },
];

const NUMBER_FIELDS = [
  { name: "tenure", label: "Tenure (months)", min: 0, max: 100, step: 1 },
  { name: "MonthlyCharges", label: "Monthly charges ($)", min: 0, max: 1000, step: 0.01 },
  { name: "TotalCharges", label: "Total charges ($)", min: 0, max: 100000, step: 0.01 },
];

// A loyal, low-risk customer as the starting point
const DEFAULT_CUSTOMER = {
  gender: "Male", SeniorCitizen: "0", Partner: "Yes", Dependents: "Yes",
  tenure: "48", PhoneService: "Yes", MultipleLines: "Yes", InternetService: "DSL",
  OnlineSecurity: "Yes", OnlineBackup: "Yes", DeviceProtection: "Yes", TechSupport: "Yes",
  StreamingTV: "No", StreamingMovies: "No", Contract: "Two year", PaperlessBilling: "No",
  PaymentMethod: "Bank transfer (automatic)", MonthlyCharges: "65.00", TotalCharges: "3120.00",
};

// A typical high-risk customer, loaded by the "example" button
const HIGH_RISK_CUSTOMER = {
  gender: "Female", SeniorCitizen: "0", Partner: "No", Dependents: "No",
  tenure: "2", PhoneService: "Yes", MultipleLines: "No", InternetService: "Fiber optic",
  OnlineSecurity: "No", OnlineBackup: "No", DeviceProtection: "No", TechSupport: "No",
  StreamingTV: "Yes", StreamingMovies: "Yes", Contract: "Month-to-month", PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check", MonthlyCharges: "95.50", TotalCharges: "190.00",
};

// Check number fields before sending; returns { fieldName: message }
function validate(values) {
  const errors = {};
  for (const field of NUMBER_FIELDS) {
    const raw = values[field.name];
    const number = Number(raw);
    if (raw === "" || Number.isNaN(number)) {
      errors[field.name] = "Required";
    } else if (number < field.min || number > field.max) {
      errors[field.name] = `Must be between ${field.min} and ${field.max}`;
    } else if (field.name === "tenure" && !Number.isInteger(number)) {
      errors[field.name] = "Must be a whole number";
    }
  }
  return errors;
}

export default function ChurnForm({ onSubmit, loading }) {
  const [values, setValues] = useState(DEFAULT_CUSTOMER);
  const [errors, setErrors] = useState({});

  function handleChange(event) {
    setValues({ ...values, [event.target.name]: event.target.value });
  }

  function handleSubmit(event) {
    event.preventDefault();
    const foundErrors = validate(values);
    setErrors(foundErrors);
    if (Object.keys(foundErrors).length > 0) return;

    // Convert form strings to the types the API expects
    onSubmit({
      ...values,
      SeniorCitizen: Number(values.SeniorCitizen),
      tenure: Number(values.tenure),
      MonthlyCharges: Number(values.MonthlyCharges),
      TotalCharges: Number(values.TotalCharges),
    });
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <div className="card-header">
        <h2>Customer details</h2>
        <div className="presets">
          <button type="button" className="link" onClick={() => setValues(HIGH_RISK_CUSTOMER)}>
            Load example customer
          </button>
          <button type="button" className="link" onClick={() => setValues(DEFAULT_CUSTOMER)}>
            Reset
          </button>
        </div>
      </div>

      <div className="grid">
        {NUMBER_FIELDS.map((field) => (
          <label key={field.name}>
            {field.label}
            <input
              type="number"
              name={field.name}
              value={values[field.name]}
              min={field.min}
              max={field.max}
              step={field.step}
              onChange={handleChange}
              className={errors[field.name] ? "invalid" : ""}
            />
            {errors[field.name] && <span className="field-error">{errors[field.name]}</span>}
          </label>
        ))}

        {SELECT_FIELDS.map((field) => (
          <label key={field.name}>
            {field.label}
            <select name={field.name} value={values[field.name]} onChange={handleChange}>
              {field.options.map((option, i) => (
                <option key={option} value={option}>
                  {field.labels ? field.labels[i] : option}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>

      <button type="submit" className="primary" disabled={loading}>
        {loading ? "Predicting..." : "Predict churn"}
      </button>
    </form>
  );
}
