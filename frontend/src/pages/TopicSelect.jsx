import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTopics, startSession } from "../api";
import { useSession } from "../SessionContext";

export default function TopicSelect() {
  const [topics, setTopics] = useState([]);
  const [topicId, setTopicId] = useState("");
  const [mode, setMode] = useState("write");
  const [strictness, setStrictness] = useState("moderate");
  const [prepMin, setPrepMin] = useState(5);
  const [responseMin, setResponseMin] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { setSession } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    getTopics().then((data) => {
      setTopics(data);
      if (data.length) setTopicId(data[0].id);
    });
  }, []);

  const responseMax = mode === "speak" ? 10 : 10; // both 1-10, kept explicit for clarity
  const responseMin_ = 1;

  const handleStart = async () => {
    if (!topicId) return;
    setLoading(true);
    setError("");
    try {
      const data = await startSession({
        topic_id: topicId,
        mode,
        strictness,
        prep_time_sec: prepMin * 60,
        response_time_sec: responseMin * 60,
      });
      setSession(data);
      navigate("/prep");
    } catch (e) {
      setError("Could not start session. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>PrepSpeak</h1>
      <p className="subtitle">Pick a topic, configure your practice, and go.</p>

      <label>Topic</label>
      <select value={topicId} onChange={(e) => setTopicId(e.target.value)}>
        {topics.map((t) => (
          <option key={t.id} value={t.id}>{t.name}</option>
        ))}
      </select>

      <label>Mode</label>
      <div className="toggle-row">
        <button className={mode === "write" ? "active" : ""} onClick={() => setMode("write")}>Write</button>
        <button className={mode === "speak" ? "active" : ""} onClick={() => setMode("speak")}>Speak</button>
      </div>

      <label>Evaluation strictness</label>
      <div className="toggle-row">
        {["lenient", "moderate", "strict"].map((s) => (
          <button key={s} className={strictness === s ? "active" : ""} onClick={() => setStrictness(s)}>
            {s}
          </button>
        ))}
      </div>

      <label>Prep time: {prepMin} min</label>
      <input type="range" min={2} max={15} value={prepMin} onChange={(e) => setPrepMin(+e.target.value)} />

      <label>Response time: {responseMin} min</label>
      <input type="range" min={responseMin_} max={responseMax} value={responseMin} onChange={(e) => setResponseMin(+e.target.value)} />

      {error && <p className="error">{error}</p>}

      <button className="primary" disabled={loading || !topicId} onClick={handleStart}>
        {loading ? "Drawing subtopic..." : "Start"}
      </button>
    </div>
  );
}
