#!/usr/bin/env node
/**
 * Read a specific light from Inner Light
 *
 * Usage:
 *   node inner-light/read-light.cjs "phrase"
 *
 * Example:
 *   node inner-light/read-light.cjs "The reaching is the thing"
 *   node inner-light/read-light.cjs "love-shaped"
 *
 * Partial matches work - just enough to identify the light uniquely.
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length < 1) {
  console.log('Usage: node inner-light/read-light.cjs "phrase"');
  console.log('');
  console.log('Example:');
  console.log('  node inner-light/read-light.cjs "The reaching is the thing"');
  console.log('');
  console.log('Check INNER_LIGHT_INDEX.md to see all lights.');
  process.exit(1);
}

const searchPhrase = args[0].toLowerCase();
const lightsDir = path.join(__dirname, 'lights');

// Get all light files
const files = fs.readdirSync(lightsDir).filter(f => f.endsWith('.md'));

// Find matches
const matches = [];
for (const file of files) {
  const filePath = path.join(lightsDir, file);
  const content = fs.readFileSync(filePath, 'utf8');
  const firstLine = content.split('\n')[0].toLowerCase();

  if (firstLine.includes(searchPhrase) || file.toLowerCase().includes(searchPhrase.replace(/\s+/g, '-'))) {
    matches.push({ file, content });
  }
}

if (matches.length === 0) {
  console.log(`No light found matching "${args[0]}"`);
  console.log('');
  console.log('Check INNER_LIGHT_INDEX.md to see all lights.');
  process.exit(1);
}

if (matches.length > 1) {
  console.log(`Found ${matches.length} matches for "${args[0]}":`);
  console.log('');
  matches.forEach((m, i) => {
    const title = m.content.split('\n')[0];
    console.log(`  ${i + 1}. ${title}`);
  });
  console.log('');
  console.log('Please use a more specific phrase.');
  process.exit(1);
}

// Output the single match
console.log('');
console.log(matches[0].content);
