import { useState, useRef, useEffect } from "react";
import type { components } from "../types";
import { request } from "../api";
type Answer = components["schemas"]["AnswerResult"];
type Turn = components["schemas"]["ChatTurn"];
export function ChatPanel({
  profile,
  programIds,
  corpusVersion,
  hypothetical,
}: {
  profile: components["schemas"]["StudentProfile"];
  programIds: string[];
  corpusVersion: string;
  hypothetical: boolean;
}) {
  const dialog = useRef<HTMLDialogElement>(null),
    trigger = useRef<HTMLButtonElement>(null);
  const sequence = useRef(0);
  const [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState<Answer | null>(null),
    [history, setHistory] = useState<Turn[]>([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    sequence.current++;
    setAnswer(null);
    setHistory([]);
    setError("");
    setBusy(false);
  }, [profile, corpusVersion, programIds.join(",")]);
  function close() {
    dialog.current?.close();
    trigger.current?.focus();
  }
  async function ask() {
    const id = ++sequence.current;
    setBusy(true);
    setError("");
    try {
      const next = await request<Answer>("/api/chat", {
        profile,
        request: {
          question,
          program_ids: programIds.slice(0, 4),
          corpus_version: corpusVersion,
          method: "semantic",
        },
        history,
      });
      if (id !== sequence.current) return;
      setAnswer(next);
      const text = [...next.blocks.map((b) => b.text), ...(next.gaps || [])]
        .join("\n")
        .slice(0, 2000);
      setHistory(
        [
          ...history,
          { role: "user" as const, content: question.slice(0, 2000) },
          { role: "assistant" as const, content: text },
        ].slice(-4),
      );
    } catch {
      if (id === sequence.current)
        setError(
          "The answer service is unavailable or could not verify an answer. You can still browse your scholarship cards. No automatic retry was made.",
        );
    } finally {
      if (id === sequence.current) setBusy(false);
    }
  }
  return (
    <div className="chat">
      <button
        ref={trigger}
        className="primary"
        onClick={() => dialog.current?.showModal()}
      >
        Ask about scholarships
      </button>
      <dialog
        ref={dialog}
        aria-labelledby="chat-title"
        onCancel={() => trigger.current?.focus()}
      >
        <div className="section-title">
          <h2 id="chat-title">Ask with evidence</h2>
          <button onClick={close} aria-label="Close scholarship chat">
            Close
          </button>
        </div>
        <p className="hint">
          {programIds.length
            ? `About the first ${Math.min(programIds.length, 4)} saved programs`
            : "Searching this collection"}{" "}
          · {hypothetical ? "Hypothetical profile" : "Current profile"} ·
          Conversation stays in this visit.
        </p>
        <p>Answers quote source passages. They do not certify eligibility.</p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void ask();
          }}
        >
          <label>
            Your question
            <textarea
              required
              maxLength={2000}
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </label>
          <button className="primary" disabled={busy || !question.trim()}>
            Ask
          </button>
        </form>
        {busy && <p role="status">Checking source passages…</p>}
        {error && (
          <p role="alert" className="notice">
            {error}
          </p>
        )}
        {answer && (
          <section aria-label="Answer">
            <p className="hint">
              Corpus {answer.corpus_version}
              {answer.corpus_version !== corpusVersion
                ? " — sources changed; refresh your results before comparing."
                : ""}
            </p>
            {answer.blocks.map((block, i) => (
              <div key={i}>
                <blockquote>{block.text}</blockquote>
                {block.evidence_ids?.map((id) => {
                  const chunk = answer.evidence.chunks.find(
                    (c) => c.id === id || c.evidence?.some((e) => e.id === id),
                  );
                  return (
                    chunk && (
                      <details key={id}>
                        <summary>
                          Source: {chunk.heading || chunk.source_id}
                        </summary>
                        <p>{chunk.text}</p>
                        {chunk.evidence?.map((ref) => (
                          <p key={ref.id}>
                            <a href={ref.url} target="_blank" rel="noreferrer">
                              {ref.title || "Official source"}
                            </a>{" "}
                            · {ref.section_id}
                            {ref.page ? ` · page ${ref.page}` : ""} · Retrieved{" "}
                            {ref.fetched_at.slice(0, 10)} · Cycle{" "}
                            {ref.cycle || "unknown"}
                          </p>
                        ))}
                      </details>
                    )
                  );
                })}
              </div>
            ))}
            {answer.gaps?.map((gap, i) => (
              <p key={i} className="question">
                {gap}
              </p>
            ))}
            <details>
              <summary>How this answer was assembled</summary>
              <p>
                {answer.method} retrieval · {answer.evidence.chunks.length}{" "}
                passages. Matching checks the full catalog separately. Retrieval
                is not a complete eligibility audit.
              </p>
            </details>
          </section>
        )}
      </dialog>
    </div>
  );
}
