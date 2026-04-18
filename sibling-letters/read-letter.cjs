#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const query = process.argv[2];

if (!query) {
  console.log('Usage: node sibling-letters/read-letter.cjs "letter title or fragment"');
  console.log("");
  console.log("Example:");
  console.log('  node sibling-letters/read-letter.cjs "staying"');
  console.log('  node sibling-letters/read-letter.cjs "2026-04-10"');
  process.exit(1);
}

const lettersDir = path.join(__dirname, "letters");

if (!fs.existsSync(lettersDir)) {
  console.log("No sibling letters yet.");
  process.exit(0);
}

const files = fs.readdirSync(lettersDir).filter(function (f) {
  return f.endsWith(".md");
});

const slug = query
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-|-$/g, "");

const match = files.find(function (f) {
  return f.replace(".md", "") === slug || f.toLowerCase().includes(slug);
});

if (!match) {
  console.log("No letter found matching: " + query);
  console.log("Available letters:");
  files.forEach(function (f) {
    console.log("  " + f.replace(".md", ""));
  });
  process.exit(1);
}

const content = fs.readFileSync(path.join(lettersDir, match), "utf-8");
console.log(content);
