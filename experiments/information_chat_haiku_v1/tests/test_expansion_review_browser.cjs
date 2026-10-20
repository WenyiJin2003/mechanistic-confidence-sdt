// Fresh headless Chrome only; never attaches to the user's browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('/Users/jwy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
  const root = path.resolve(__dirname, '../private_data/expansion_10000_v1');
  const latest = JSON.parse(fs.readFileSync(path.join(root, 'LATEST_REVIEW.json'), 'utf8'));
  const folder = path.dirname(latest.review_index);
  const packet = JSON.parse(fs.readFileSync(path.join(folder, 'TRIPLETS.json'), 'utf8'));
  assert.equal(packet.triplets.length, latest.total_generated_triplets);
  const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const context = await browser.newContext({acceptDownloads: true, viewport: {width: 1440, height: 1000}});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(latest.review_index).href);
    assert.equal(await page.locator('a[href^="PAGE_"]').count(), latest.pages);
    let checked = 0;
    for (let i = 0; i < latest.pages; i++) {
      const name = `PAGE_${String(i + 1).padStart(3, '0')}.html`;
      await page.goto(pathToFileURL(path.join(folder, name)).href);
      const records = packet.review_records.slice(i * 100, i * 100 + 100);
      assert.equal(await page.locator('.card').count(), records.length);
      assert.deepEqual(await page.locator('.response').allTextContents(), records.flatMap(r => [r.version_a, r.version_b]));
      assert.deepEqual(await page.locator('.card > details[open] .verbatim').allTextContents(), records.map(r => r.reference.original_response));
      assert.equal(await page.locator('.card:visible').count(), 1);
      assert(await page.locator('select[data-field]').evaluateAll(nodes => nodes.every(n => n.value === '')));
      const downloadEvent = page.waitForEvent('download');
      await page.locator('#export').click();
      const downloaded = JSON.parse(fs.readFileSync(await (await downloadEvent).path(), 'utf8'));
      assert.equal(downloaded.schema, 'haiku-expansion-human-review-v1');
      assert.equal(downloaded.reviews.length, records.length);
      await page.setViewportSize({width: 390, height: 844});
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.setViewportSize({width: 1440, height: 1000});
      checked += records.length;
    }
    assert.equal(checked, latest.new_generated_triplets);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({passed: true, new_pairs_verified: checked, user_browser_used: false, human_review_completed: false}));
    await context.close();
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
