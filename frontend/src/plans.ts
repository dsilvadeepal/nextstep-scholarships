// Conservative, local hints. Unrecognized plans stay in the editable text box;
// no eligibility or acceptance is inferred from these words.
const COLLEGES = [
  ["Kennesaw State", /\bkennesaw state(?: university)?\b/i],
  ["Georgia State", /\bgeorgia state(?: university)?\b/i],
  ["Georgia Tech", /\b(?:georgia tech|georgia institute of technology)\b/i],
  ["Auburn", /\bauburn\b/i],
  ["Clemson", /\bclemson\b/i],
  ["University of Alabama", /\b(?:university of alabama|ua|bama)\b/i],
  ["Georgia Southern", /\bgeorgia southern\b/i],
] as const;

const INTERESTS = [
  ["engineering", /\bengineering\b/i],
  ["business", /\bbusiness\b/i],
  ["nursing", /\bnursing\b/i],
  ["computer science", /\bcomputer science\b/i],
  ["volunteering", /\b(?:volunteer|volunteering)\b/i],
] as const;

function clearlyMentioned(text: string, pattern: RegExp) {
  const match = pattern.exec(text);
  if (!match) return false;
  const lead = text.slice(Math.max(0, match.index - 32), match.index);
  return !/\b(?:not|never|don't|do not|no longer|no|without)\b[^.!?;]*$/i.test(lead);
}

export function normalizeCitizenship(value: string) {
  const normalized = value.trim().toLowerCase().replace(/\./g, "");
  if (["us citizen", "usa citizen", "united states citizen", "american citizen"].includes(normalized)) return "US citizen";
  if (["permanent resident", "us permanent resident", "green card holder"].includes(normalized)) return "permanent resident";
  if (["uk citizen", "british citizen"].includes(normalized)) return "UK citizen";
  return value.trim();
}

export function planHints(text: string) {
  // Only explicit first-person statements become suggested identity facts.
  const citizenship = /\b(?:i am|i'm) (?:a |an )?(?:(?:georgia resident|resident of georgia) and (?:a |an )?)?(united states citizen|u\.?s\.? citizen|american citizen|permanent resident|green card holder|uk citizen|british citizen)\b/i.exec(text)?.[1];
  const residency = /\b(?:i am|i'm) (?:a )?(?:georgia resident|resident of georgia)\b/i.test(text) ? "yes" : "";
  const volunteer = /\bi (?:do not|don't|have no|have never)[^.!?;]{0,35}\bvolunteer(?:ing)?\b/i.test(text) ? "none" : "";
  const activities = /\bi (?:am|am also|'m) (?:a )?(?:part|member) of (?:the )?science olympiad\b/i.test(text) ? "Science Olympiad" : "";
  return {
    citizenship: citizenship ? normalizeCitizenship(citizenship) : "",
    residency, volunteer, activities,
    colleges: COLLEGES.filter(([, pattern]) => clearlyMentioned(text, pattern))
      .map(([name]) => name)
      .slice(0, 3),
    interests: INTERESTS.filter(([, pattern]) => clearlyMentioned(text, pattern)).map(
      ([name]) => name,
    ),
  };
}
