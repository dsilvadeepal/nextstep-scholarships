import type { components } from './types';
type Scholarship = components['schemas']['Scholarship'];
export const categories = ['College scholarships', 'Company-sponsored scholarships', 'Foundations & community organizations', 'Other scholarships'] as const;
const colleges: Record<string, [string[], string]> = {
  'uga-foundation-fellowship': [['UGA', 'University of Georgia'], 'GA'],
  'georgia-southern-merit': [['Georgia Southern', 'Georgia Southern University'], 'GA'],
  'gsu-stamps-presidential': [['GSU', 'Georgia State', 'Georgia State University'], 'GA'],
  'gatech-stamps-gold': [['Georgia Tech', 'Georgia Institute of Technology'], 'GA'],
  park: [['NC State', 'North Carolina State University'], 'NC'],
  'vanderbilt-ingram': [['Vanderbilt', 'Vanderbilt University'], 'TN'],
  levine: [['UNC Charlotte', 'University of North Carolina at Charlotte'], 'NC'],
  'morehead-cain': [['UNC', 'UNC Chapel Hill', 'University of North Carolina at Chapel Hill'], 'NC'],
  robertson: [['Duke', 'Duke University', 'UNC', 'UNC Chapel Hill', 'University of North Carolina at Chapel Hill'], 'NC'],
  'fsu-presidential': [['FSU', 'Florida State', 'Florida State University'], 'FL'],
  'uah-out-of-state': [['UAH', 'University of Alabama in Huntsville'], 'AL'],
  'uab-out-of-state': [['UAB', 'University of Alabama at Birmingham'], 'AL'],
  'south-alabama-out-of-state': [['South Alabama', 'University of South Alabama'], 'AL'],
};
const companies = new Set(['delta-hbcu', 'cfa-community', 'coca-cola', 'burger-king-general', 'live-mas-new', 'cobb-emc', 'sawnee-youth']);
const foundations = new Set(['coolidge', 'watson-brown', 'elks-mvs', 'elks-legacy', 'cooke-college', 'geicc', 'gates', 'hagan', 'ron-brown']);
const normalize = (name: string) => name.toLowerCase().replace(/[^a-z0-9]/g, '');
export function scholarshipGroup(s: Scholarship) {
  const college = colleges[s.id] || (s.id.startsWith('ua-') ? [['Alabama', 'University of Alabama', 'The University of Alabama'], 'AL'] as [string[], string] : s.id.startsWith('auburn-') ? [['Auburn', 'Auburn University'], 'AL'] as [string[], string] : undefined);
  return { category: college ? categories[0] : companies.has(s.id) ? categories[1] : foundations.has(s.id) ? categories[2] : categories[3], college };
}
export function matchesCollegeChoice(s: Scholarship, choices: string[]) {
  const { college } = scholarshipGroup(s);
  return !college || !choices.length || choices.some(choice => college[0].some(alias => normalize(alias) === normalize(choice)));
}
