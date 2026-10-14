import {test,expect} from '@playwright/test';
test('skippable profile and honest unavailable catalog',async({page})=>{
 await page.route('**/api/matches',route=>route.fulfill({status:503,body:'{}'}));
 await page.goto('/');
 await expect(page.getByRole('heading',{name:/Big possibilities/})).toBeVisible();
 await page.getByRole('button',{name:'Explore scholarships'}).click();
 await expect(page.getByRole('alert')).toContainText('not available');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 expect(await page.evaluate(()=>Object.keys(localStorage))).toEqual([]);
 await page.screenshot({path:`/tmp/nextstep-${test.info().project.name}.png`,fullPage:true});
});
