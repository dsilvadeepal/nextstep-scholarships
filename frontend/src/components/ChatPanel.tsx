import { useState, useRef, useEffect } from "react";
import type { components } from "../types";
import { request } from "../api";

type Answer = components["schemas"]["AnswerResult"];
type Turn = components["schemas"]["ChatTurn"];
type Scholarship = components["schemas"]["Scholarship"];
type EvidenceRef = components["schemas"]["EvidenceRef"];
type Chunk = components["schemas"]["Chunk"];
type SourceItem = { chunk: Chunk; reference?: EvidenceRef };

function answerSources(answer: Answer): SourceItem[] {
  const cited = new Set(
    answer.blocks.flatMap((block) => block.evidence_ids || []),
  );
  const seen = new Set<string>();
  const items: SourceItem[] = [];
  for (const chunk of answer.evidence.chunks) {
    const isCited =
      cited.has(chunk.id) ||
      chunk.evidence?.some((reference) => cited.has(reference.id));
    if (!isCited) continue;
    if (chunk.evidence?.length) {
      for (const reference of chunk.evidence) {
        // One URL can contain several independently cited rules or table rows.
        const key = `${reference.url}|${reference.section_id}|${reference.quote}`;
        if (!seen.has(key)) {
          seen.add(key);
          items.push({ chunk, reference });
        }
      }
    } else if (!seen.has(chunk.id)) {
      seen.add(chunk.id);
      items.push({ chunk });
    }
  }
  for (const link of answer.source_links || []) {
    if (!seen.has(link.url)) {
      seen.add(link.url);
      items.push({
        chunk: {
          id: link.url,
          program_id: "",
          source_id: link.title,
          corpus_version: answer.corpus_version,
          text: "Additional official source supplied with this answer.",
          heading: link.title,
          section_ids: [],
          token_count: 0,
          evidence: [],
          indivisible: false,
          cycle: null,
          information_status: null,
          source_checked_at: null,
        },
        reference: {
          id: link.url,
          source_id: link.title,
          document_version: answer.corpus_version,
          section_id: "official-link",
          page: null,
          quote: "Additional official source supplied with this answer.",
          start: 0,
          end: 0,
          url: link.url,
          fetched_at: "",
          title: link.title,
          cycle: null,
        },
      });
    }
  }
  return items;
}

