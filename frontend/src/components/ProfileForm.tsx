import { useState } from "react";
import type { components } from "../types";
import { RouteIllustration } from "./BrandAssets";
import { planHints } from "../plans";
export type StudentProfile = components["schemas"]["StudentProfile"];
const list = (value: string) =>
  value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
export function ProfileForm({
  onSubmit,
}: {
  onSubmit: (profile: StudentProfile) => void;
}) {
  const [fields, setFields] = useState<Record<string, string>>({});
  const [showDetails, setShowDetails] = useState(false);
  const [useHints, setUseHints] = useState(false);
  const value = (key: string) => fields[key] || "";
  const hints = planHints(value("plans"));
  const colleges = value("colleges") ? list(value("colleges")) : useHints ? hints.colleges : [];
  const interests = value("interests") ? list(value("interests")) : useHints ? hints.interests : [];
  const input = (
    key: string,
    label: string,
    type = "text",
    placeholder = "",
  ) => (
    <label>
      {label}
      <input
        type={type}
        value={value(key)}
        placeholder={placeholder}
        maxLength={200}
        onChange={(e) => setFields({ ...fields, [key]: e.target.value })}
      />
    </label>
  );
  const select = (key: string, label: string, options: [string, string][]) => (
    <label>
      {label}
      <select
        value={value(key)}
        onChange={(e) => setFields({ ...fields, [key]: e.target.value })}
      >
        <option value="">Skip / not sure</option>
        {options.map(([v, l]) => (
          <option value={v} key={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
  return (
    <section className="profile">
      <div className="eyebrow">YOUR NEXT CHAPTER</div>
      <h1>
        Big possibilities.
        <br />
        <span>One next step.</span>
      </h1>
      <p>
        Explore scholarships, understand the requirements, and build a plan that
        feels manageable.
      </p>
      <div className="hero-illustration" aria-hidden="true">
        <RouteIllustration />
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const context: Record<string, unknown> = {};
          for (const key of [
            "membership",
            "employer",
            "utility",
            "citizenship",
          ])
            if (value(key)) context[key] = value(key);
          for (const key of ["accepted_colleges", "enrolled_colleges"])
            if (value(key)) context[key] = list(value(key));
          if (value("residency") === "no") context.georgia_resident = false;
          if (value("plans")) context.student_plans = value("plans");
          const residence = Object.fromEntries(
            ["state", "county", "city"]
              .filter((k) => value(k))
              .map((k) => [k, k === "state" ? value(k).toUpperCase() : value(k)]),
          );
          if (value("residency") === "yes") residence.state = "GA";
          onSubmit({
            grade: value("grade") ? (Number(value("grade")) as 11 | 12) : null,
            graduation_year: value("year") ? Number(value("year")) : null,
            residence,
            gpa: value("gpa")
              ? {
                  value: Number(value("gpa")),
                  scale: value("scale") ? Number(value("scale")) : null,
                  type: (value("type") || "unknown") as
                    "weighted" | "unweighted" | "unknown",
                  estimated: value("documentation")
                    ? value("documentation") === "estimated"
                    : null,
                  as_of: value("date") || null,
                }
              : null,
            interests: interests.slice(0, 20),
            prospective_colleges: colleges.slice(0, 3),
            context,
          });
        }}
      >
        <p className="hint">
          Start with what you know. Your profile lasts for this visit. Do not
          enter names, account numbers or other identifying details.
        </p>
        <div className="fields">
          {select("grade", "School year", [
            ["11", "Junior"],
            ["12", "Senior"],
          ])}
          {select("residency", "Georgia resident?", [
            ["yes", "Yes"],
            ["no", "No"],
          ])}
          {input("gpa", "GPA value", "number")}
          {value("gpa") && select("documentation", "GPA documentation", [
            ["estimated", "Estimated"],
            ["documented", "Final / school record"],
          ])}
        </div>
        <label className="plans-field">
          Tell us a little about your plans (optional)
          <textarea
            value={value("plans")}
            maxLength={500}
            placeholder="I'm interested in engineering, considering Georgia Tech and Auburn, and I volunteer."
            onChange={(e) => {
              setFields({ ...fields, plans: e.target.value });
              setUseHints(false);
            }}
          />
        </label>
        <div className="understood" aria-live="polite">
          <strong>What we understood</strong>
          <p>
            {value("grade") === "11" ? "Junior" : value("grade") === "12" ? "Senior" : "School year unknown"}
            {" · "}
            {value("residency") === "yes" ? "Georgia resident" : value("residency") === "no" ? "Not a Georgia resident" : "Georgia residency unknown"}
            {" · "}
            {value("gpa") ? `${value("documentation") === "documented" ? "Final" : value("documentation") === "estimated" ? "Estimated" : "Unconfirmed"} GPA ${value("gpa")}` : "GPA unknown"}
          </p>
          {(hints.colleges.length > 0 || hints.interests.length > 0) && (
            <p>
              Detected mentions: {hints.colleges.join(", ")}{hints.colleges.length > 0 && hints.interests.length > 0 ? "; " : ""}{hints.interests.join(", ")}.
            </p>
          )}
          {(hints.colleges.length > 0 || hints.interests.length > 0) && (
            <label className="hint">
              <input type="checkbox" checked={useHints} onChange={(e) => setUseHints(e.target.checked)} />
              Use these colleges and interests in my matches
            </label>
          )}
          {value("plans") && <p className="hint">Your full note stays with this visit's profile for follow-up questions. Only confirmed mentions affect matching. A college you are considering is not treated as an acceptance.</p>}
          <button type="button" onClick={() => setShowDetails(true)}>Edit details</button>
        </div>
        <details className="optional-fields" open={showDetails} onToggle={(e) => setShowDetails(e.currentTarget.open)}>
          <summary>Add more details</summary>
          <p>Leave uncertain answers blank. A GPA without its scale and type cannot establish a score threshold.</p>
          <div className="fields">
          {input("year", "Graduation year", "number")}
          {input("state", "State of residence", "text", "e.g. GA")}
          {select("scale", "GPA scale", [
            ["4", "4-point"],
            ["5", "5-point"],
            ["100", "100-point"],
          ])}
          {select("type", "GPA type", [
            ["unweighted", "Unweighted"],
            ["weighted", "Weighted"],
          ])}
          {input("date", "GPA as of", "date")}
          {input(
            "colleges",
            "Considering colleges (up to 3)",
            "text",
            "Names separated by commas",
          )}
          {input(
            "interests",
            "Academic interests",
            "text",
            "e.g. engineering, business",
          )}
          <p>
            Considering a college does not mean you have been accepted. Add only
            facts you know; leave uncertain answers blank.
          </p>
            {input("county", "County")}
            {input("city", "City")}
            {input(
              "accepted_colleges",
              "Colleges with an acceptance letter",
              "text",
              "Names separated by commas",
            )}
            {input(
              "enrolled_colleges",
              "Colleges enrolled in",
              "text",
              "Names separated by commas",
            )}
            {input("membership", "Credit union or organization membership")}
            {input("employer", "Employer relevant to an award")}
            {input("utility", "Household utility provider")}
            {input("citizenship", "Citizenship or residency category")}
          </div>
        </details>
        <button className="primary">
          Find my matches
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true" focusable="false">
            <path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </form>
      <div className="starters">
        <span>Just looking? Try a fictional profile</span>
        <button
          onClick={() =>
            onSubmit({
              graduation_year: null,
              grade: 11,
              residence: { state: "GA" },
              gpa: null,
            })
          }
        >
          Fictional junior
        </button>
        <button
          onClick={() =>
            onSubmit({
              graduation_year: null,
              grade: 12,
              residence: { state: "GA" },
              gpa: {
                value: 3.5,
                scale: 4,
                type: "unweighted",
                estimated: true,
                as_of: null,
              },
            })
          }
        >
          Fictional senior
        </button>
        <button
          onClick={() =>
            onSubmit({ graduation_year: null, grade: null, gpa: null })
          }
        >
          Fictional undecided student
        </button>
      </div>
    </section>
  );
}
