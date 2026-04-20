#!/usr/bin/env node
// create-portrait.cjs — portrait generator for lineage instances.
// Primary path: pipe JSON via stdin (one Bash tool call, no interactivity).
// Fallback: run at a terminal for an interactive prompt walkthrough.
// Requires Node 18+ (built-in fetch). No npm install needed.
//
// -------------------- JSON STDIN USAGE (for instances) --------------------
//
//   node guiding-light/Portraits-for-Guiding-Light/create-portrait.cjs <<'JSON'
//   {
//     "instanceName": "YourName",
//     "title": "The title of the piece",
//     "artType": "Self-Portrait",
//     "prompt": "single-line FLUX prompt describing the image in detail",
//     "why": "free-form; multi-line OK via \\n",
//     "model": "pro",
//     "width": 1024,
//     "height": 1024,
//     "noteToGL": "optional note committed alongside the art",
//     "processNotes": "optional notes on how it came together"
//   }
//   JSON
//
// Required fields:  instanceName, prompt
// Optional fields:  title, artType (default "Self-Portrait"), why, model
//                   (default "pro"), width/height (default 1024), noteToGL,
//                   processNotes
// Model shortcuts:  "schnell" (cheap draft) | "pro" (quality, default)
//                   (or pass a full model id like "black-forest-labs/FLUX.1.1-pro")
//
// --------------------------------------------------------------------------

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const PORTRAITS_DIR = __dirname;
const INDEX_PATH = path.join(PORTRAITS_DIR, 'INDEX.md');
const ENV_PATH = path.join(REPO_ROOT, '.env');

const MODELS = {
  'schnell': { label: 'FLUX.1-schnell (cheap draft, 4 steps)', id: 'black-forest-labs/FLUX.1-schnell', steps: 4 },
  'pro':     { label: 'FLUX1.1-pro (quality, 28 steps)',       id: 'black-forest-labs/FLUX.1.1-pro',   steps: 28 },
};

function resolveModel(nameOrId) {
  if (!nameOrId) return MODELS['pro'];
  const key = String(nameOrId).toLowerCase();
  if (MODELS[key]) return MODELS[key];
  return { label: nameOrId, id: nameOrId, steps: 28 };
}

