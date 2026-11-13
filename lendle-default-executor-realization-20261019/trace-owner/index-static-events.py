"""Index this one saved explorer HTML/text. No financial arithmetic or network."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "api3-oev-public-income-boundary-20261019" / "receipt-owner"
html_path = SOURCE / "action2-mantlescan.source.html"
text_path = SOURCE / "action2-mantlescan.static-text.txt"
html = html_path.read_bytes()
text_raw = text_path.read_bytes()
assert hashlib.sha256(html).hexdigest() == "b0174b9a078a8957d32aaf4f81441a38f4e1e331cc5c9b13d3dcc0d59a80ca06"
assert hashlib.sha256(text_raw).hexdigest() == "e786385cb4203442f0a8e02e7ae1c933d326e202e8acd2fab7ff90478231b6f6"
lines = text_raw.decode("utf-8").splitlines()
starts = []
for pos in range(535, 2388):
    if lines[pos].isdigit() and lines[pos + 1] == "Address" and re.fullmatch(r"0x[0-9a-fA-F]{40}", lines[pos + 2]):
        starts.append(pos)
assert [int(lines[pos]) for pos in starts] == list(range(48))

events = []
for ordinal, start in enumerate(starts):
    end = starts[ordinal + 1] if ordinal + 1 < len(starts) else 2388
    record = lines[start:end]
    topics_pos = record.index("Topics")
    header = " ".join(record[record.index("Name") + 1:topics_pos]) if "Name" in record[:topics_pos] else "UNDECODED"
    events.append({
        "page_event_index": int(record[0]),
        "source_static_text_line_range": [start + 1, end],
        "emitter": record[2],
        "explorer_label": record[3] if record[3].startswith("(") else None,
        "explorer_decoded_header": header,
        "all_displayed_record_lines": record,
        "independent_abi_or_registry_verification": False
    })

def named_address(record, marker):
    start = record.index(marker)
    for value in record[start + 1:]:
        if re.fullmatch(r"0x[0-9a-fA-F]{40}", value):
            return value
    raise ValueError(marker)

transfers = []
for event in events:
    if event["explorer_decoded_header"].startswith("Transfer "):
        record = event["all_displayed_record_lines"]
        transfers.append({
            "page_event_index": event["page_event_index"],
            "token_contract": event["emitter"],
            "token_label_from_explorer": event["explorer_label"],
            "from": named_address(record, "1: from"),
            "to": named_address(record, "2: to"),
            "value_uint256_verbatim": record[record.index("value (uint256) :") + 1],
            "source_static_text_line_range": event["source_static_text_line_range"]
        })
assert len(transfers) == 19

all_events = {"scope": "All48 displayed receipt events of the one fixed transaction", "events": events}
all_transfers = {"scope": "All19 Transfer events; no aggregation, decimal conversion or net quantities", "transfers": transfers}
(ROOT / "receipt-events.all.json").write_text(json.dumps(all_events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "token-transfers.all.json").write_text(json.dumps(all_transfers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "tokens-transferred.visible.static.txt").write_text("\n".join(lines[122:329]) + "\n", encoding="utf-8")
(ROOT / "internal-records.visible.static.txt").write_text("\n".join(lines[518:535]) + "\n", encoding="utf-8")
html_lines = html.splitlines(keepends=True)
fragment = b"".join(html_lines[1969:2807])
(ROOT / "receipt-events.all.raw-fragment.html").write_bytes(fragment)

metadata = {
    "source_url": "https://mantlescan.xyz/tx/0x5165cdcf3363042ec3f6c4c04e64df1a6378dfeb47acfce978560433722e1507",
    "source_html": str(html_path),
    "source_html_sha256": hashlib.sha256(html).hexdigest(),
    "source_text": str(text_path),
    "source_text_sha256": hashlib.sha256(text_raw).hexdigest(),
    "public_source_actions_this_unit": 0,
    "all_receipt_events_count": len(events),
    "event_indices": [event["page_event_index"] for event in events],
    "transfer_events_count": len(transfers),
    "transfer_event_indices": [event["page_event_index"] for event in transfers],
    "undecoded_event_indices": [event["page_event_index"] for event in events if event["explorer_decoded_header"] == "UNDECODED"],
    "events_raw_fragment": "receipt-events.all.raw-fragment.html",
    "events_raw_fragment_source_html_lines": [1970, 2807],
    "events_raw_fragment_sha256": hashlib.sha256(fragment).hexdigest(),
    "internal_call_coverage": "Only page summary/link to279 zero-value internal transactions; individual279 records not present in the saved static text and not fetched.",
    "amount_arithmetic_or_conversion": False,
    "source_js_contract_or_third_party_code_execution": False,
    "own_static_parser_only": True,
    "outputs": {}
}
for name in ["receipt-events.all.json", "token-transfers.all.json", "tokens-transferred.visible.static.txt", "internal-records.visible.static.txt", "receipt-events.all.raw-fragment.html"]:
    data = (ROOT / name).read_bytes()
    metadata["outputs"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
(ROOT / "static-index-receipt.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"events": len(events), "transfers": len(transfers), "undecoded": metadata["undecoded_event_indices"], "financial_arithmetic": False}))
for event in events:
    print(str(event["page_event_index"]) + "\t" + event["emitter"] + "\t" + event["explorer_decoded_header"])
