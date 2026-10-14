import { useState } from "react";
import type { StudentProfile } from "./ProfileForm";
export function ScenarioPanel({
  profile,
  onApply,
  onReset,
}: {
  profile: StudentProfile;
  onApply: (overrides: Partial<StudentProfile>) => void;
  onReset: () => void;
}) {
  const [gpa, setGpa] = useState("");
  const [college, setCollege] = useState("");
  return (
    <details className="scenario">
      <summary>What if my GPA or college plans change?</summary>
      <p>Explore a hypothetical change. Your original profile stays intact.</p>
      <div className="fields">
        <label>
          Hypothetical GPA
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
          Hypothetical college
          <input value={college} onChange={(e) => setCollege(e.target.value)} />
        </label>
      </div>
      <button
        onClick={() =>
          onApply({
            ...(gpa
              ? {
                  gpa: {
                    ...profile.gpa,
                    value: Number(gpa),
                    scale: profile.gpa?.scale ?? null,
                    type: profile.gpa?.type ?? "unknown",
                    estimated: true,
                    as_of: null,
                  },
                }
              : {}),
            ...(college ? { prospective_colleges: [college] } : {}),
          })
        }
      >
        Try scenario
      </button>
      <button
        onClick={() => {
          setGpa("");
          setCollege("");
          onReset();
        }}
      >
        Restore original profile
      </button>
    </details>
  );
}
