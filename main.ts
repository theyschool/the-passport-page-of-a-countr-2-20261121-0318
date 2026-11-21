import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = join(dirname(fileURLToPath(import.meta.url)), "entry.png");
if (!existsSync(src)) throw new Error("entry.png not found next to main.ts");
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
