import fs from "node:fs";
import path from "node:path";

const buildRoot = path.resolve(process.argv[2] || "public");
const pages = [
  { language: "en", file: "index.html", title: "Future design network map", featuredHeading: "Featured posts" },
  { language: "ru", file: "ru/index.html", title: "Карта проектирования будущего", featuredHeading: "Избранные записи" },
  { language: "uk", file: "uk/index.html", title: "Мапа проєктування майбутнього", featuredHeading: "Вибрані дописи" }
];

function fail(message) { throw new Error(message); }
function attr(value) { return `(?:"${value}"|'${value}'|${value})`; }

if (!fs.existsSync(buildRoot)) fail(`Build directory does not exist: ${buildRoot}`);
for (const page of pages) {
  const file = path.join(buildRoot, page.file);
  if (!fs.existsSync(file)) fail(`Homepage missing for ${page.language}: ${file}`);
  const html = fs.readFileSync(file, "utf8");
  const firstPost = new RegExp(
    `<ul\\b[^>]*\\bid=${attr("posts")}\\b[^>]*>[\\s\\S]*?<li\\b[^>]*class=${attr("post_item")}\\b[\\s\\S]*?<h3\\b[^>]*class=${attr("post_link")}\\b[^>]*>[\\s\\S]*?<a\\b[^>]*>([^<]+)<\\/a>`, "i"
  ).exec(html);
  if (!firstPost) fail(`Homepage post list is missing for ${page.language}`);
  if (firstPost[1].trim() !== page.title) fail(`Map is not the first homepage post for ${page.language}: ${firstPost[1].trim()}`);

  const featured = new RegExp(
    `<h2\\b[^>]*class=${attr("mt-4")}\\b>${page.featuredHeading}<\\/h2><ul>([\\s\\S]*?)<\\/ul>`, "i"
  ).exec(html);
  if (!featured) fail(`Featured-post section is missing for ${page.language}`);
  const titles = [...featured[1].matchAll(/<a\b[^>]*>([^<]+)<\/a>/gi)].map((match) => match[1].trim());
  if (titles.length !== 1 || titles[0] !== page.title) fail(`Expected only map in featured posts for ${page.language}, found: ${titles.join(", ")}`);
}

console.log(`Featured post validation passed: map is first and sole featured post in ${pages.length} languages.`);
