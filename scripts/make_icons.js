// Renders the PNG favicons from docs/favicon.svg (ع on a dusk-over-dunes tile, colours from src/app.html).
// Run from the repo root: node scripts/make_icons.js  (uses the pre-installed Playwright Chromium)
// then: convert docs/favicon-16.png docs/favicon-32.png docs/favicon-48.png docs/favicon.ico && rm docs/favicon-16.png docs/favicon-48.png
const {chromium} = require('playwright'); const fs = require('fs');
(async () => {
  const sv = fs.readFileSync('docs/favicon.svg', 'utf8');
  const square = sv.replace('rx="14"', 'rx="0"');   // iOS rounds the corners itself
  const out = [['favicon-16.png', sv, 16], ['favicon-32.png', sv, 32], ['favicon-48.png', sv, 48],
               ['icon-192.png', sv, 192], ['icon-512.png', sv, 512], ['apple-touch-icon.png', square, 180]];
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [name, s, z] of out) {
    await p.setViewportSize({width: z, height: z});
    await p.setContent(`<style>html,body{margin:0;background:transparent}</style><img src="data:image/svg+xml;base64,${Buffer.from(s).toString('base64')}" width=${z} height=${z}>`);
    await p.screenshot({path: 'docs/' + name, omitBackground: true});
  }
  await b.close();
})();
