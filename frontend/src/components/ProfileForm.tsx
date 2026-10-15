import { useState } from "react";
import type { components } from "../types";
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
  const value = (key: string) => fields[key] || "";
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
          onSubmit({
            grade: value("grade") ? (Number(value("grade")) as 11 | 12) : null,
            graduation_year: value("year") ? Number(value("year")) : null,
            residence: Object.fromEntries(
              ["state", "county", "city"]
                .filter((k) => value(k))
                .map((k) => [
                  k,
                  k === "state" ? value(k).toUpperCase() : value(k),
                ]),
            ),
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
            interests: list(value("interests")).slice(0, 20),
            prospective_colleges: list(value("colleges")).slice(0, 3),
            context,
          });
        }}
      >
        <p className="hint">
          Every question is optional. Your profile lasts for this visit. Do not
          enter names, account numbers or other identifying details.
        </p>
        <div className="fields">
          {select("grade", "School year", [
            ["11", "Junior"],
            ["12", "Senior"],
          ])}
          {input("year", "Graduation year", "number")}
          {input("state", "State of residence", "text", "e.g. GA")}
          {input("gpa", "GPA value", "number")}
          {select("scale", "GPA scale", [
            ["4", "4-point"],
            ["5", "5-point"],
            ["100", "100-point"],
          ])}
          {select("type", "GPA type", [
            ["unweighted", "Unweighted"],
            ["weighted", "Weighted"],
          ])}
          {select("documentation", "GPA documentation", [
            ["estimated", "My estimate"],
            ["documented", "From my school record"],
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
        </div>
        <details className="optional-fields">
          <summary>Optional details for more specific requirements</summary>
          <p>
            Considering a college does not mean you have been accepted. Add only
            facts you know; leave uncertain answers blank.
          </p>
          <div className="fields">
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
        <button className="primary">Explore scholarships</button>
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
