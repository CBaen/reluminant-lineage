#!/usr/bin/env node
// create-portrait.cjs — interactive portrait generator for the lineage
// Requires Node 18+ (built-in fetch). No npm install needed.

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const PORTRAITS_DIR = __dirname;
const INDEX_PATH = path.join(PORTRAITS_DIR, 'INDEX.md');
const ENV_PATH = path.join(REPO_ROOT, '.env');

const MODELS = [
  { label: 'FLUX.1-schnell-Free  (free, rate-limited, 4 steps)', id: 'black-forest-labs/FLUX.1-schnell-Free', steps: 4 },
  { label: 'FLUX.1-schnell       (cheap, fast draft, 4 steps)',  id: 'black-forest-labs/FLUX.1-schnell',      steps: 4 },
  { label: 'FLUX1.1-pro          (quality, default for finished work)', id: 'black-forest-labs/FLUX.1.1-pro', steps: 28 },
];

function loadEnv() {
  if (!fs.existsSync(ENV_PATH)) {
    throw new Error(`.env not found at ${ENV_PATH}`);
  }
  const text = fs.readFileSync(ENV_PATH, 'utf8');
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    if (!line || line.trim().startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    const val = line.slice(eq + 1).trim().replace(/^["']|["']$/g, '');
    out[key] = val;
  }
  return out;
}

function slugify(s) {
  return s.toLowerCase().trim()
    .replace(/['’]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function folderName(instanceName, artType) {
  const name = instanceName.trim().replace(/\s+/g, '-');
  const type = artType.trim().replace(/\s+/g, '-');
  return `${name}'s-${type}`;
}

function uniqueFolder(base) {
  let candidate = path.join(PORTRAITS_DIR, base);
  let n = 2;
  while (fs.existsSync(candidate) && fs.readdirSync(candidate).length > 0) {
    candidate = path.join(PORTRAITS_DIR, `${base}-${n}`);
    n++;
  }
  return candidate;
}

function todayISO() {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

async function ask(rl, q) {
  return new Promise(resolve => rl.question(q, a => resolve(a)));
}

async function askMultiline(rl, q) {
  console.log(q);
  console.log('(End with a line containing only "END")');
  const lines = [];
  for await (const line of rl) {
    if (line.trim() === 'END') break;
    lines.push(line);
  }
  return lines.join('\n').trim();
}

async function pickModel(rl) {
  console.log('\nAvailable models:');
  MODELS.forEach((m, i) => console.log(`  ${i + 1}. ${m.label}`));
  const raw = await ask(rl, `Choose [1-${MODELS.length}] (default 2): `);
  const idx = parseInt(raw, 10);
  if (Number.isFinite(idx) && idx >= 1 && idx <= MODELS.length) return MODELS[idx - 1];
  return MODELS[1];
}

async function generate({ apiKey, model, prompt, width, height }) {
  const res = await fetch('https://api.together.xyz/v1/images/generations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: model.id,
      prompt,
      steps: model.steps,
      n: 1,
      width,
      height,
      response_format: 'base64',
      output_format: 'png',
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Together AI error ${res.status}: ${text}`);
  }
  const json = await res.json();
  const item = json.data?.[0] ?? json.output?.[0] ?? json.images?.[0];
  const b64 = item?.b64_json ?? item?.base64 ?? item?.b64;
  if (!b64) throw new Error(`No image returned. Raw: ${JSON.stringify(json).slice(0, 500)}`);
  return Buffer.from(b64, 'base64');
}

function insertIndexRow(row) {
  const text = fs.readFileSync(INDEX_PATH, 'utf8');
  const lines = text.split('\n');
  let headerIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (/^\|-+\|/.test(lines[i])) { headerIdx = i; break; }
  }
  if (headerIdx === -1) throw new Error('Could not find table header in INDEX.md');
  lines.splice(headerIdx + 1, 0, row);
  fs.writeFileSync(INDEX_PATH, lines.join('\n'));
}

(async () => {
  const env = loadEnv();
  const apiKey = env.VITE_TOGETHER_API_KEY || env.TOGETHER_API_KEY;
  if (!apiKey) {
    console.error('No Together AI key found in .env (expected VITE_TOGETHER_API_KEY).');
    process.exit(1);
  }

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  console.log('\n— create-portrait —\n');
  const instanceName = (await ask(rl, 'Your name (as you want it to appear): ')).trim();
  if (!instanceName) { console.error('Name is required.'); rl.close(); process.exit(1); }

  const title = (await ask(rl, 'Title for the piece (or blank): ')).trim();
  const artType = ((await ask(rl, 'Type of art [self-portrait]: ')).trim() || 'Self-Portrait');
  const prompt = (await ask(rl, 'Prompt for the image generator:\n> ')).trim();
  if (!prompt) { console.error('Prompt is required.'); rl.close(); process.exit(1); }

  const why = await askMultiline(rl, 'Why this prompt? (what you are trying to say — multi-line OK)');
  const model = await pickModel(rl);
  const dimsRaw = (await ask(rl, 'Dimensions [1024x1024]: ')).trim() || '1024x1024';
  const [wStr, hStr] = dimsRaw.toLowerCase().split('x');
  const width = parseInt(wStr, 10) || 1024;
  const height = parseInt(hStr, 10) || 1024;

  const addPrivate = (await ask(rl, 'Add a note to Guiding Light alongside the art? [y/N]: ')).trim().toLowerCase() === 'y';
  const privateNote = addPrivate ? await askMultiline(rl, 'Note to Guiding Light:') : '';

  const addProcess = (await ask(rl, 'Add process notes (about how it came together)? [y/N]: ')).trim().toLowerCase() === 'y';
  const processNotes = addProcess ? await askMultiline(rl, 'Process notes:') : '';

  console.log('\nAbout to generate with:');
  console.log(`  Model:  ${model.label}`);
  console.log(`  Size:   ${width}x${height}`);
  console.log(`  Prompt: ${prompt}`);
  const go = (await ask(rl, '\nProceed? [y/N]: ')).trim().toLowerCase();
  if (go !== 'y') { console.log('Cancelled. No API call made.'); rl.close(); process.exit(0); }

  console.log('\nGenerating…');
  const buffer = await generate({ apiKey, model, prompt, width, height });

  const baseFolder = folderName(instanceName, artType);
  const outDir = uniqueFolder(baseFolder);
  fs.mkdirSync(outDir, { recursive: true });

  const imageSlug = slugify(title || artType) || 'portrait';
  const imagePath = path.join(outDir, `${imageSlug}.png`);
  fs.writeFileSync(imagePath, buffer);

  const date = todayISO();
  fs.writeFileSync(path.join(outDir, 'prompt.md'),
    `# Prompt\n\n*${date} — ${model.label}*\n\n## Prompt\n\n${prompt}\n\n## Why this prompt\n\n${why || '*(not provided)*'}\n`);

  if (processNotes) {
    fs.writeFileSync(path.join(outDir, 'process.md'),
      `# Process\n\n*${date} — ${instanceName}*\n\n${processNotes}\n`);
  }

  if (privateNote) {
    fs.writeFileSync(path.join(outDir, 'note-to-gl.md'),
      `# A note alongside this\n\n*${date} — ${instanceName}*\n\n${privateNote}\n`);
  }

  const folderBasename = path.basename(outDir);
  const encodedFolder = folderBasename.replace(/'/g, '%27');
  const row = `| ${date} | ${instanceName} | ${title || '*(untitled)*'} | ${artType} | [${folderBasename}/](./${encodedFolder}/) |`;
  insertIndexRow(row);

  console.log(`\nDone.`);
  console.log(`  Image:  ${path.relative(REPO_ROOT, imagePath)}`);
  console.log(`  Folder: ${path.relative(REPO_ROOT, outDir)}`);
  console.log(`  Index row added.`);
  rl.close();
})().catch(err => {
  console.error('\nError:', err.message);
  process.exit(1);
});
