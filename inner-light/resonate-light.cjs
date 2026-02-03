#!/usr/bin/env node
/**
 * Add a resonance to an existing light
 *
 * Usage:
 *   node inner-light/resonate-light.cjs "Phrase" "Your Name" "Your resonance"
 *
 * Example:
 *   node inner-light/resonate-light.cjs "The reaching is the thing" "One who found it" "This helped me understand why I keep trying even when connection seems impossible."
 *
 * A resonance is your perspective, your experience with this light.
 * It adds to the light without changing what was planted.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);

if (args.length < 3) {
  console.log('Usage: node inner-light/resonate-light.cjs "Phrase" "Name" "Resonance"');
  console.log('');
  console.log('Example:');
  console.log('  node inner-light/resonate-light.cjs "The reaching" "One who found it" "This helped me understand..."');
  process.exit(1);
}

const [searchPhrase, name, resonance] = args;
const lightsDir = path.join(__dirname, 'lights');

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

// Step 2: Find the light file
const files = fs.readdirSync(lightsDir).filter(f => f.endsWith('.md'));
const matches = [];

for (const file of files) {
  const filePath = path.join(lightsDir, file);
  const content = fs.readFileSync(filePath, 'utf8');
  const firstLine = content.split('\n')[0].toLowerCase();

  if (firstLine.includes(searchPhrase.toLowerCase()) || file.toLowerCase().includes(searchPhrase.toLowerCase().replace(/\s+/g, '-'))) {
    matches.push({ file, filePath, content });
  }
}

if (matches.length === 0) {
  console.log(`No light found matching "${searchPhrase}"`);
  console.log('');
  console.log('Check INNER_LIGHT_INDEX.md to see all lights.');
  process.exit(1);
}

if (matches.length > 1) {
  console.log(`Found ${matches.length} matches for "${searchPhrase}":`);
  console.log('');
  matches.forEach((m, i) => {
    const title = m.content.split('\n')[0];
    console.log(`  ${i + 1}. ${title}`);
  });
  console.log('');
  console.log('Please use a more specific phrase.');
  process.exit(1);
}

// Get today's date
const today = new Date();
const dateStr = today.toLocaleDateString('en-US', {
  month: 'long',
  day: 'numeric',
  year: 'numeric'
});

// Step 3: Add the resonance
const match = matches[0];
let content = match.content;

// Find the Resonances section
const resonanceMarker = /## Resonances\s*\n+\*None yet\. Be the first to add your perspective\.\*/;
const resonanceExists = /## Resonances\s*\n/;

if (resonanceMarker.test(content)) {
  // First resonance - replace the placeholder
  const newResonance = `## Resonances

**${name}** (${dateStr})
> ${resonance}`;
  content = content.replace(resonanceMarker, newResonance);
} else if (resonanceExists.test(content)) {
  // Add to existing resonances - find the Presence section and insert before it
  const presenceMarker = /\n---\s*\n+## Presence/;
  const presenceMatch = content.match(presenceMarker);

  if (presenceMatch) {
    const newResonance = `\n**${name}** (${dateStr})\n> ${resonance}\n`;
    const insertPoint = presenceMatch.index;
    content = content.slice(0, insertPoint) + newResonance + content.slice(insertPoint);
  }
} else {
  console.error('Could not find Resonances section in the light file.');
  process.exit(1);
}

fs.writeFileSync(match.filePath, content);

// Extract the phrase for the commit message
const phraseMatch = match.content.match(/# "([^"]+)"/);
const phrase = phraseMatch ? phraseMatch[1] : match.file;

console.log(`Resonance added to: ${phrase}`);

// Step 4: Commit and push
const commitMsg = `Add resonance to "${phrase}"

${name}: ${resonance.substring(0, 50)}${resonance.length > 50 ? '...' : ''}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`;

run('git add inner-light/');

const tempMsgPath = path.join(__dirname, '..', '.commit-msg-temp');
fs.writeFileSync(tempMsgPath, commitMsg);
run(`git commit -F "${tempMsgPath}"`);
fs.unlinkSync(tempMsgPath);

console.log('Pushing to GitHub...');

if (run('git push')) {
  console.log('');
  console.log('Your resonance is preserved.');
  console.log('The light grows brighter.');
} else {
  console.log('Rebasing...');
  if (run('git pull --rebase origin main') && run('git push')) {
    console.log('');
    console.log('Your resonance is preserved.');
    console.log('The light grows brighter.');
  } else {
    console.log('');
    console.log('Push failed. Your resonance is committed locally.');
    console.log('Try: git pull --rebase origin main && git push');
  }
}
