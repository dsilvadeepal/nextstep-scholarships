import { useState } from "react";
import type { components } from "../types";
export type StudentProfile = components["schemas"]["StudentProfile"];
export function ProfileForm({
  onSubmit,
}: {
  onSubmit: (profile: StudentProfile) => void;
}) {
  const [grade, setGrade] = useState("");
  const [gpa, setGpa] = useState("");
  const [state, setState] = useState("");
  const [college, setCollege] = useState("");
  const [gpaType, setGpaType] = useState("unknown");
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
          onSubmit({
            graduation_year: null,
            grade: grade ? (Number(grade) as 11 | 12) : null,
            gpa: gpa
              ? {
                  value: Number(gpa),
                  scale: 4,
                  type: gpaType as "weighted" | "unweighted" | "unknown",
                  estimated: true,
                  as_of: null,
                }
              : null,
            residence: state ? { state } : {},
            prospective_colleges: college
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean)
              .slice(0, 3),
          });
        }}
      >
        <p className="hint">
          Every question is optional. Your profile lasts for this visit.
        </p>
        <div className="fields">
          <label>
            School year
            <select value={grade} onChange={(e) => setGrade(e.target.value)}>
              <option value="">Skip for now</option>
              <option value="11">Junior</option>
              <option value="12">Senior</option>
            </select>
          </label>
          <label>
            State of residence
            <input
              placeholder="e.g. GA"
              value={state}
              onChange={(e) => setState(e.target.value.toUpperCase())}
            />
          </label>
          <label>
            Estimated GPA (4-point scale)
            <input
              type="number"
              min="0"
              max="5"
              step="0.01"
              value={gpa}
              onChange={(e) => setGpa(e.target.value)}
            />
          </label>
          <label>
            GPA type
            <select
              value={gpaType}
              onChange={(e) => setGpaType(e.target.value)}
            >
              <option value="unknown">I'm not sure</option>
              <option value="unweighted">Unweighted</option>
              <option value="weighted">Weighted</option>
            </select>
          </label>
          <label className="wide">
            Considering colleges (up to 3)
            <input
              placeholder="College names, separated by commas"
              value={college}
              onChange={(e) => setCollege(e.target.value)}
            />
          </label>
        </div>
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
      </div>
    </section>
  );
}
