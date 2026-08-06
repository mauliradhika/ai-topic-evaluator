import { useNavigate } from "react-router-dom";
import { useSession } from "../SessionContext";

export default function Results() {
  const { result, setSession, setResult } = useSession();
  const navigate = useNavigate();

  if (!result) {
    navigate("/");
    return null;
  }

  const restart = () => {
    setSession(null);
    setResult(null);
    navigate("/");
  };

  return (
    <div className="page">
      <h1>Your Score</h1>
      <div className="score-circle">{Math.round(result.overall_score)}</div>

      <h3>Breakdown</h3>
      <ul className="criteria-list">
        {Object.entries(result.criteria).map(([name, c]) => (
          <li key={name}>
            <div className="criterion-row">
              <span>{name.replace(/_/g, " ")}</span>
              <span>{c.score}/10 (weight {(c.weight * 100).toFixed(0)}%)</span>
            </div>
            <p className="criterion-comment">{c.comment}</p>
          </li>
        ))}
      </ul>

      <h3>Feedback</h3>
      <p>{result.feedback}</p>

      <div className="two-col">
        <div>
          <h4>Strengths</h4>
          <ul>{result.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
        <div>
          <h4>Improve</h4>
          <ul>{result.improvements.map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
      </div>

      <button className="primary" onClick={restart}>Practice again</button>
    </div>
  );
}