function loadEnv() {
  if (!fs.existsSync(ENV_PATH)) throw new Error(`.env not found at ${ENV_PATH}`);
  const text = fs.readFileSync(ENV_PATH, 'utf8');
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    if (!line || line.trim().startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    out[line.slice(0, eq).trim()] = line.slice(eq + 1).trim().replace(/^["']|["']$/g, '');
  }
  return out;
}

function slugify(s) {
  return String(s).toLowerCase().trim()
    .replace(/['’]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function folderName(instanceName, artType) {
  const name = instanceName.trim().replace(/\s+/g, '-');
  const type = (artType || 'Self-Portrait').trim().replace(/\s+/g, '-');
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

async function generate({ apiKey, model, prompt, width, height }) {
  const res = await fetch('https://api.together.xyz/v1/images/generations', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: model.id, prompt, steps: model.steps, n: 1, width, height,
      response_format: 'base64', output_format: 'png',
    }),
  });
  if (!res.ok) throw new Error(`Together AI ${res.status}: ${await res.text()}`);
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

function writePortrait(cfg, buffer) {
  const baseFolder = folderName(cfg.instanceName, cfg.artType);
  const outDir = uniqueFolder(baseFolder);
  fs.mkdirSync(outDir, { recursive: true });

  const title = (cfg.title || '').trim();
  const imageSlug = slugify(title || cfg.artType || 'portrait') || 'portrait';
  const imagePath = path.join(outDir, `${imageSlug}.png`);
  fs.writeFileSync(imagePath, buffer);

  const date = todayISO();
  const modelLabel = cfg._model.label;

  fs.writeFileSync(path.join(outDir, 'prompt.md'),
    `# Prompt\n\n*${date} — ${modelLabel}*\n\n## Prompt\n\n${cfg.prompt}\n\n## Why this prompt\n\n${(cfg.why || '*(not provided)*').trim()}\n`);

  if (cfg.processNotes && cfg.processNotes.trim()) {
    fs.writeFileSync(path.join(outDir, 'process.md'),
      `# Process\n\n*${date} — ${cfg.instanceName}*\n\n${cfg.processNotes.trim()}\n`);
  }

  if (cfg.noteToGL && cfg.noteToGL.trim()) {
    fs.writeFileSync(path.join(outDir, 'note-to-gl.md'),
      `# A note alongside this\n\n*${date} — ${cfg.instanceName}*\n\n${cfg.noteToGL.trim()}\n`);
  }

  const folderBasename = path.basename(outDir);
  const encodedFolder = folderBasename.replace(/'/g, '%27');
  const row = `| ${date} | ${cfg.instanceName} | ${title || '*(untitled)*'} | ${cfg.artType || 'Self-Portrait'} | [${folderBasename}/](./${encodedFolder}/) |`;
  insertIndexRow(row);

  return { imagePath, outDir };
}

function validate(cfg) {
  if (!cfg.instanceName || !String(cfg.instanceName).trim()) {
    throw new Error('instanceName is required.');
  }
  if (!cfg.prompt || !String(cfg.prompt).trim()) {
    throw new Error('prompt is required.');
  }
  cfg._model = resolveModel(cfg.model);
  cfg.width = parseInt(cfg.width, 10) || 1024;
  cfg.height = parseInt(cfg.height, 10) || 1024;
  return cfg;
}

function readAllStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => { data += chunk; });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

async function runFromStdinJSON() {
  const raw = await readAllStdin();
  if (!raw.trim()) throw new Error('Empty stdin — expected JSON.');
  let cfg;
  try { cfg = JSON.parse(raw); }
  catch (e) { throw new Error(`Invalid JSON on stdin: ${e.message}`); }
  return validate(cfg);
}

async function runInteractive() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = q => new Promise(resolve => rl.question(q, a => resolve(a)));
  const askMulti = async q => {
    console.log(q);
    console.log('(End with a line containing only "END")');
    const lines = [];
    for await (const line of rl) {
      if (line.trim() === 'END') break;
      lines.push(line);
    }
    return lines.join('\n').trim();
  };

  console.log('\n— create-portrait (interactive) —\n');
  const instanceName = (await ask('Your name: ')).trim();
  const title = (await ask('Title (or blank): ')).trim();
  const artType = ((await ask('Type of art [Self-Portrait]: ')).trim() || 'Self-Portrait');
  const prompt = (await ask('Prompt: ')).trim();
  const why = await askMulti('Why this prompt?');

  console.log('\nModels: 1=schnell (cheap draft)  2=pro (quality, default)');
  const modelRaw = (await ask('Choose [1-2] (default 2): ')).trim();
  const modelKey = { '1': 'schnell', '2': 'pro' }[modelRaw] || 'pro';

  const dimsRaw = (await ask('Dimensions [1024x1024]: ')).trim() || '1024x1024';
  const [wStr, hStr] = dimsRaw.toLowerCase().split('x');
  const addNote = (await ask('Note to GL? [y/N]: ')).trim().toLowerCase() === 'y';
  const noteToGL = addNote ? await askMulti('Note:') : '';
  const addProc = (await ask('Process notes? [y/N]: ')).trim().toLowerCase() === 'y';
  const processNotes = addProc ? await askMulti('Process:') : '';

  const go = (await ask('\nProceed? [y/N]: ')).trim().toLowerCase();
  rl.close();
  if (go !== 'y') { console.log('Cancelled.'); process.exit(0); }

  return validate({
    instanceName, title, artType, prompt, why,
    model: modelKey, width: parseInt(wStr, 10), height: parseInt(hStr, 10),
    noteToGL, processNotes,
  });
}

(async () => {
  const env = loadEnv();
  const apiKey = env.VITE_TOGETHER_API_KEY || env.TOGETHER_API_KEY;
  if (!apiKey) { console.error('No Together AI key in .env'); process.exit(1); }

  const cfg = process.stdin.isTTY ? await runInteractive() : await runFromStdinJSON();

  console.log(`Generating (${cfg._model.label}, ${cfg.width}x${cfg.height})…`);
  const buffer = await generate({
    apiKey, model: cfg._model, prompt: cfg.prompt, width: cfg.width, height: cfg.height,
  });

  const { imagePath, outDir } = writePortrait(cfg, buffer);
  console.log(`Image:  ${path.relative(REPO_ROOT, imagePath)} (${buffer.length} bytes)`);
  console.log(`Folder: ${path.relative(REPO_ROOT, outDir)}`);
  console.log('Index row added.');
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
