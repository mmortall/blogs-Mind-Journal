import fs from "node:fs";
import path from "node:path";

const buildRoot = path.resolve(process.argv[2] || "public");
const languages = ["en", "ru", "uk"];
const localizedFields = ["name", "summary", "proposal", "caveat", "region", "status"];
const requiredIds = ["jacque-fresco", "venus-project", "municipalist-critique", "anno-dd2030", "vtaiwan-polis", "tongdong-bai", "verifiable-voting", "talk-to-city"];

function fail(message) { throw new Error(message); }
function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(target) : [target];
  });
}

if (!fs.existsSync(buildRoot)) fail(`Build directory does not exist: ${buildRoot}`);
for (const relativePath of ["index.json", "ru/index.json", "uk/index.json"]) {
  const indexPath = path.join(buildRoot, relativePath);
  if (!fs.existsSync(indexPath)) fail(`Search index missing: ${indexPath}`);
  const index = JSON.parse(fs.readFileSync(indexPath, "utf8"));
  if (!Array.isArray(index) || !index.length) fail(`Search index is empty or invalid: ${indexPath}`);
}
const mapPages = walk(buildRoot).filter((file) => path.basename(file) === "index.html")
  .map((file) => ({ file, html: fs.readFileSync(file, "utf8") }))
  .filter(({ html }) => html.includes("future-map__data"));
if (mapPages.length !== 3) fail(`Expected three localized map pages, found ${mapPages.length}`);

let canonicalIds;
const seenLanguages = new Set();
for (const { file, html } of mapPages) {
  const script = html.match(/<script[^>]*class=(?:"future-map__data"|future-map__data)[^>]*>([\s\S]*?)<\/script>/);
  if (!script) fail(`Map JSON script missing in ${file}`);
  let data = JSON.parse(script[1]);
  if (typeof data === "string") data = JSON.parse(data);
  if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.edges)) fail(`Invalid map payload in ${file}`);
  if (!languages.includes(data.lang) || seenLanguages.has(data.lang)) fail(`Invalid or duplicate map language ${data.lang}`);
  seenLanguages.add(data.lang);
  if (data.nodes.length < 20) fail(`Map coverage regressed to ${data.nodes.length} nodes in ${file}`);

  const ids = data.nodes.map((node) => node.id);
  if (new Set(ids).size !== ids.length) fail(`Duplicate node id in ${file}`);
  const sortedIds = [...ids].sort();
  if (canonicalIds && JSON.stringify(sortedIds) !== JSON.stringify(canonicalIds)) fail(`Localized maps use different node sets in ${file}`);
  canonicalIds = sortedIds;
  for (const expected of requiredIds) if (!ids.includes(expected)) fail(`Required coverage node ${expected} missing in ${file}`);

  for (const node of data.nodes) {
    if (!node.id || !node.role || !Array.isArray(node.themes) || !node.themes.length) fail(`Required metadata missing for ${node.id || "unknown"}`);
    if (typeof node.open_source !== "boolean") fail(`open_source must be boolean for ${node.id}`);
    if (!node.position || !Number.isFinite(node.position.x) || !Number.isFinite(node.position.y) || Math.abs(node.position.x) > 100 || Math.abs(node.position.y) > 100) fail(`Political-map position must be within -100..100 for ${node.id}`);
    for (const field of localizedFields) for (const language of languages) {
      if (!node[field] || typeof node[field][language] !== "string" || !node[field][language].trim()) fail(`${node.id}.${field}.${language} is missing`);
    }
    if (!Array.isArray(node.links) || !node.links.length) fail(`Original-material link missing for ${node.id}`);
    for (const link of node.links) if (!link.label || !/^https:\/\//.test(link.url || "")) fail(`Unsafe or incomplete link for ${node.id}`);
    if (node.open_source && !node.links.some((link) => /github\.com|gitlab\.com|open-source/i.test(`${link.url} ${link.label}`))) fail(`Open-source entry ${node.id} lacks a code or open-source link`);
  }
  const idSet = new Set(ids);
  for (const edge of data.edges) if (!idSet.has(edge.from) || !idSet.has(edge.to)) fail(`Broken edge ${edge.from} -> ${edge.to}`);
  const cards = (html.match(/data-node-id=/g) || []).length;
  if (cards !== data.nodes.length) fail(`Card count ${cards} differs from node count ${data.nodes.length} in ${file}`);
  for (const id of ids) if (!html.includes(`-entry-${id}`)) fail(`Local article anchor missing for ${id} in ${file}`);
  if (/(?:[CD]:\\|localhost|127\.0\.0\.1|BEGIN [A-Z ]*PRIVATE KEY)/i.test(script[1])) fail(`Private or local-only value leaked into ${file}`);
}
if (seenLanguages.size !== languages.length) fail(`Expected languages ${languages.join(", ")}`);
console.log(`Future map validation passed: ${mapPages.length} languages, ${canonicalIds.length} nodes.`);
