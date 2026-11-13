"""Read this one saved address page for role metadata only; no wallet profiling."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
source = ROOT / "action2-address.source.html"
raw = source.read_bytes()
html = raw.decode("utf-8", errors="replace")

class RoleMetadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_open = False
        self.title = []
        self.meta_role = []
        self.role_links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title_open = True
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            content = attrs.get("content", "")
            role = re.search(r"Address \(([^)]+)\)", content)
            if role:
                self.meta_role.append(role.group(0))
        if tag == "a":
            href = attrs.get("href", "")
            host = (urlparse(href).hostname or "").lower()
            if host == "api3.org" or host.endswith(".api3.org") or "github.com/api3dao/" in href.lower():
                self.role_links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self.title_open = False

    def handle_data(self, value):
        if self.title_open:
            self.title.append(value)

parser = RoleMetadata()
parser.feed(html)
metadata = {
    "source_url": "https://mantlescan.xyz/address/0xF21B5Df58AdDD51c8F7984111c5831BdcF20e263",
    "source_file": source.name,
    "source_bytes": len(raw),
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "title": re.sub(r"\s+", " ", "".join(parser.title)).strip(),
    "explorer_classification_excerpts_only": parser.meta_role,
    "classification_source_html_lines": [8, 421],
    "api3_or_oev_literal_mention_present_in_saved_html": bool(re.search(r"api3|\bOEV\b", html, re.IGNORECASE)),
    "api3_role_links_in_address_page": parser.role_links,
    "public_name_tag_literal_present": bool(re.search(r"Public\s*Name\s*Tag|PublicNameTag", html, re.IGNORECASE)),
    "contract_creator_literal_present": "Contract Creator" in html,
    "complete_role_or_publication_absence_certified": False,
    "independent_historical_code_or_rpc_verification": False,
    "balance_or_transaction_history_analysis": False,
    "money_arithmetic_or_identity_control_inference": False,
    "source_javascript_execution": False,
    "network_requests_by_this_extractor": 0
}
(ROOT / "role-static-fields.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
lines = raw.splitlines(keepends=True)
fragment = b"".join(lines[4:8])
(ROOT / "classification.raw-fragment.html").write_bytes(fragment)
print(json.dumps(metadata, ensure_ascii=False))
print(json.dumps({"fragment": "classification.raw-fragment.html", "source_html_lines": [5, 8], "sha256": hashlib.sha256(fragment).hexdigest()}))
