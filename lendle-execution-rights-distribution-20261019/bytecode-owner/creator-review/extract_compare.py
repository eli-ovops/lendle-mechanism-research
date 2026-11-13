"""Own passive HTML/hex/opcode data reader. Does not execute/simulate EVM."""
from pathlib import Path
from html.parser import HTMLParser
import re,json,hashlib,datetime
P=Path(__file__).resolve().parent;R=P.parent.parent/'root'
class Inputs(HTMLParser):
 def __init__(self):super().__init__();self.active=None;self.values={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id') in ('inputdata','rawinput'):self.active=(tag,a['id']);self.values.setdefault(a['id'],'')
 def handle_endtag(self,tag):
  if self.active and tag==self.active[0]:self.active=None
 def handle_data(self,data):
  if self.active:self.values[self.active[1]]+=data
h=Inputs();h.feed((R/'creator-tx.source.html').read_text());inputs={k:v.strip() for k,v in h.values.items()}
assert inputs['inputdata']==inputs['rawinput']
s=inputs['inputdata'];assert re.fullmatch(r'0x[0-9a-fA-F]+',s) and len(s[2:])%2==0
lines=(R/'creator-tx.static-text.txt').read_text().splitlines();matches=[j+1 for j,v in enumerate(lines) if v==s]
assert len(matches)==2
b=bytes.fromhex(s[2:]);r=bytes.fromhex((R/'execution-contract-block0.txt').read_text().strip()[2:])
# Candidate template located by actual byte prefix; explicit constructor CODECOPY constants checked separately.
starts=[m.start() for m in re.finditer(re.escape(r[:128]),b)]
assert len(starts)==1;off=starts[0];template=b[off:off+len(r)];assert len(template)==len(r)
diff=[];j=0
while j<len(r):
 if r[j]==template[j]:j+=1;continue
 k=j
 while j<len(r) and r[j]!=template[j]:j+=1
 diff.append({'runtime_pc_start':k,'runtime_pc_end_exclusive':j,'template_hex':template[k:j].hex(),'runtime_hex':r[k:j].hex()})
patches=[0x1b1f,0x1f52,0x276d,0x2aa0,0x40a2,0x1ccc,0x28a9,0x49c1]
normalized=bytearray(r);words=[]
for pc in patches:
 words.append({'runtime_word_start_pc':hex(pc),'template_word':template[pc:pc+32].hex(),'runtime_word':r[pc:pc+32].hex()})
 assert template[pc:pc+32]==bytes(32)
 normalized[pc:pc+32]=bytes(32)
assert bytes(normalized)==template
# Fixed-length opcode decoder for constructor only; names/operands are descriptions, not executed instructions.
names={0:'STOP',1:'ADD',2:'MUL',3:'SUB',4:'DIV',16:'LT',17:'GT',18:'SLT',19:'SGT',20:'EQ',21:'ISZERO',22:'AND',23:'OR',24:'XOR',25:'NOT',27:'SHL',28:'SHR',32:'KECCAK256',48:'ADDRESS',51:'CALLER',52:'CALLVALUE',53:'CALLDATALOAD',54:'CALLDATASIZE',55:'CALLDATACOPY',56:'CODESIZE',57:'CODECOPY',61:'RETURNDATASIZE',80:'POP',81:'MLOAD',82:'MSTORE',83:'MSTORE8',84:'SLOAD',85:'SSTORE',86:'JUMP',87:'JUMPI',88:'PC',89:'MSIZE',90:'GAS',91:'JUMPDEST',243:'RETURN',253:'REVERT',254:'INVALID'}
ins=[];pc=0
while pc<off:
 op=b[pc];n=op-95 if 96<=op<=127 else 0
 name=f'PUSH{n}' if n else f'DUP{op-127}' if 128<=op<=143 else f'SWAP{op-143}' if 144<=op<=159 else f'LOG{op-160}' if 160<=op<=164 else names.get(op,f'OP_{op:02x}')
 ins.append({'pc':pc,'pc_hex':hex(pc),'name':name,'raw_hex':b[pc:pc+1+n].hex(),'immediate':b[pc+1:pc+1+n].hex() if n else None});pc+=1+n
assert pc==off
(P/'deployment-input.hex.txt').write_text(s+'\n')
(P/'constructor-opcodes.json').write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
sha=lambda x:hashlib.sha256(x).hexdigest()
res={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_chars_including_0x':len(s),'input_bytes':len(b),'input_decoded_sha256':sha(b),'input_source_text_lines':matches,'identical_html_inputdata_and_rawinput':True,'identical_static_text_copies':True,'template_offset_in_input':off,'template_offset_hex':hex(off),'template_bytes':len(template),'template_end_offset_exclusive':off+len(template),'constructor_prefix_bytes':off,'runtime_exact_unmodified_substring_in_input':r in b,'template_sha256':sha(template),'runtime_sha256':sha(r),'normalized_runtime_sha256':sha(bytes(normalized)),'normalized_runtime_matches_template':True,'differing_byte_spans':diff,'patched_word_positions':words,'metadata_last_53_bytes_identical':template[-53:]==r[-53:],'constructor_arguments_raw_hex':b[off+len(template):].hex(),'constructor_arguments_bytes':len(b)-(off+len(template)),'constructor_caller_instructions':[i for i in ins if i['name']=='CALLER'],'constructor_sstore_instructions':[i for i in ins if i['name']=='SSTORE'],'constructor_codecopy_instructions':[i for i in ins if i['name']=='CODECOPY'],'constructor_return_instructions':[i for i in ins if i['name']=='RETURN'],'method':'data parsing, opcode labeling and byte comparison only; no opcode execution/simulation'}
(P/'comparison.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(res,ensure_ascii=False,indent=2))
for lo,hi in [(0x004f,0x0107),(0x0500,0x05a3)]:
 print('OPCODE_WINDOW',hex(lo),hex(hi))
 for i in ins:
  if lo<=i['pc']<hi:print(i['pc_hex'],i['name'],i['immediate'] or '')
