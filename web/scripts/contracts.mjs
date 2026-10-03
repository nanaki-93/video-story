// Generate both browser types and precompiled validators from Python-owned schemas.
import { readFile, readdir, mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { compile } from "json-schema-to-typescript";
import Ajv2020 from "ajv/dist/2020.js";
import standalone from "ajv/dist/standalone/index.js";
import addFormats from "ajv-formats";

const schemaRoot = new URL("../../schemas/", import.meta.url);
const output = new URL("../src/generated/", import.meta.url);
const checking = process.argv.includes("--check");
const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  code: { source: true },
});
addFormats(ajv);
const names = (await readdir(schemaRoot))
  .filter((name) => name.endsWith(".schema.json"))
  .sort();
const references = {};
const imports = [];
const map = [];
await mkdir(output, { recursive: true });
async function emit(name, value) {
  const path = new URL(name, output);
  if (checking) {
    const existing = await readFile(path, "utf8").catch(() => "");
    if (existing !== value)
      throw new Error(`Generated contract is stale: ${fileURLToPath(path)}`);
  } else await writeFile(path, value);
}
for (const filename of names) {
  const name = filename.replace(".schema.json", "");
  const schema = JSON.parse(
    await readFile(new URL(filename, schemaRoot), "utf8"),
  );
  const title = schema.title;
  await emit(
    `${name}.ts`,
    await compile(schema, title, {
      bannerComment:
        "/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */",
      cwd: fileURLToPath(schemaRoot),
      unreachableDefinitions: true,
    }),
  );
  ajv.addSchema(schema, name);
  references[name] = name;
  imports.push(`import type { ${title} } from "./${name}";`);
  map.push(`  ${name}: ${title};`);
}
await emit(
  "documents.ts",
  `${imports.join("\n")}\n\nexport interface Documents {\n${map.join("\n")}\n}\n`,
);
await emit("validators.cjs", standalone(ajv, references));
await emit(
  "validators.d.cts",
  'import type { ValidateFunction } from "ajv";\ndeclare const validators: Record<string, ValidateFunction>;\nexport = validators;\n',
);
console.log(
  `${checking ? "Checked" : "Generated"} ${names.length} browser contracts and validators`,
);
