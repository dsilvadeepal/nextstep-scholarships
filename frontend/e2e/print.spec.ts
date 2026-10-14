import {test,expect} from '@playwright/test';
test('synthetic scholarship print includes unresolved conditions and source',async({page})=>{
 await page.route('**/api/matches',route=>route.fulfill({json:{corpus_version:'synthetic',scholarships:[{id:'test',name:'Synthetic test award',corpus_version:'synthetic',information_status:'automatically_extracted',cycle:'2026',deadline:'2026-12-01',materials:['Request a transcript'],evidence:[{id:'e',quote:'Seniors may apply.',url:'https://example.org/fixture',title:'Synthetic fixture',section_id:'rules',fetched_at:'2026-10-14T00:00:00Z'}]}],matches:[{scholarship_id:'test',group:'matches',fit:'Potential match',timing:'unknown',evidence_label:'automatically_extracted',followups:['Confirm your membership'],conditions:[]}]}}));
 await page.goto('/');await page.getByRole('button',{name:'Fictional senior'}).click();await page.getByRole('button',{name:'+ Add to my plan'}).click();
 await page.emulateMedia({media:'print'});
 await expect(page.getByRole('heading',{name:'My next steps'})).toBeVisible();
 await expect(page.locator('.print-plan')).toContainText('Confirm your membership');
 await expect(page.locator('.print-plan')).toContainText('https://example.org/fixture');
 await page.pdf({path:`/tmp/nextstep-plan-${test.info().project.name}.pdf`,format:'A4',printBackground:true});
 await page.screenshot({path:`/tmp/nextstep-print-${test.info().project.name}.png`,fullPage:true});
});
