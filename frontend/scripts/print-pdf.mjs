// Print an HTML report to A4 PDF with Chromium. Usage: node scripts/print-pdf.mjs <input.html> <output.pdf> [footer text]
import { chromium } from "playwright";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [input, output, footer = ""] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(resolve(input)).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const fonts = await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").map((f) => f.family));
const broken = await page.evaluate(() => [...document.images].filter((i) => !i.naturalWidth).map((i) => i.src));
await page.pdf({
  path: resolve(output), format: "A4", printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: `<div style="width:100%;padding:0 15mm;font:7.5pt sans-serif;color:#7b8a95;display:flex;justify-content:space-between"><span>${footer}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
});
console.log("fonts loaded:", [...new Set(fonts)].join(", ") || "NONE");
console.log("broken images:", broken.length ? broken : "none");
await browser.close();
