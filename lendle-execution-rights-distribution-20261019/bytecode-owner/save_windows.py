"""Passive evidence-window indexing; no EVM/source execution."""
from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).parent
raw=(p.parent/'root/execution-contract-block0.txt').read_text().strip()
b=bytes.fromhex(raw[2:]);ins=json.loads((p/'opcodes-static.json').read_text())
ranges=[('selector_fa81fdd8_dispatch',0x0188,0x0193),('sample_gate_storage_caller',0x0655,0x0689),('sample_gate_revert_and_alternative_storage',0x0818,0x083d),('f21_constant_1',0x1ccb,0x1cec),('f21_constant_1_context',0x1cc5,0x1d01),('f21_constant_2',0x28a8,0x28c9),('f21_constant_2_context',0x28a2,0x28de),('f21_constant_3',0x49c0,0x49e1),('f21_constant_3_conditional_and_shift',0x49b3,0x4a19),('cbor_metadata',19203,19254),('metadata_length_suffix',19254,19256)]
a=[]
for label,lo,hi in ranges:
 a.append({'label':label,'pc_base':0,'start_pc':lo,'start_pc_hex':hex(lo),'end_pc_exclusive':hi,'end_pc_exclusive_hex':hex(hi),'raw_hex':b[lo:hi].hex(),'sha256_decoded_bytes':hashlib.sha256(b[lo:hi]).hexdigest(),'instructions':[i for i in ins if lo<=i['pc']<hi]})
(p/'evidence-windows.json').write_text(json.dumps({'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'select copied raw byte intervals and static opcode descriptions only','windows':a},ensure_ascii=False,indent=2)+'\n')
for w in a:print(w['label'],w['start_pc_hex'],w['end_pc_exclusive_hex'],w['raw_hex'],w['sha256_decoded_bytes'])
