// Print a 1440x810 slide deck (HTML) to PDF. Usage: node scripts/print-deck.mjs <input.html> <output.pdf>
import { chromium } from "playwright";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [input, output] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 810 } });
await page.goto(pathToFileURL(resolve(input)).href, { waitUntil: "load" });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);
const broken = await page.evaluate(() => [...document.images].filter((i) => !i.naturalWidth).map((i) => i.src));
const overflow = await page.evaluate(() => [...document.querySelectorAll(".slide")].map((s, i) => [i + 1, s.scrollHeight - s.clientHeight]).filter(([, d]) => d > 1));
await page.pdf({ path: resolve(output), width: "1440px", height: "810px", printBackground: true, pageRanges: "" });
console.log("fonts:", [...new Set(await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").map((f) => f.family)))].join(", ") || "NONE");
console.log("broken images:", broken.length ? broken : "none", "| slides overflowing:", overflow.length ? JSON.stringify(overflow) : "none");
await browser.close();
