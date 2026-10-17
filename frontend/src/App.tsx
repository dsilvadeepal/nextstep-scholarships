import { useState, useRef } from "react";
import { ProfileForm } from "./components/ProfileForm";
import type { StudentProfile } from "./components/ProfileForm";
import { Results } from "./components/Results";
import type { components } from "./types";
import { request } from "./api";
import "./styles.css";
import { PrintPlan } from "./components/PrintPlan";
import { ChatPanel } from "./components/ChatPanel";
import { EvalDashboard } from "./admin/EvalDashboard";
import { BrandMark } from "./components/BrandAssets";
type Catalog = components["schemas"]["CatalogResponse"];
type Scholarship = components["schemas"]["Scholarship"];
export default function App() {
  const requestSequence = useRef(0);
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [activeProfile, setActiveProfile] = useState<StudentProfile | null>(
    null,
  );
  const [sourceChange, setSourceChange] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [chatRequest, setChatRequest] = useState<
    (Pick<Scholarship, "id" | "name"> & { nonce: number }) | null
  >(null);
  async function explore(profile: StudentProfile) {
    const sequence = ++requestSequence.current;
    setLoading(true);
    setError("");
    try {
      const next = await request<Catalog>("/api/matches", { profile });
      if (sequence !== requestSequence.current) return;
      if (catalog && catalog.corpus_version !== next.corpus_version) {
        const removed = selected.filter(
          (id) => !next.scholarships.some((s) => s.id === id),
        );
        setSourceChange(
          `Sources changed from ${catalog.corpus_version} to ${next.corpus_version}. Saved records were refreshed; ${removed.length} removed from this collection. Recheck requirements before printing.`,
        );
      }
      setCatalog(next);
      setActiveProfile(profile);
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
  if (new URLSearchParams(location.search).get("admin") === "1")
    return <EvalDashboard />;
  return (
    <>
      <header>
        <div className="brand">
          <BrandMark />
          <span className="brand-name">next<span>step</span></span>
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
        {loading && <p role="status">Finding possibilities…</p>}
        {error && (
          <p role="alert" className="notice">
            {error}
          </p>
        )}
        {catalog?.coverage && (
          <p className="coverage hint">
            {catalog.coverage.program_count} programs · {catalog.coverage.note}
          </p>
        )}
        {sourceChange && <p className="notice">{sourceChange}</p>}
        {catalog && activeProfile && (
          <ChatPanel
            profile={activeProfile}
            programIds={selected}
            corpusVersion={catalog.corpus_version}
            promptRequest={chatRequest}
          />
        )}
        <Results
          collegeChoices={activeProfile?.prospective_colleges || []}
          scholarships={catalog?.scholarships || []}
          matches={catalog?.matches || []}
          selected={selected}
          onSelect={(id) =>
            setSelected((old) =>
              old.includes(id) ? old.filter((x) => x !== id) : [...old, id],
            )
          }
          onAsk={(scholarship) =>
            setChatRequest({
              id: scholarship.id,
              name: scholarship.name,
              nonce: Date.now(),
            })
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
          hypothetical={false}
          generatedAt={new Date().toLocaleDateString("en-CA", {
            timeZone: "America/New_York",
          })}
        />
        <p className="hint">
          Potential fit is provisional. Always confirm current requirements with
          the official sponsor.
        </p>
      </main>
      <footer>
        Your next step starts with a question. No account needed.{" "}
        <a href="/?admin=1">Admin</a>
      </footer>
    </>
  );
}
