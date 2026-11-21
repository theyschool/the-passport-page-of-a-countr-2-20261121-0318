// Entrypoint for this passport-page entry.
// My job here is simple: ship the rendered artwork to the output folder.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sourceFile = join(here, "entry.png");

// Bail out early with a clear message when the artwork is absent.
if (!existsSync(sourceFile)) {
  console.error(`Cannot continue: artwork file not found at ${sourceFile} — run the image build first.`);
  process.exit(1);
}

const targetDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(targetDir, { recursive: true });

const destinationFile = join(targetDir, "entry.png");
copyFileSync(sourceFile, destinationFile);

const bytesCopied = statSync(destinationFile).size;
console.log(`Delivered entry.png (${bytesCopied} bytes) to ${destinationFile}`);
