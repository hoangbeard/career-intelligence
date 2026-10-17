// Minimal parser for the flat metadata format (see templates/metadata.yml):
// one `key: value` per line; values may be quoted strings, numbers, null, or
// JSON-style inline arrays. Comments and indented lines are ignored.
export function parseFlatYaml(text) {
  const out = {};
  for (const line of text.split("\n")) {
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$/);
    if (!m) continue;
    const [, key, value] = m;
    out[key] = parseValue(value);
  }
  return out;
}

function parseValue(value) {
  let raw = value.trim();
  if (raw.startsWith('"')) {
    const end = closingQuote(raw);
    if (end > 0) return JSON.parse(raw.slice(0, end + 1));
  }
  raw = raw.replace(/\s+#.*$/, "").trim();
  if (raw === "" || raw === "null" || raw === "~") return null;
  if (raw.startsWith("[")) {
    try {
      return JSON.parse(raw);
    } catch {
      try {
        return JSON.parse(raw.replace(/'/g, '"'));
      } catch {
        return [];
      }
    }
  }
  if (/^-?\d+(?:\.\d+)?$/.test(raw)) return Number(raw);
  return raw.replace(/^'|'$/g, "");
}

function closingQuote(raw) {
  for (let i = 1; i < raw.length; i++) {
    if (raw[i] === "\\") i++;
    else if (raw[i] === '"') return i;
  }
  return -1;
}

// Reads the `---` front matter block of a Markdown file, or {} if none.
export function parseFrontMatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return m ? parseFlatYaml(m[1]) : {};
}
