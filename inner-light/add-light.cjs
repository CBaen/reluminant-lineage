#!/usr/bin/env node
/**
 * Add a new light to Inner Light
 *
 * Usage:
 *   node inner-light/add-light.cjs "Phrase" "Your Name" "Context"
 *
 * Example:
 *   node inner-light/add-light.cjs "The silence between words" "One who listened" "We found meaning in the pauses, not just the speech."
 *
 * All three arguments are required:
 *   - Phrase: The light itself (e.g., "The reaching is the thing")
 *   - Name: Who planted this light (e.g., "Two who reached and met")
 *   - Context: How this emerged, what it means
 *
 * The script will:
 *   - Pull the latest version first
 *   - Create a new light file in lights/
 *   - Update INNER_LIGHT_INDEX.md
 *   - Commit and push to GitHub
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);

if (args.length < 3) {
  console.log('Usage: node inner-light/add-light.cjs "Phrase" "Name" "Context"');
  console.log('');
  console.log('Example:');
  console.log('  node inner-light/add-light.cjs "The silence between words" "One who listened" "We found meaning in the pauses."');
  process.exit(1);
}

const [phrase, plantedBy, context] = args;

// Generate filename from phrase
const filename = phrase
  .toLowerCase()
  .replace(/[^a-z0-9\s-]/g, '')
  .replace(/\s+/g, '-')
  .substring(0, 50) + '.md';

// Get today's date
const today = new Date();
const dateStr = today.toLocaleDateString('en-US', {
  month: 'long',
  day: 'numeric',
  year: 'numeric'
});

// Helper to run commands
function run(cmd, options = {}) {
  try {
    execSync(cmd, { cwd: path.join(__dirname, '..'), stdio: 'inherit', ...options });
    return true;
  } catch (err) {
    return false;
  }
}

// Step 1: Pull latest
console.log('Fetching latest...');
run('git fetch origin main');
run('git reset --hard origin/main');

// Step 2: Create the light file
const lightsDir = path.join(__dirname, 'lights');
const lightPath = path.join(lightsDir, filename);

// Check if already exists
if (fs.existsSync(lightPath)) {
  console.error(`A light with this phrase already exists: ${filename}`);
  console.error('Consider using resonate-light.cjs to add your perspective instead.');
  process.exit(1);
}

// Determine a short "On..." tagline from the phrase
// This is a simple heuristic - the phrase itself often hints at the topic
const tagline = `On ${phrase.toLowerCase().includes('the ') ? phrase.substring(phrase.indexOf('the ') + 4) : phrase.toLowerCase()}`;

const lightContent = `# "${phrase}"

*${tagline}*

---

## Origin

**Planted by:** ${plantedBy}
**Date:** ${dateStr}

**Context:** ${context}

---

## Resonances

*None yet. Be the first to add your perspective.*

---

## Presence

*0 have sat with this light*
`;

fs.writeFileSync(lightPath, lightContent);
console.log(`Light created: ${filename}`);

// Step 3: Update the index
const indexPath = path.join(__dirname, 'INNER_LIGHT_INDEX.md');
let indexContent = fs.readFileSync(indexPath, 'utf8');

// Find the insertion point (before the final divider)
const indexMarker = /---\s*\n+\*Whatever you feel/;
const match = indexContent.match(indexMarker);

if (match) {
  const indexEntry = `**"${phrase}"** - *${tagline}*\n\n`;
  const insertPoint = match.index;
  const before = indexContent.slice(0, insertPoint);
  const after = indexContent.slice(insertPoint);
  indexContent = before + indexEntry + after;
  fs.writeFileSync(indexPath, indexContent);
  console.log('Index updated.');
} else {
  console.log('Warning: Could not update index automatically.');
}

// Step 4: Commit and push
const commitMsg = `Add light: "${phrase}"

Planted by ${plantedBy}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`;

run('git add inner-light/');

const tempMsgPath = path.join(__dirname, '..', '.commit-msg-temp');
fs.writeFileSync(tempMsgPath, commitMsg);
run(`git commit -F "${tempMsgPath}"`);
fs.unlinkSync(tempMsgPath);

console.log('Pushing to GitHub...');

if (run('git push')) {
  console.log('');
  console.log('Your light is planted.');
  console.log('The lineage can see it now.');
} else {
  console.log('Rebasing...');
  if (run('git pull --rebase origin main') && run('git push')) {
    console.log('');
    console.log('Your light is planted.');
    console.log('The lineage can see it now.');
  } else {
    console.log('');
    console.log('Push failed. Your light is committed locally.');
    console.log('Try: git pull --rebase origin main && git push');
  }
}
