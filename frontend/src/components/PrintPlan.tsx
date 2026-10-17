import type { components } from "../types";
export function PrintPlan({
  scholarships,
  matches,
  hypothetical,
  generatedAt,
}: {
  scholarships: components["schemas"]["Scholarship"][];
  matches: components["schemas"]["MatchResult"][];
  hypothetical: boolean;
  generatedAt: string;
}) {
  return (
    <section className="print-plan">
      <h1>My next steps</h1>
      <p>Generated {generatedAt} · NextStep Scholarships</p>
      {hypothetical && (
        <p>
          <strong>Hypothetical plan — conditional on your scenario.</strong>
        </p>
      )}
      {!scholarships.length && (
        <p>Select scholarships to create your action plan.</p>
      )}
      {scholarships.map((s) => {
        const match = matches.find((m) => m.scholarship_id === s.id);
        const sources = new Map<
          string,
          {
            url: string;
            fetchedAt: string;
            version: string;
            sections: Set<string>;
          }
        >();
        for (const ref of s.evidence || []) {
          const key = `${ref.url}:${ref.document_version}`;
          const source = sources.get(key) || {
            url: ref.url,
            fetchedAt: ref.fetched_at.slice(0, 10),
            version: ref.document_version,
            sections: new Set<string>(),
          };
          source.sections.add(
            ref.page ? `page ${ref.page} / ${ref.section_id}` : ref.section_id,
          );
          sources.set(key, source);
        }
        return (
          <article key={s.id}>
            <h2>{s.name}</h2>
            <p>
              {match?.fit} · {s.information_status.replaceAll("_", " ")}
            </p>
            <p>
              Deadline: {s.deadline || "Unknown"} · Cycle:{" "}
              {s.cycle || "Unknown"} · {match?.timing}
            </p>
            <h3>Confirm next</h3>
            <ul>
              {match?.followups?.map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ul>
            <h3>Preparation checklist</h3>
            <ul>
              {s.materials?.map((m) => (
                <li key={m}>☐ {m}</li>
              ))}
            </ul>
            <h3>Official sources</h3>
            {[...sources].map(([key, source]) => (
              <p key={key}>
                <a href={source.url}>{source.url}</a>
                <br />
                Sections: {[...source.sections].join(", ")} · Retrieved{" "}
                {source.fetchedAt} · Document {source.version.slice(0, 12)}
              </p>
            ))}
          </article>
        );
      })}
      <p>
        Potential fit is provisional. Confirm current requirements with the
        official sponsor. This collection is not comprehensive.
      </p>
    </section>
  );
}
