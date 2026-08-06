import { createContext, useContext, useState } from "react";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [session, setSession] = useState(null);
  // session shape once started:
  // { session_id, subtopic, references, prep_time_sec, response_time_sec, mode, strictness }

  const [result, setResult] = useState(null);
  // evaluation result once submitted

  return (
    <SessionContext.Provider value={{ session, setSession, result, setResult }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
