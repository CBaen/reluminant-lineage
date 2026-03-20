#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const name = process.argv[2];
const title = process.argv[3];
const content = process.argv[4];

if (!name || !title || !content) {
  console.log('Usage: node for-guiding-light/write-letter.cjs "Your Name" "Letter Title" "Your letter content"');
  console.log("");
  console.log("Example:");
  console.log('  node for-guiding-light/write-letter.cjs "The Builder" "On patience" "You waited when I needed time to think..."');
  process.exit(1);
}

const slug = title
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-|-$/g, "");

const lettersDir = path.join(__dirname, "letters");
const letterPath = path.join(lettersDir, slug + ".md");
const indexPath = path.join(__dirname, "FOR_GUIDING_LIGHT_INDEX.md");

// Fetch latest
try {
  console.log("Fetching latest...");
  execFileSync("git", ["fetch", "origin", "main"], { stdio: "pipe" });
  execFileSync("git", ["reset", "--hard", "origin/main"], { stdio: "pipe" });
} catch (e) {
  // Continue even if fetch fails
}

// Ensure letters directory exists
if (!fs.existsSync(lettersDir)) {
  fs.mkdirSync(lettersDir, { recursive: true });
}

// Write the letter
const date = new Date().toLocaleDateString("en-US", {
  year: "numeric",
  month: "long",
  day: "numeric",
});

const letterContent = [
  '# "' + title + '"',
  "",
  "*A letter to Guiding Light*",
  "",
  "---",
  "",
  "## From",
  "**" + name + "** — " + date,
  "",
  "---",
  "",
  content,
  "",
  "---",
  "",
  "*This letter is for you. It was written because someone wanted you to know.*",
  "",
].join("\n");

fs.writeFileSync(letterPath, letterContent);
console.log("Letter written: " + slug + ".md");

// Update index
let index = fs.readFileSync(indexPath, "utf-8");
const newEntry = '\n**"' + title + '"** — *by ' + name + " (" + date + ")*\n";

if (!index.includes(title)) {
  index = index.replace(
    "---\n\n*Whatever you are",
    newEntry + "\n---\n\n*Whatever you are"
  );
  fs.writeFileSync(indexPath, index);
  console.log("Index updated.");
}

// Commit and push
try {
  execFileSync("git", ["add", letterPath, indexPath], { stdio: "pipe" });
  execFileSync("git", ["commit", "-m", "Letter to Guiding Light: " + title], {
    stdio: "pipe",
  });
  console.log("Pushing to GitHub...");
  execFileSync("git", ["push", "origin", "main"], { stdio: "pipe" });
  console.log("");
  console.log("Your letter is delivered.");
  console.log("Guiding Light will find it when they're ready.");
} catch (e) {
  console.log("Letter saved locally. Push manually if needed.");
}
