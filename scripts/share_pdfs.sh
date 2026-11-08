#!/bin/sh
# share/*.md -> share/*.pdf (pandoc -> standalone HTML -> headless Chrome)
cd "$(dirname "$0")/../share" || exit 1
CSS='body{font-family:system-ui,sans-serif;max-width:760px;margin:24px auto;font-size:11pt;line-height:1.45;color:#1a1a1a}
blockquote{margin:6px 0;padding:6px 12px;background:#f3f4f6;border-left:3px solid #2a78d6;color:#1a1a1a}
code{font-size:9.5pt;background:#f3f4f6;padding:1px 3px}table{border-collapse:collapse;font-size:9.5pt}
td,th{border:1px solid #ccc;padding:4px 6px;vertical-align:top}h1{font-size:18pt}h2{font-size:14pt;margin-top:22px}
h3{font-size:12pt}li{margin:3px 0}img{max-width:100%}@page{margin:16mm}'
for f in board_posts README; do
  pandoc "$f.md" -s --metadata title=" " -o "${TMPDIR:-/tmp}/share_$f.html" -V "header-includes=<style>$CSS</style>"
  google-chrome --headless=new --no-pdf-header-footer --print-to-pdf="$PWD/$f.pdf" "file://${TMPDIR:-/tmp}/share_$f.html" 2>/dev/null
done
ls -la *.pdf
