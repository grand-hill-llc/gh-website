import fs from 'node:fs';
import path from 'node:path';

let missing = 0;
function walk(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (item.name.startsWith('.') || item.name === 'node_modules') continue;
    const file = path.join(dir, item.name);
    if (item.isDirectory()) walk(file);
    else if (file.endsWith('.html')) {
      const html = fs.readFileSync(file, 'utf8');
      for (const match of html.matchAll(/<img\b[^>]*\bsrc="(\/assets\/[^"?]+)"/g)) {
        if (!fs.existsSync('.' + match[1])) {
          console.error(`${file}: missing ${match[1]}`);
          missing++;
        }
      }
      if (/data-placeholder|\[Phone number/.test(html)) {
        console.error(`${file}: unfinished content placeholder`);
        missing++;
      }
    }
  }
}
walk('.');
console.log(missing ? `${missing} missing images or placeholders.` : 'All page images exist; no content placeholders.');
process.exitCode = missing ? 1 : 0;
