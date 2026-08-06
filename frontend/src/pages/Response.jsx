import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../SessionContext";
import { submitResponse } from "../api";

function formatTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function Response() {
  const { session, setResult } = useSession();
  const navigate = useNavigate();

  const total = session?.response_time_sec ?? 0;
  const [remaining, setRemaining] = useState(total);
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const recognitionRef = useRef(null);
  const startedAt = useRef(Date.now());

  useEffect(() => {
    if (!session) {
      navigate("/");
      return;
    }
  }, [session, navigate]);

  // Countdown
  useEffect(() => {
    if (remaining <= 0) {
      handleSubmit();
      return;
    }
    const t = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remaining]);

  // Speech recognition setup (Web Speech API - browser native, free)
  useEffect(() => {
    if (session?.mode !== "speak") return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setText("(Speech recognition not supported in this browser — try Chrome, or switch to write mode.)");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    let finalTranscript = "";

    recognition.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + " ";
        } else {
          interim += transcript;
        }
      }
      setText(finalTranscript + interim);
    };

    recognition.onerror = (e) => console.error("Speech recognition error:", e.error);
    recognition.onend = () => {
      // auto-restart if still within time and user hasn't submitted
      if (recognitionRef.current) {
        try { recognition.start(); } catch { /* ignore */ }
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);

    return () => {
      recognitionRef.current = null;
      recognition.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.mode]);

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);

    if (recognitionRef.current) {
      recognitionRef.current = null; // prevent auto-restart
    }

    const timeUsed = Math.round((Date.now() - startedAt.current) / 1000);

    try {
      const data = await submitResponse(session.session_id, {
        user_input: text.trim(),
        time_used_sec: Math.min(timeUsed, total),
      });
      setResult(data);
      navigate("/results");
    } catch (e) {
      console.error(e);
      alert("Evaluation failed. Check the backend/API key and try again.");
      setSubmitting(false);
    }
  };

  if (!session) return null;

  return (
    <div className="page">
      <div className="timer-badge">{formatTime(remaining)}</div>
      <h2>{session.subtopic.name}</h2>

      {session.mode === "write" ? (
        <textarea
          rows={14}
          placeholder="Start writing..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          autoFocus
        />
      ) : (
        <div className="speak-box">
          <p className="listening-indicator">{listening ? "🎙️ Listening..." : "Not listening"}</p>
          <div className="transcript">{text || "(start speaking, your words will appear here)"}</div>
        </div>
      )}

      <button className="primary" onClick={handleSubmit} disabled={submitting || !text.trim()}>
        {submitting ? "Evaluating..." : "Submit now"}
      </button>
    </div>
  );
}
