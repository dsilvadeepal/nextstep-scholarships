import type { components } from "../types";
export type CaseRow = {
  case_id: string;
  method: string;
  status: string;
  result?: {
    answer?: components["schemas"]["AnswerResult"];
    scores?: Record<string, unknown>;
    expected?: components["schemas"]["EvalCase"];
    actual_conditions?: Record<string, string>;
    error?: string;
    trace_status?: string;
    trace_id?: string;
  };
  attempts?: unknown[];
};
export function CaseInspector({ row }: { row: CaseRow }) {
  const result = row.result;
  return (
    <details className="card">
      <summary>
        {row.case_id} · {row.method} · {row.status}
      </summary>
      {result?.error && <p role="alert">Case failed: {result.error}</p>}
      <h3>Expected claims and evidence</h3>
      <ul>
        {result?.expected?.expected_claims?.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
      <p>
        {result?.expected?.expected_evidence?.join(", ") ||
          "No required evidence IDs"}
      </p>
      <h3>Actual answer and retrieved passages</h3>
      {result?.answer?.blocks.map((b, i) => (
        <blockquote key={i}>
          {b.text}
          <small> {b.evidence_ids?.join(", ")}</small>
        </blockquote>
      ))}
      {result?.answer?.gaps?.map((g) => (
        <p key={g}>{g}</p>
      ))}
      {result?.answer?.evidence.chunks.map((c) => (
        <details key={c.id}>
          <summary>
            {c.heading} · {c.id}
          </summary>
          <p>{c.text}</p>
          {c.evidence?.map((e) => (
            <p key={e.id}>
              <a href={e.url}>{e.title || e.source_id}</a> · {e.section_id}{" "}
              {e.quote}
            </p>
          ))}
        </details>
      ))}
      <h3>Scores, denominators and rubric reasons</h3>
      <pre>
        {JSON.stringify(
          result?.scores || {
            note: "No scores; incomplete/error counts as failure",
          },
          null,
          2,
        )}
      </pre>
      <h3>Actual conditions</h3>
      <pre>{JSON.stringify(result?.actual_conditions || {}, null, 2)}</pre>
      <h3>Timing and usage</h3>
      <pre>
        {JSON.stringify(
          { timing: result?.answer?.timings, usage: result?.answer?.usage },
          null,
          2,
        )}
      </pre>
      <p>
        Trace: {result?.trace_status || "not uploaded"} {result?.trace_id || ""}
      </p>
      {Boolean(row.attempts?.length) && (
        <p>{row.attempts?.length} prior attempts retained with this case.</p>
      )}
    </details>
  );
}
