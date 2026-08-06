import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../SessionContext";

function formatTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function Prep() {
  const { session } = useSession();
  const navigate = useNavigate();
  const [remaining, setRemaining] = useState(session?.prep_time_sec ?? 0);

  useEffect(() => {
    if (!session) {
      navigate("/");
      return;
    }
  }, [session, navigate]);

  useEffect(() => {
    if (remaining <= 0) {
      navigate("/respond");
      return;
    }
    const t = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(t);
  }, [remaining, navigate]);

  if (!session) return null;

  return (
    <div className="page">
      <div className="timer-badge">{formatTime(remaining)}</div>
      <h2>{session.subtopic.name}</h2>
      <p>{session.subtopic.description}</p>

      <h3>Reference material</h3>
      <ul className="ref-list">
        {session.references.map((r, i) => (
          <li key={i}>
            {r.citation_text}
            {r.url && (
              <>
                {" "}
                <a href={r.url} target="_blank" rel="noreferrer">[source]</a>
              </>
            )}
          </li>
        ))}
      </ul>

      <button className="primary" onClick={() => navigate("/respond")}>
        Skip prep, start now
      </button>
    </div>
  );
}
