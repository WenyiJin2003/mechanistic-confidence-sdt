// Headless checks of the locally generated reviewer; no network or real review.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(path.join(process.argv[3], 'playwright'));

(async () => {
  const options = {headless: true};
  const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (!fs.existsSync(chromium.executablePath()) && fs.existsSync(localChrome)) options.executablePath = localChrome;
  const browser = await chromium.launch(options);
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}, acceptDownloads: true});
    const file = path.resolve(process.argv[2]);
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(pathToFileURL(file).href);
    assert.equal(await page.locator('.card').count(), 50);
    assert.equal(await page.locator('.card:visible').count(), 1);
    assert.equal(await page.locator('#position').textContent(), '1 / 50');
    assert.match(await page.locator('#progress').textContent(), /0 \/ 50/);
    await page.screenshot({path: path.join(path.dirname(file), 'REVIEW_UI_PREVIEW.png'), fullPage: true});
    await page.locator('#next').click();
    assert.equal(await page.locator('#position').textContent(), '2 / 50');
    await page.locator('#jump').selectOption('49');
    assert.equal(await page.locator('#position').textContent(), '50 / 50');
    await page.locator('#jump').selectOption('0');
    await page.locator('.card:visible [data-field=content_preserved]').selectOption('yes');
    await page.locator('.card:visible [data-field=more_certain]').selectOption('A');
    await page.locator('.card:visible [data-field=other_confound]').selectOption('no');
    assert.match(await page.locator('#progress').textContent(), /1 \/ 50/);
    await page.reload();
    assert.equal(await page.locator('.card:visible [data-field=content_preserved]').inputValue(), 'yes');
    const downloadEvent = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloadEvent;
    const exportData = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
    assert.equal(exportData.reviews.length, 50);
    assert.equal(exportData.reviews.filter(r => r.human_review === 'annotated').length, 1);
    assert.equal(exportData.reviews.filter(r => r.human_review === 'pending').length, 49);
    assert.equal(errors.length, 0);
    await page.evaluate(() => localStorage.clear());
    console.log(JSON.stringify({cards: 50, navigation: 'pass', local_save: 'pass', export: 'pass', script_errors: errors.length,
                               test_annotations: 'ephemeral browser only; not human review'}));
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
