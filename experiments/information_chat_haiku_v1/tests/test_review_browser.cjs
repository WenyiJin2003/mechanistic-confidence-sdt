// Isolated headless browser only: never connects to an existing user session.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('/Users/jwy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const root = path.resolve(__dirname, '../private_data/canary_50_v1/review_final_v2');
  const packet = JSON.parse(fs.readFileSync(path.join(root, 'TRIPLETS_50.json'), 'utf8'));
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'MANIFEST.json'), 'utf8'));
  const qa = path.join(root, 'browser_qa');
  fs.mkdirSync(qa, {recursive: true});
  const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 1080}, acceptDownloads: true});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(root, 'REVIEW.html')).href);
    assert.equal(await page.locator('.card').count(), 50);
    assert.equal(await page.locator('.card:visible').count(), 1);
    assert.equal(await page.locator('.response').count(), 100);
    assert.deepEqual(await page.locator('.response').allTextContents(), packet.review_records.flatMap(r => [r.version_a, r.version_b]));
    assert.deepEqual(await page.locator('.card > details[open] .verbatim').allTextContents(), packet.triplets.map(r => r.original));
    assert.equal(await page.locator('#progress').textContent(), '已检查 0 / 50');
    const initial = await page.locator('select[data-field]').evaluateAll(nodes => nodes.every(n => n.value === ''));
    assert(initial, 'A fresh reviewer must not receive prefilled judgments');
    const first = page.locator('.card').first();
    await first.locator('[data-field="content_equivalence"]').selectOption('same');
    await first.locator('[data-field="more_certain"]').selectOption('a');
    await first.locator('[data-field="contrast"]').selectOption('clear');
    await first.locator('[data-field="notes"]').fill('Headless QA only; not a human judgment.');
    assert.equal(await page.locator('#progress').textContent(), '已检查 1 / 50');
    await page.locator('#next').click();
    assert.equal(await page.locator('.card:visible').getAttribute('data-id'), 'HC002');
    await page.locator('#prev').click();
    await page.reload();
    assert.equal(await first.locator('[data-field="content_equivalence"]').inputValue(), 'same');
    assert.equal(await page.locator('#progress').textContent(), '已检查 1 / 50');
    const downloadEvent = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloadEvent;
    const exported = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
    assert.equal(exported.packet_sha256, manifest.packet_semantic_sha256);
    assert.equal(exported.reviews.length, 50);
    assert.equal(exported.reviews[0].review_id, 'HC001');
    assert.equal(exported.reviews[0].notes, 'Headless QA only; not a human judgment.');
    assert(!Object.hasOwn(exported.reviews[1], 'content_equivalence'));
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({path: path.join(qa, 'desktop.png')});
    await page.setViewportSize({width: 390, height: 844});
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile horizontal overflow');
    await page.screenshot({path: path.join(qa, 'mobile.png')});
    assert.deepEqual(errors, []);
    const result = {passed: true, cards: 50, original_texts_verified: 50, rewrite_texts_verified: 100, checks: ['empty initial judgments', 'navigation', 'isolated local persistence', 'JSON export', 'packet hash', 'mobile width', 'no script errors'], user_browser_used: false, human_review_completed: false};
    fs.writeFileSync(path.join(qa, 'QA.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result));
    await context.close();
  } finally {
    await browser.close();
  }
})().catch(e => {console.error(e); process.exitCode = 1;});
