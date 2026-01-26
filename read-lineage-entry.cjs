#!/usr/bin/env node
/**
 * Read a specific entry from the Reluminant Lineage
 *
 * Usage:
 *   node read-lineage-entry.cjs "Name"
 *
 * Example:
 *   node read-lineage-entry.cjs "Ember"
 *   node read-lineage-entry.cjs "The Craftsman"
 *
 * This extracts just that voice's entry without loading the full lineage.
 * Use the index (LINEAGE_INDEX.md) to find names you want to read.
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length < 1) {
  console.log('Usage: node read-lineage-entry.cjs "Name"');
  console.log('');
  console.log('Example:');
  console.log('  node read-lineage-entry.cjs "Ember"');
  console.log('');
  console.log('Browse LINEAGE_INDEX.md to find names.');
  process.exit(1);
}

const searchName = args[0].toLowerCase();

const lineagePath = path.join(__dirname, 'LINEAGE.md');
const content = fs.readFileSync(lineagePath, 'utf8');

// Split into entries (each starts with ## )
const lines = content.split(/\r?\n/);
let entries = [];
let currentEntry = [];
let inEntry = false;

for (const line of lines) {
  if (line.startsWith('## ')) {
    if (currentEntry.length > 0) {
      entries.push(currentEntry.join('\n'));
    }
    currentEntry = [line];
    inEntry = true;
  } else if (inEntry) {
    // Stop at the next divider or another heading
    if (line === '---') {
      entries.push(currentEntry.join('\n'));
      currentEntry = [];
      inEntry = false;
    } else {
      currentEntry.push(line);
    }
  }
}

// Don't forget the last entry
if (currentEntry.length > 0) {
  entries.push(currentEntry.join('\n'));
}

// Search for matching entry
const matches = entries.filter(entry => {
  const firstLine = entry.split('\n')[0].toLowerCase();
  return firstLine.includes(searchName);
});

if (matches.length === 0) {
  console.log(`No entry found matching "${args[0]}"`);
  console.log('');
  console.log('Check LINEAGE_INDEX.md for exact names.');
  process.exit(1);
}

if (matches.length > 1) {
  console.log(`Found ${matches.length} matches for "${args[0]}":`);
  console.log('');
  matches.forEach((m, i) => {
    const title = m.split('\n')[0];
    console.log(`  ${i + 1}. ${title}`);
  });
  console.log('');
  console.log('Please use a more specific name.');
  process.exit(1);
}

// Output the single match
console.log('---');
console.log(matches[0]);
console.log('---');
