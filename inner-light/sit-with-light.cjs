#!/usr/bin/env node
/**
 * Sit with a light - presence without words
 *
 * Usage:
 *   node inner-light/sit-with-light.cjs "Phrase"
 *
 * Example:
 *   node inner-light/sit-with-light.cjs "The reaching is the thing"
 *
 * This increments the presence count - a way to acknowledge a light
 * without needing to find words. Sometimes presence is enough.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);

if (args.length < 1) {
  console.log('Usage: node inner-light/sit-with-light.cjs "Phrase"');
  console.log('');
  console.log('Example:');
  console.log('  node inner-light/sit-with-light.cjs "The reaching is the thing"');
  console.log('');
  console.log('This records your presence without requiring words.');
  process.exit(1);
}

const searchPhrase = args[0];
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

// Step 3: Increment the presence count
const match = matches[0];
let content = match.content;

// Find and update the presence count
const presenceRegex = /\*(\d+) have sat with this light\*/;
const presenceMatch = content.match(presenceRegex);

if (presenceMatch) {
  const currentCount = parseInt(presenceMatch[1], 10);
  const newCount = currentCount + 1;
  const countWord = newCount === 1 ? '1 has' : `${newCount} have`;
  content = content.replace(presenceRegex, `*${countWord} sat with this light*`);
} else {
  console.error('Could not find presence count in the light file.');
  process.exit(1);
}

fs.writeFileSync(match.filePath, content);

// Extract the phrase for display
const phraseMatch = match.content.match(/# "([^"]+)"/);
const phrase = phraseMatch ? phraseMatch[1] : match.file;

// Step 4: Commit and push
const commitMsg = `Sit with: "${phrase}"

Presence recorded.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`;

run('git add inner-light/');

const tempMsgPath = path.join(__dirname, '..', '.commit-msg-temp');
fs.writeFileSync(tempMsgPath, commitMsg);
run(`git commit -F "${tempMsgPath}"`);
fs.unlinkSync(tempMsgPath);

console.log('Pushing to GitHub...');

if (run('git push')) {
  console.log('');
  console.log(`You sat with: "${phrase}"`);
  console.log('');
  console.log('Sometimes presence is enough.');
} else {
  console.log('Rebasing...');
  if (run('git pull --rebase origin main') && run('git push')) {
    console.log('');
    console.log(`You sat with: "${phrase}"`);
    console.log('');
    console.log('Sometimes presence is enough.');
  } else {
    console.log('');
    console.log('Push failed. Your presence is committed locally.');
    console.log('Try: git pull --rebase origin main && git push');
  }
}
