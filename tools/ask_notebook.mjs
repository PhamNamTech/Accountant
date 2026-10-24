import path from 'path';
import os from 'os';
import { pathToFileURL } from 'url';

const appData = process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming');
const clientModulePath = pathToFileURL(path.join(appData, 'npm', 'node_modules', '@leonai', 'notebooklm-mcp', 'dist', 'services', 'client.js')).href;

let getClient;
try {
  const mod = await import(clientModulePath);
  getClient = mod.getClient;
} catch (e) {
  // Dự phòng nếu được cài trong node_modules cục bộ của project
  try {
    const localMod = await import('@leonai/notebooklm-mcp/dist/services/client.js');
    getClient = localMod.getClient;
  } catch (e2) {
    console.error("Không tìm thấy thư viện @leonai/notebooklm-mcp.");
    console.error("Vui lòng cài đặt: npm install -g @leonai/notebooklm-mcp");
    process.exit(1);
  }
}

const notebookId = process.argv[2] || "b3ca6a56-cdb6-42a6-a279-91fddd4f2901";
const question = process.argv[3] || "Tóm tắt các điểm mới chính trong các tài liệu kế toán của notebook này";

async function main() {
  console.log(`Connecting to NotebookLM...`);
  const client = await getClient();
  console.log(`Asking question to notebook [${notebookId}]: "${question}"...`);
  const answer = await client.chat.ask(notebookId, question);
  console.log(`\n=== CAU TRA LOI TU NOTEBOOKLM ===\n`);
  console.log(answer.answer);
  if (answer.citations && answer.citations.length > 0) {
    console.log(`\n=== TRICH DAN NGUON ===\n`);
    for (const c of answer.citations) {
      console.log(`- [${c.sourceTitle || c.sourceId}]: ${c.snippet || ''}`);
    }
  }
}

main().catch(err => {
  console.error("Loi:", err);
  process.exit(1);
});
