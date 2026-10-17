import { useState, useEffect, useRef } from "react";
import { request } from "../api";
import { CaseInspector } from "./CaseInspector";
import type { CaseRow } from "./CaseInspector";
type Config = {
  corpus_version: string;
  cases: string[];
  methods: string[];
  split: string;
  suite_hash: string;
};
type Run = {
  id: string;
  status: string;
  config: Config;
  results?: CaseRow[];
  historical?: boolean;
  metrics?: unknown;
};
export function EvalDashboard() {
  const [auth, setAuth] = useState<{
      configured: boolean;
      authenticated: boolean;
    } | null>(null),
    [runs, setRuns] = useState<Run[]>([]),
    [active, setActive] = useState<Run | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [reports, setReports] = useState<unknown>(null),
    [ack, setAck] = useState(false);
  const stopped = useRef(false);
  useEffect(() => {
    void request<{ configured: boolean; authenticated: boolean }>(
      "/api/auth/status",
    )
      .then((a) => {
        setAuth(a);
        if (a.authenticated) {
          void refresh();
          void request("/api/admin/ingestion")
            .then(setReports)
            .catch(() => setReports({ note: "Reports unavailable" }));
        }
      })
      .catch(() => setError("Could not verify admin sign-in."));
    return () => {
      stopped.current = true;
    };
  }, []);
  async function refresh() {
    try {
      setRuns(await request<Run[]>("/api/admin/runs"));
    } catch {
      setError("Run history unavailable.");
    }
  }
  async function inspect(id: string) {
    const r = await request<Run>(`/api/admin/runs/${id}`);
    setActive(r);
    return r;
  }
  async function start(split: string) {
    setError("");
    try {
      const { id } = await request<{ id: string }>("/api/admin/runs", {
        split,
      });
      await inspect(id);
      await refresh();
    } catch {
      setError(
        "Run could not start. Check live access/budget, an existing active run, or the heldout restriction.",
      );
    }
  }
  async function drive() {
    if (!active) return;
    stopped.current = false;
    setBusy(true);
    setError("");
    try {
      let current = await inspect(active.id);
      for (const [index, id] of current.config.cases.entries()) {
        const methods =
          index % 2
            ? [...current.config.methods].reverse()
            : current.config.methods;
        for (const method of methods) {
          if (stopped.current) return;
          const row = current.results?.find(
            (r) => r.case_id === id && r.method === method,
          );
          if (row?.status === "completed") continue;
          if (row && row.status !== "pending") {
            setError(
              "An in-flight or failed case needs attention. Refresh status; retry only after acknowledging possible duplicate cost.",
            );
            return;
          }
          await request(
            `/api/admin/runs/${current.id}/cases/${id}?method=${method}`,
            {},
          );
          current = await inspect(current.id);
          if (
            current.results?.some(
              (r) => r.status === "error" || r.status === "interrupted",
            )
          ) {
            setError(
              "A case stopped. Inspect the saved error before explicitly retrying.",
            );
            return;
          }
        }
      }
    } catch {
      setError(
        "Execution stopped. Refresh to inspect persisted progress. An interrupted provider call may have incurred cost.",
      );
    } finally {
      setBusy(false);
      await refresh();
    }
  }
  async function retry(row: CaseRow) {
    if (!active || !ack) return;
    try {
      await request(
        `/api/admin/runs/${active.id}/cases/${row.case_id}/retry?method=${row.method}`,
        { acknowledge_cost: true },
      );
      await inspect(active.id);
      setAck(false);
    } catch {
      setError(
        "Retry rejected: the attempt may still be running, completed, or another run is active.",
      );
    }
  }
  const total = active
      ? active.config.cases.length * active.config.methods.length
      : 0,
    rows = active?.results || [],
    completed = rows.filter((r) => r.status === "completed"),
    passed = rows.filter((r) => r.result?.scores?.passed === true).length;
  return (
    <main className="admin">
      <a href="/">← Student view</a>
      <h1>Evaluation workspace</h1>
      <p>
        Fictional profiles only. Completed cases are saved; closing this page
        stops dispatching new cases. In-flight work may still finish.
      </p>
      {error && (
        <p role="alert" className="notice">
          {error}
        </p>
      )}
      {!auth ? (
        <p>Checking sign-in…</p>
      ) : !auth.authenticated ? (
        <section>
          {auth.configured ? (
            <a href="/api/auth/login">Sign in with Replit</a>
          ) : (
            <p>Admin sign-in is not configured</p>
          )}
        </section>
      ) : (
        <>
          <div className="tabs">
            <button onClick={() => void start("tuning")} disabled={busy}>
              Create tuning run
            </button>
            <button onClick={() => void start("heldout")} disabled={busy}>
              Open heldout suite once
            </button>
            <button
              onClick={() =>
                void request("/api/auth/logout", {}).then(() =>
                  location.reload(),
                )
              }
            >
              Sign out
            </button>
          </div>
          <p className="hint">
            Runs use both semantic and hybrid retrieval with alternating order
            and a frozen configuration. Heldout data cannot be reopened as a
            fresh experiment after exposure.
          </p>
          <h2>Saved runs</h2>
          {runs.map((r) => (
            <button
              key={r.id}
              onClick={() =>
                void inspect(r.id).catch(() => setError("Run unavailable"))
              }
            >
              Inspect {r.id} · {r.status}
            </button>
          ))}
          {active && (
            <section>
              <h2>{active.status} run</h2>
              {active.historical && (
                <p className="notice">
                  Historical corpus — this run retains its original sources and
                  settings.
                </p>
              )}
              <p>
                {completed.length}/{total} completed · {passed}/{total} passed
                (errors and incomplete cases are not passes)
              </p>
              <details>
                <summary>Aggregate scores and release gates</summary>
                <pre>
                  {JSON.stringify(
                    active.metrics || {
                      note: "No aggregate metrics available",
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
              <details>
                <summary>Immutable configuration</summary>
                <pre>{JSON.stringify(active.config, null, 2)}</pre>
              </details>
              <div className="tabs">
                <button
                  disabled={busy || active.status !== "active"}
                  onClick={() => void drive()}
                >
                  Run / resume incomplete cases
                </button>
                <button
                  onClick={() => {
                    stopped.current = true;
                  }}
                >
                  Stop after this case
                </button>
                <button onClick={() => void inspect(active.id)}>
                  Refresh status
                </button>
                <button
                  onClick={() => {
                    stopped.current = true;
                    void request(`/api/admin/runs/${active.id}/cancel`, {})
                      .then(() => inspect(active.id))
                      .catch(() => setError("Cancel failed; refresh status"));
                  }}
                >
                  Cancel run
                </button>
              </div>
              <p>
                Paired regressions (semantic pass → hybrid fail):{" "}
                {active.config.cases
                  .filter(
                    (id) =>
                      rows.some(
                        (r) =>
                          r.case_id === id &&
                          r.method === "semantic" &&
                          r.result?.scores?.passed === true,
                      ) &&
                      rows.some(
                        (r) =>
                          r.case_id === id &&
                          r.method === "hybrid" &&
                          r.result?.scores?.passed === false,
                      ),
                  )
                  .join(", ") ||
                  "None recorded; incomplete pairs are not comparisons."}
              </p>
              <label>
                <input
                  type="checkbox"
                  checked={ack}
                  onChange={(e) => setAck(e.target.checked)}
                />
                I acknowledge an interrupted attempt may already have incurred
                provider cost.
              </label>
              {rows.map((r) => (
                <div key={r.case_id + r.method}>
                  <CaseInspector row={r} />
                  {["error", "interrupted"].includes(r.status) && (
                    <button
                      disabled={!ack || busy}
                      onClick={() => void retry(r)}
                    >
                      Retry {r.case_id} / {r.method}
                    </button>
                  )}
                </div>
              ))}
            </section>
          )}
          <details>
            <summary>Read-only ingestion report</summary>
            <pre>{JSON.stringify(reports, null, 2)}</pre>
          </details>
        </>
      )}
    </main>
  );
}
