import { chromium } from "playwright";
import { join } from "path";
import { homedir } from "os";
import { writeFileSync, mkdirSync } from "fs";

const sessionDir = join(homedir(), ".notebooklm");
mkdirSync(sessionDir, { recursive: true });

console.log("Dang mo Google Chrome that de dang nhap Google...");
console.log("Vui long dang nhap tren cua so Chrome vua hien len.");

const context = await chromium.launchPersistentContext(join(sessionDir, ".auth_profile"), {
  headless: false,
  channel: "chrome",
  args: ["--disable-blink-features=AutomationControlled"]
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://notebooklm.google.com/");

await page.waitForURL((url) => {
  return url.hostname === "notebooklm.google.com" && !url.pathname.includes("/login");
}, { timeout: 0 });

console.log("Xac nhan dang nhap thanh cong, dang lay token...");
await page.goto("https://accounts.google.com/", { waitUntil: "load" });
await page.goto("https://notebooklm.google.com/", { waitUntil: "load" });

const storageState = await context.storageState();
const sessionFile = join(sessionDir, "session.json");
writeFileSync(sessionFile, JSON.stringify(storageState, null, 2));

console.log("\n>>> DANG NHAP THANH CONG! <<<");
console.log(`Phien dang nhap da duoc luu tai: ${sessionFile}`);
await context.close();
process.exit(0);
