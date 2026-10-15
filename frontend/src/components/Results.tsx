import { useState } from "react";
import type { components } from "../types";
type Scholarship = components["schemas"]["Scholarship"];
type Match = components["schemas"]["MatchResult"];
export function Results({
  scholarships,
  matches,
  selected,
  onSelect,
}: {
  scholarships: Scholarship[];
  matches: Match[];
  selected: string[];
  onSelect: (id: string) => void;
}) {
  const [view, setView] = useState("matches");
  const visible = matches.filter((m) =>
    view === "upcoming"
      ? scholarships.some(
          (s) =>
            s.id === m.scholarship_id && s.deadline && m.timing !== "closed",
        )
      : m.group === view,
  );
  return (
    <section className="results">
      <div className="section-title">
        <div>
          <div className="eyebrow">FIND YOUR POSSIBILITIES</div>
          <h2>Your scholarship starting point</h2>
        </div>
        <span className="count">{scholarships.length} in this collection</span>
      </div>
      <nav className="tabs" aria-label="Scholarship views">
        {[
          ["matches", "Potential matches"],
          ["upcoming", "Upcoming deadlines"],
          ["prepare", "Prepare for senior year"],
          ["explore", "Explore more"],
        ].map(([id, label]) => (
          <button
            key={id}
            aria-pressed={view === id}
            onClick={() => setView(id)}
          >
            {label}
          </button>
        ))}
      </nav>
      {!visible.length ? (
        <div className="empty">
          <span className="spark">✦</span>
          <h3>A starting point, not the whole picture.</h3>
          <p>
            No opportunities are shown in this view yet. There may be
            scholarships outside this collection. Try another view or add more
            profile information.
          </p>
        </div>
      ) : (
        <div className="cards">
          {visible.map((match) => {
            const s = scholarships.find((s) => s.id === match.scholarship_id);
            if (!s) return null;
            return (
              <article className="card" key={s.id}>
                <span className="badge">
                  {match.evidence_label.replaceAll("_", " ")}
                </span>
                <h3>{s.name}</h3>
                <p>{match.fit}</p>
                {match.followups?.map((q) => (
                  <p className="question" key={q}>
                    {q}
                  </p>
                ))}
                <p className="timing">
                  {match.timing} · {s.deadline || "Deadline not established"}
                </p>
                <details>
                  <summary>Requirements, checklist & sources</summary>
                  {match.conditions.map((c, i) => (
                    <p key={i}>
                      {c.status}: {c.reason}
                    </p>
                  ))}
                  <ul>
                    {s.materials?.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  {s.evidence?.map((ref) => (
                    <blockquote key={ref.id}>
                      <p>{ref.quote}</p>
                      <a href={ref.url} target="_blank" rel="noreferrer">
                        {ref.title || "Official source"}
                      </a>
                      <small>
                        {" "}
                        · {ref.section_id}{" "}
                        {ref.page ? `· page ${ref.page}` : ""} · Retrieved{" "}
                        {ref.fetched_at.slice(0, 10)} · Cycle{" "}
                        {ref.cycle || s.cycle || "unknown"}
                      </small>
                    </blockquote>
                  ))}
                </details>
                <button
                  className="save"
                  aria-pressed={selected.includes(s.id)}
                  onClick={() => onSelect(s.id)}
                >
                  {selected.includes(s.id)
                    ? "✓ Saved to this visit"
                    : "+ Add to my plan"}
                </button>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
