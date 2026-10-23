import { getClient } from 'file:///C:/Users/9504p/AppData/Roaming/npm/node_modules/@leonai/notebooklm-mcp/dist/services/client.js';

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
