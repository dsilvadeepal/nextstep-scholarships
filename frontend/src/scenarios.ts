import type { StudentProfile } from "./components/ProfileForm";
export function applyScenario(
  profile: StudentProfile,
  overrides: Partial<StudentProfile>,
): StudentProfile {
  return structuredClone({ ...profile, ...overrides });
}