export function ChatPanel({
  profile,
  programIds,
  corpusVersion,
  promptRequest,
}: {
  profile: components["schemas"]["StudentProfile"];
  programIds: string[];
  corpusVersion: string;
  promptRequest: (Pick<Scholarship, "id" | "name"> & { nonce: number }) | null;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const sequence = useRef(0);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [history, setHistory] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [focusProgram, setFocusProgram] = useState<Pick<
    Scholarship,
    "id" | "name"
  > | null>(null);

  useEffect(() => {
    sequence.current++;
    setAnswer(null);
    setHistory([]);
    setError("");
    setBusy(false);
    setSourcesOpen(false);
  }, [profile, corpusVersion, programIds.join(",")]);

  useEffect(() => {
    if (!promptRequest) return;
    setFocusProgram(promptRequest);
    setQuestion(
      `Tell me about ${promptRequest.name}. What should I verify and prepare?`,
    );
    setSourcesOpen(false);
    dialog.current?.showModal();
  }, [promptRequest]);

  function openGeneral() {
    setFocusProgram(null);
    dialog.current?.showModal();
  }

  function close() {
    setSourcesOpen(false);
    dialog.current?.close();
    trigger.current?.focus();
  }

  async function ask() {
    const id = ++sequence.current;
    setBusy(true);
    setError("");
    setSourcesOpen(false);
    try {
      const next = await request<Answer>("/api/chat", {
        profile,
        request: {
          question,
          program_ids: focusProgram
            ? [focusProgram.id]
            : programIds.slice(0, 4),
          corpus_version: corpusVersion,
          method: "hybrid",
          retrieval_policy: "targeted",
        },
        history,
      });
      if (id !== sequence.current) return;
      setAnswer(next);
      const text = [
        ...next.blocks.map((block) => block.text),
        ...(next.gaps || []),
      ]
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
      if (id === sequence.current) {
        setError(
          "The answer service is unavailable or could not verify an answer. You can still browse your scholarship cards. No automatic retry was made.",
        );
      }
    } finally {
      if (id === sequence.current) setBusy(false);
    }
  }

  const sourceItems = answer ? answerSources(answer) : [];
  const sources = Array.from(
    sourceItems.reduce((groups, item) => {
      const key = item.reference?.url || item.chunk.id;
      const group = groups.get(key) || [];
      group.push(item);
      groups.set(key, group);
      return groups;
    }, new Map<string, SourceItem[]>()),
  );
  return (
    <div className="chat chat-prominent">
      <div>
        <span className="eyebrow">ASK WITH EVIDENCE</span>
        <strong>Refine your scholarship plan in conversation</strong>
        <p>Ask about eligibility, deadlines, or what to prepare next.</p>
      </div>
      <button ref={trigger} className="primary" onClick={openGeneral}>
        Ask about scholarships
      </button>
      <dialog ref={dialog} aria-labelledby="chat-title" onCancel={close}>
        <div className="section-title">
          <h2 id="chat-title">Ask about scholarships</h2>
          <button onClick={close} aria-label="Close scholarship chat">
            Close
          </button>
        </div>
        <p className="hint">
          {focusProgram
            ? `About ${focusProgram.name}`
            : programIds.length
              ? `About the first ${Math.min(programIds.length, 4)} saved programs`
              : "Searching this collection"}{" "}
          · Current profile · Conversation stays in this visit.
        </p>
        <p>
          Answers explain cited source passages. They do not certify
          eligibility.
        </p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
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
              onChange={(event) => setQuestion(event.target.value)}
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
            {answer.blocks.map((block, index) =>
              block.kind === "explanation" ? (
                <p key={index}>{block.text}</p>
              ) : (
                <blockquote key={index}>{block.text}</blockquote>
              ),
            )}
            {sources.length > 0 && (
              <button
                className="source-pill"
                onClick={() => setSourcesOpen(true)}
              >
                Sources ({sources.length})
              </button>
            )}
            {answer.gaps?.map((gap, index) => (
              <p key={index} className="question">
                {gap}
              </p>
            ))}
            <details className="answer-method">
              <summary>How this answer was assembled</summary>
              <p>
                {answer.method} retrieval · {answer.retrieval_policy} selection
                · {answer.evidence.chunks.length} passages. Matching checks the
                full catalog separately. Retrieval is not a complete eligibility
                audit.
              </p>
            </details>
          </section>
        )}
        {sourcesOpen && (
          <section
            className="source-drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby="source-title"
          >
            <div className="section-title">
              <div>
                <span className="eyebrow">ANSWER EVIDENCE</span>
                <h2 id="source-title">Sources ({sources.length})</h2>
              </div>
              <button
                onClick={() => setSourcesOpen(false)}
                aria-label="Close sources"
              >
                Close
              </button>
            </div>
            <div className="source-list">
              {sources.map(([key, passages], index) => (
                <article className="source-card" key={key}>
                  <span className="source-number">{index + 1}</span>
                  {passages.map(({ chunk, reference }) => (
                    <div key={reference?.id || chunk.id}>
                      <h3>
                        {reference?.title || chunk.heading || chunk.source_id}
                      </h3>
                      <blockquote>{reference?.quote || chunk.text}</blockquote>
                      <p className="hint">
                        {reference?.section_id ||
                          chunk.heading ||
                          "Source passage"}
                        {reference?.page ? ` · page ${reference.page}` : ""}
                        {reference?.fetched_at
                          ? ` · Retrieved ${reference.fetched_at.slice(0, 10)}`
                          : ""}
                        {reference?.cycle ? ` · Cycle ${reference.cycle}` : ""}
                      </p>
                    </div>
                  ))}
                  {passages[0].reference?.url && (
                    <a
                      href={passages[0].reference.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open official source
                    </a>
                  )}
                </article>
              ))}
            </div>
          </section>
        )}
      </dialog>
    </div>
  );
}
