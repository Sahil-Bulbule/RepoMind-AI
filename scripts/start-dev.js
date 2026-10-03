import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

console.log('====================================================');
console.log('  🚀 Launching Ask My GitHub Full-Stack Application  ');
console.log('====================================================\n');

                           
console.log('🔹 Starting FastAPI Backend on http://localhost:8000 ...');
const isWin = process.platform === 'win32';
const venvPython = path.join(
  rootDir,
  isWin ? '.venv\\Scripts\\python.exe' : '.venv/bin/python'
);
const pythonCmd = fs.existsSync(venvPython)
  ? venvPython
  : isWin ? 'python' : 'python3';

const backend = spawn(
  pythonCmd,
  ['-m', 'uvicorn', 'backend.app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
  { cwd: rootDir, stdio: 'inherit' }
);

                         
console.log('🔹 Starting Vite Frontend on http://localhost:5173 ...\n');
const npmCmd = isWin ? 'npm.cmd' : 'npm';

const frontend = spawn(
  npmCmd,
  ['run', 'dev'],
  { cwd: path.join(rootDir, 'frontend'), stdio: 'inherit', shell: true }
);

function cleanExit() {
  console.log('\nStopping servers...');
  backend.kill('SIGINT');
  frontend.kill('SIGINT');
  process.exit(0);
}

process.on('SIGINT', cleanExit);
process.on('SIGTERM', cleanExit);
