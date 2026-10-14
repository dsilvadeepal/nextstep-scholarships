import { useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import { ProfileForm } from "./components/ProfileForm";
import type { StudentProfile } from "./components/ProfileForm";
import { Results } from "./components/Results";
import type { components } from "./types";
import { request } from "./api";
import "./styles.css";
import { ScenarioPanel } from "./components/ScenarioPanel";
import { PrintPlan } from "./components/PrintPlan";
import { applyScenario } from "./scenarios";
type Catalog = {
  corpus_version: string;
  scholarships: components["schemas"]["Scholarship"][];
  matches: components["schemas"]["MatchResult"][];
};
function App() {
  const [original, setOriginal] = useState<StudentProfile | null>(null);
  const requestSequence = useRef(0);
  const [catalog, setCatalog] = useState<
    (Catalog & { hypothetical: boolean }) | null
  >(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const hypothetical = catalog?.hypothetical ?? false;
  async function explore(
    profile: StudentProfile,
    isHypothetical = false,
    baseProfile = profile,
  ) {
    const sequence = ++requestSequence.current;
    setLoading(true);
    setError("");
    try {
      const next = await request<Catalog>("/api/matches", { profile });
      if (sequence !== requestSequence.current) return;
      setCatalog({ ...next, hypothetical: isHypothetical });
      setOriginal(baseProfile);
      setSelected((old) =>
        old.filter((id) => next.scholarships.some((s) => s.id === id)),
      );
    } catch {
      if (sequence !== requestSequence.current) return;
      setError(
        "The scholarship catalog is not available right now. Please try again later. Your information has not been saved.",
      );
    } finally {
      if (sequence === requestSequence.current) setLoading(false);
    }
  }
  return (
    <>
      <header>
        <div className="brand">
          ✦ next<span>step</span>
        </div>
        <span className="header-note">
          Scholarship possibilities for Georgia students
        </span>
      </header>
      <main>
        <ProfileForm
          onSubmit={(profile) => {
            void explore(profile);
          }}
        />
        {original && (
          <ScenarioPanel
            profile={original}
            onApply={(overrides) => {
              void explore(applyScenario(original, overrides), true, original);
            }}
            onReset={() => {
              void explore(original);
            }}
          />
        )}
        {hypothetical && (
          <p className="notice">
            Hypothetical results — your original profile is preserved.
          </p>
        )}
        {loading && <p role="status">Finding possibilities…</p>}
        {error && (
          <p role="alert" className="notice">
            {error}
          </p>
        )}
        <Results
          scholarships={catalog?.scholarships || []}
          matches={catalog?.matches || []}
          selected={selected}
          onSelect={(id) =>
            setSelected((old) =>
              old.includes(id) ? old.filter((x) => x !== id) : [...old, id],
            )
          }
        />
        <button
          className="print-button"
          disabled={!selected.length}
          onClick={() => window.print()}
        >
          Print my plan ({selected.length})
        </button>
        <PrintPlan
          scholarships={
            catalog?.scholarships.filter((s) => selected.includes(s.id)) || []
          }
          matches={catalog?.matches || []}
          hypothetical={hypothetical}
          generatedAt={new Date().toLocaleDateString("en-CA")}
        />
        <p className="hint">
          Potential fit is provisional. Always confirm current requirements with
          the official sponsor.
        </p>
      </main>
      <footer>Your next step starts with a question. No account needed.</footer>
    </>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
