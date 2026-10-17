import { useState } from "react";
import type { components } from "../types";
import { categories, scholarshipGroup, matchesCollegeChoice } from "../scholarshipGroups";

type Scholarship = components["schemas"]["Scholarship"];
type Match = components["schemas"]["MatchResult"];

function formatDate(value: string) {
  return new Date(`${value}T12:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function timingLabel(match: Match, scholarship: Scholarship) {
  const deadline = scholarship.deadline
    ? `deadline ${formatDate(scholarship.deadline)}`
    : "deadline not confirmed";
  if (match.timing === "open") return `Open · ${deadline}`;
  if (match.timing === "closed") return `Closed · ${deadline}`;
  if (match.timing === "upcoming") {
    return scholarship.opens
      ? `Opens ${formatDate(scholarship.opens)} · ${deadline}`
      : `Upcoming · ${deadline}`;
  }
  return scholarship.deadline
    ? `Deadline ${formatDate(scholarship.deadline)} · opening status not confirmed`
    : "Application timing not confirmed";
}

function usefulFollowup(followups: string[] = []) {
  return followups.find(
    (item) =>
      !item
        .toLowerCase()
        .includes("confirm the full sponsor eligibility and exclusions"),
  );
}

export function Results({
  scholarships,
  matches,
  selected,
  onSelect,
  onAsk,
  collegeChoices = [],
}: {
  collegeChoices?: string[];
  scholarships: Scholarship[];
  matches: Match[];
  selected: string[];
  onSelect: (id: string) => void;
  onAsk: (scholarship: Scholarship) => void;
}) {
  const [view, setView] = useState("matches");
  const [category, setCategory] = useState("all");
  const [location, setLocation] = useState("all");
  const [useColleges, setUseColleges] = useState(true);
  const visible = matches
    .filter(m => {
      const s = scholarships.find(s => s.id === m.scholarship_id);
      if (!s || m.fit === "Not currently eligible") return false;
      const info = scholarshipGroup(s);
      return (category === "all" || info.category === category)
        && (location === "all" || (info.college && (location === "GA" ? info.college[1] === "GA" : info.college[1] !== "GA")))
        && (!useColleges || matchesCollegeChoice(s, collegeChoices));
    })
    .filter((m) =>
      view === "upcoming"
        ? m.group !== "unmet" && scholarships.some(
          (s) =>
            s.id === m.scholarship_id && s.deadline && m.timing !== "closed",
        )
        : m.group !== "unmet",
    )
    .sort((a, b) => {
      if (view !== "upcoming") return 0;
      const aDate = scholarships.find((s) => s.id === a.scholarship_id)?.deadline;
      const bDate = scholarships.find((s) => s.id === b.scholarship_id)?.deadline;
      return (aDate || "9999-12-31").localeCompare(bDate || "9999-12-31");
    });
  const primary = visible.filter(m => m.fit !== "Explore");
  const explore = visible.filter(m => m.fit === "Explore");
  function renderGroups(items: Match[]) {
    return categories.map(group => {
      const members = items.filter(m => {
        const s = scholarships.find(s => s.id === m.scholarship_id);
        return s && scholarshipGroup(s).category === group;
      });
      if (!members.length) return null;
      return <details className="scholarship-group" key={group} open>
        <summary>{group} ({members.length})</summary>
        {renderCards(members)}
      </details>;
    });
  }
  function renderCards(items: Match[]) {
    return (        <div className="cards">
          {items.map((match) => {
            const s = scholarships.find((item) => item.id === match.scholarship_id);
            if (!s) return null;
            const caveat = usefulFollowup(match.followups);
            return (
              <article className="card" key={s.id}>
                {match.evidence_label !== "source_checked" && <span className="badge">
                  {match.evidence_label === "conflicting" ? "Source details differ" : "Source verification needed"}
                </span>}
                <h3>{s.name}</h3>
                <p className={`match-label match-${match.fit.toLowerCase().replaceAll(" ", "-")}`}>
                  {match.fit}
                </p>
                {match.fit_reason && (
                  <p className="match-reason">{match.fit_reason}</p>
                )}
                {caveat && <p className="question">{caveat}</p>}
                <p className="timing">{timingLabel(match, s)}</p>
                <div className="card-actions">
                  <button className="ask-card" onClick={() => onAsk(s)}>
                    Ask about this
                  </button>
                  <button
                    className="save"
                    aria-pressed={selected.includes(s.id)}
                    onClick={() => onSelect(s.id)}
                  >
                    {selected.includes(s.id)
                      ? "✓ Saved to this visit"
                      : "+ Add to my plan"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>);
  }
  return (
    <section className="results">
      <div className="section-title">
        <div>
          <div className="eyebrow">FIND YOUR POSSIBILITIES</div>
          <h2>Your scholarship starting point</h2>
        </div>
        <span className="count">{primary.length} matches · {explore.length} to explore</span>
      </div>
      <nav className="tabs" aria-label="Scholarship views">
        {[
          ["matches", "Potential matches"],
          ["upcoming", "Upcoming deadlines"],
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
      <div className="result-filters">
        <label>Scholarship type<select value={category} onChange={e => setCategory(e.target.value)}>
          <option value="all">All types</option>{categories.map(c => <option key={c}>{c}</option>)}
        </select></label>
        <label>College location<select value={location} onChange={e => setLocation(e.target.value)}>
          <option value="all">All locations and portable awards</option><option value="GA">Georgia colleges</option><option value="outside">Out-of-state colleges</option>
        </select></label>
      </div>
      {collegeChoices.length > 0 && <label className="college-filter"><input type="checkbox" checked={useColleges} onChange={e => setUseColleges(e.target.checked)} /> Limit college awards to my choices: {collegeChoices.join(', ')}. Company and foundation awards stay included unless another filter excludes them.</label>}
      <p className="hint">Counts reflect your current filters. College preferences indicate relevance, not admission or eligibility.</p>
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
        <>
          {renderGroups(primary)}
          {!primary.length && <p>No strong or possible matches with these filters. Expand Explore for opportunities that need more information.</p>}
          {explore.length > 0 && <details className="explore-results" key={`${view}-${category}-${location}-${useColleges}-${collegeChoices.join(',')}`}>
            <summary>Explore other opportunities ({explore.length})</summary>
            <p>These need more information or may be relevant for a future year.</p>
            {renderGroups(explore)}
          </details>}
        </>
      )}
    </section>
  );
}
