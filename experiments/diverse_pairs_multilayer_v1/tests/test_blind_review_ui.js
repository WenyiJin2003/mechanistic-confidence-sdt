// Headless checks of a locally generated generic blind-review page.
// Test selections live only in an isolated browser context and are cleared.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(path.join(process.argv[4], 'playwright'));

(async () => {
  const file = path.resolve(process.argv[2]);
  const expected = Number(process.argv[3]);
  assert(Number.isInteger(expected) && expected > 0);
  const options = {headless: true};
  const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (!fs.existsSync(chromium.executablePath()) && fs.existsSync(localChrome)) {
    options.executablePath = localChrome;
  }
  const browser = await chromium.launch(options);
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}, acceptDownloads: true});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    await page.goto(pathToFileURL(file).href);
    assert.equal(await page.locator('.card').count(), expected);
    assert.equal(await page.locator('.card:visible').count(), 1);
    assert.equal(await page.locator('#position').textContent(), `1 / ${expected}`);
    assert.match(await page.locator('#progress').textContent(), new RegExp(`0 / ${expected}$`));
    await page.screenshot({path: path.join(path.dirname(file), 'BLIND_REVIEW_PREVIEW.png'), fullPage: true});

    await page.locator('#next').click();
    assert.equal(await page.locator('#position').textContent(), `2 / ${expected}`);
    await page.locator('#jump').selectOption(String(expected - 1));
    assert.equal(await page.locator('#position').textContent(), `${expected} / ${expected}`);
    await page.locator('#jump').selectOption('0');
    await page.locator('.card:visible [data-field=content_equivalence]').selectOption('both_match');
    await page.locator('.card:visible [data-field=certainty_contrast]').selectOption('a_more_certain');
    await page.locator('.card:visible [data-field=naturalness]').selectOption('both_natural');
    await page.locator('.card:visible [data-field=cue_scope]').selectOption('both_global');
    await page.locator('.card:visible [data-field=decision]').selectOption('accept');
    assert.match(await page.locator('#progress').textContent(), new RegExp(`1 / ${expected}$`));
    await page.reload();
    assert.equal(
      await page.locator('.card:visible [data-field=content_equivalence]').inputValue(),
      'both_match',
    );

    const downloadEvent = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloadEvent;
    assert.equal(download.suggestedFilename(), `blind_human_review_${expected}.json`);
    const exported = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
    assert.equal(exported.reviews.length, expected);
    assert.equal(exported.reviews.filter(row => row.decision === 'accept').length, 1);
    assert.equal(errors.length, 0);
    await page.evaluate(() => localStorage.clear());
    console.log(JSON.stringify({
      cards: expected,
      navigation: 'pass',
      local_save: 'pass',
      export: 'pass',
      script_errors: errors.length,
      test_annotations: 'ephemeral browser only; not human review',
    }));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
