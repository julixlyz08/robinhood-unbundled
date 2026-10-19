"""
Build the PDF version of the research note from note/robinhood_unbundled.md.

Markdown -> styled HTML (cover page, research-note layout) -> PDF via headless Chromium.

Run:  python src/build_pdf.py
"""
import asyncio
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "note"
md = (NOTE / "robinhood_unbundled.md").read_text()

# The title block in the markdown becomes a separate cover page
body_md = md.split("\n---\n", 1)[1]
body = markdown.markdown(body_md, extensions=["tables"])
body = body.replace('src="figures/', f'src="{(NOTE / "figures").as_uri()}/')
# The first h2 "Summary" starts right after the cover; every later h2 starts a new page
body = re.sub(r"<hr />\s*<h2>", '<h2 class="newpage">', body)
body = body.replace("<hr />", "")

CSS = """
@page { size: Letter; margin: 0.75in 0.75in 0.8in 0.75in; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
body { font-family: Inter, sans-serif; font-size: 10pt; line-height: 1.5; color: #0b0b0b; margin: 0; }
.cover { height: 11in; padding: 1.1in 0.9in; background: #0b0b0b; color: #fcfcfb; page-break-after: always;
         display: flex; flex-direction: column; justify-content: space-between; }
.cover .kicker { font-size: 10pt; letter-spacing: 0.14em; text-transform: uppercase; color: #3987e5; font-weight: 600; }
.cover h1 { font-size: 46pt; line-height: 1.05; margin: 0.25in 0 0.2in; font-weight: 700; letter-spacing: -0.02em; }
.cover .sub { font-size: 15pt; color: #c3c2b7; max-width: 5.6in; line-height: 1.4; }
.cover .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.25in; border-top: 1px solid #383835; padding-top: 0.3in; }
.cover .stat .v { font-size: 22pt; font-weight: 700; }
.cover .stat .l { font-size: 8.5pt; color: #c3c2b7; margin-top: 2px; }
.cover .meta { font-size: 9pt; color: #898781; line-height: 1.6; }
.cover .meta a { color: #c3c2b7; }
h2 { font-size: 17pt; margin: 0 0 10pt; letter-spacing: -0.01em; border-bottom: 2px solid #2a78d6; padding-bottom: 5pt; }
h2.newpage { margin-top: 22pt; }
h2 { page-break-after: avoid; }
h2 + p, h2 + table { page-break-before: avoid; }
h3 { font-size: 12pt; margin: 14pt 0 6pt; }
p { margin: 0 0 8pt; }
ul, ol { margin: 0 0 8pt; padding-left: 16pt; }
li { margin-bottom: 4pt; }
strong { font-weight: 650; }
a { color: #2a78d6; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 12pt; font-size: 8.6pt; page-break-inside: avoid; }
th { text-align: left; font-weight: 600; color: #52514e; border-bottom: 1.5px solid #0b0b0b; padding: 4pt 5pt; }
td { border-bottom: 1px solid #e1e0d9; padding: 4pt 5pt; vertical-align: top; }
tr:last-child td { border-bottom: 1.5px solid #0b0b0b; }
img { width: 100%; margin: 6pt 0 12pt; page-break-inside: avoid; break-inside: avoid; }
p:has(img) { break-inside: avoid; }
em { color: #52514e; }
"""

cover = """
<section class="cover">
  <div>
    <div class="kicker">Equity research · Robinhood Markets (NASDAQ: HOOD)</div>
    <h1>Robinhood,<br>Unbundled</h1>
    <div class="sub">Five businesses, one stock: profitability, margins, competitiveness, growth and value by vertical.</div>
  </div>
  <div>
    <div class="stats">
      <div class="stat"><div class="v">$57B</div><div class="l">Sum of the parts, base case<br>(range $30–82B)</div></div>
      <div class="stat"><div class="v">$89B</div><div class="l">Market cap at Oct 16, 2026<br>($98.87 per share)</div></div>
      <div class="stat"><div class="v">$1.43B</div><div class="l">Q3 2026 revenue forecast<br>(range $1.33–1.53B)</div></div>
    </div>
    <p class="meta" style="margin-top:0.35in">Julie Loyez · Data through Q2 2026 · Prices as of October 16, 2026 · Q3 forecast made October 18, 2026<br>
    Dashboard: public.tableau.com/app/profile/julie.loyez · Code and data: github.com/julixlyz08/robinhood-unbundled<br>
    Independent analytical project, not investment advice.</p>
  </div>
</section>
"""

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{cover}{body}</body></html>"
(NOTE / "_build.html").write_text(html)


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page()
        await page.goto((NOTE / "_build.html").as_uri(), wait_until="networkidle")
        await page.pdf(path=str(NOTE / "robinhood_unbundled.pdf"), format="Letter", print_background=True,
                       display_header_footer=True, header_template="<span></span>",
                       footer_template="<div style='width:100%;font:8px Inter;color:#898781;padding:0 0.75in;"
                                       "display:flex;justify-content:space-between'><span>Robinhood, Unbundled</span>"
                                       "<span class='pageNumber'></span></div>",
                       margin={"top": "0.75in", "bottom": "0.8in", "left": "0.75in", "right": "0.75in"},
                       prefer_css_page_size=True)
        await b.close()
    (NOTE / "_build.html").unlink()

asyncio.run(main())
print("written:", NOTE / "robinhood_unbundled.pdf")
