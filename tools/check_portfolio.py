"""Validate safe public portfolio documents and their offline demo."""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.has_rtl=False
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if "id" in data:self.ids.add(data["id"])
        if tag=="html" and data.get("dir")=="rtl":self.has_rtl=True
fail=[]
for name in ("README.md","CASE_STUDY.md","ARCHITECTURE.md","ROADMAP.md"):
    p=ROOT/name
    if not p.is_file():fail.append(f"missing {name}");continue
    s=p.read_text(encoding="utf-8")
    if len(s)<300:fail.append(f"short {name}")
    for ref in re.findall(r"\]\(([^)]+)\)",s):
        href=ref.split("#")[0]
        if href and not href.startswith(("https://","http://","mailto:")) and not (p.parent/href).is_file():
            fail.append(f"broken link: {name} {href}")
demo=ROOT/"demo/index.html"
if not demo.is_file():fail.append("missing demo/index.html")
else:
    data=demo.read_text(encoding="utf-8")
    parser=Inspector();parser.feed(data)
    if not parser.has_rtl:fail.append("demo lacks RTL")
    if "ساختگی" not in data or "offline" not in data.lower():fail.append("demo must be explicitly synthetic")
    for bad in ("fetch(", "XMLHttpRequest(", "WebSocket(", "localStorage.", "https://api."):
        if bad in data:fail.append(f"demo must remain offline: {bad}")
    for match in re.findall(r"getElementById\('([^']+)'\)",data):
        if match not in parser.ids:fail.append("missing HTML id: "+match)
if fail:
    for issue in fail:print("FAIL:",issue,file=sys.stderr)
    sys.exit(1)
print("PASS: documents, links, synthetic offline demo, RTL and DOM references")
