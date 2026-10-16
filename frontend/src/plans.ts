// Conservative, local hints. Unrecognized plans stay in the editable text box;
// no eligibility or acceptance is inferred from these words.
const COLLEGES = [
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
  return !/\b(?:not|never|don't|do not|no longer)\b[^.!?;]*$/i.test(lead);
}

export function planHints(text: string) {
  return {
    colleges: COLLEGES.filter(([, pattern]) => clearlyMentioned(text, pattern))
      .map(([name]) => name)
      .slice(0, 3),
    interests: INTERESTS.filter(([, pattern]) => clearlyMentioned(text, pattern)).map(
      ([name]) => name,
    ),
  };
}
