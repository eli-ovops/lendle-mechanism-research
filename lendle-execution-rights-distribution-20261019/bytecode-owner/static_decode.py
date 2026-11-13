"""Static data decoding only. Does not execute or simulate EVM/source contracts."""
from pathlib import Path
import hashlib,json,re,datetime
P=Path(__file__).parent
SOURCE=P.parent/'root/execution-contract-block0.txt'
raw=SOURCE.read_bytes();text=raw.decode().strip()
assert re.fullmatch(r'0x[0-9a-fA-F]+',text) and len(text[2:])%2==0
code=bytes.fromhex(text[2:]);ml=int.from_bytes(code[-2:],'big');ms=len(code)-2-ml
names={0:'STOP',1:'ADD',2:'MUL',3:'SUB',4:'DIV',5:'SDIV',6:'MOD',8:'ADDMOD',9:'MULMOD',10:'EXP',11:'SIGNEXTEND',16:'LT',17:'GT',18:'SLT',19:'SGT',20:'EQ',21:'ISZERO',22:'AND',23:'OR',24:'XOR',25:'NOT',26:'BYTE',27:'SHL',28:'SHR',29:'SAR',32:'KECCAK256',48:'ADDRESS',49:'BALANCE',50:'ORIGIN',51:'CALLER',52:'CALLVALUE',53:'CALLDATALOAD',54:'CALLDATASIZE',55:'CALLDATACOPY',56:'CODESIZE',57:'CODECOPY',58:'GASPRICE',59:'EXTCODESIZE',60:'EXTCODECOPY',61:'RETURNDATASIZE',62:'RETURNDATACOPY',63:'EXTCODEHASH',64:'BLOCKHASH',65:'COINBASE',66:'TIMESTAMP',67:'NUMBER',68:'PREVRANDAO',69:'GASLIMIT',70:'CHAINID',71:'SELFBALANCE',72:'BASEFEE',80:'POP',81:'MLOAD',82:'MSTORE',83:'MSTORE8',84:'SLOAD',85:'SSTORE',86:'JUMP',87:'JUMPI',88:'PC',89:'MSIZE',90:'GAS',91:'JUMPDEST',95:'PUSH0',240:'CREATE',241:'CALL',242:'CALLCODE',243:'RETURN',244:'DELEGATECALL',245:'CREATE2',250:'STATICCALL',253:'REVERT',254:'INVALID',255:'SELFDESTRUCT'}
separator=code[:ms].rfind(b'\xfe')
assert separator>=0
code_end=separator+1
ins=[];pc=0
while pc<code_end:
 op=code[pc];n=op-95 if 96<=op<=127 else 0
 name=f'PUSH{n}' if n else f'DUP{op-127}' if 128<=op<=143 else f'SWAP{op-143}' if 144<=op<=159 else f'LOG{op-160}' if 160<=op<=164 else names.get(op,f'OP_{op:02x}')
 imm=code[pc+1:pc+1+n]
 ins.append({'pc':pc,'pc_hex':f'0x{pc:04x}','name':name,'bytes':code[pc:pc+1+n].hex(),'immediate':imm.hex() if n else None})
 pc+=1+n
assert pc==code_end
by={i['pc']:j for j,i in enumerate(ins)}
addr=bytes.fromhex('f21b5df58addd51c8f7984111c5831bdcf20e263')
positions=[i for i in range(len(code)) if code.startswith(addr,i)]
selectors=[]
for j,i in enumerate(ins):
 if i['name']=='PUSH4' and j+3<len(ins) and ins[j+1]['name']=='EQ' and ins[j+2]['name'].startswith('PUSH') and ins[j+3]['name']=='JUMPI':
  selectors.append({'selector':'0x'+i['immediate'],'comparison_pc':i['pc'],'comparison_pc_hex':i['pc_hex'],'target_pc':int(ins[j+2]['immediate'],16),'target_pc_hex':hex(int(ins[j+2]['immediate'],16))})
def block(a,b):
 return {'pc_start':a,'pc_start_hex':hex(a),'pc_end_exclusive':b,'pc_end_exclusive_hex':hex(b),'raw_hex':code[a:b].hex(),'sha256_decoded_bytes':hashlib.sha256(code[a:b]).hexdigest(),'instructions':[i for i in ins if a<=i['pc']<b]}
addr_windows=[]
for k in positions:
 containing=next((i for i in ins if i['pc']<k<i['pc']+len(bytes.fromhex(i['bytes']))),None)
 ix=by[containing['pc']] if containing else next(j for j,i in enumerate(ins) if i['pc']>=k)
 a=ins[max(0,ix-12)]['pc'];b=ins[min(len(ins)-1,ix+30)]['pc']
 addr_windows.append({'raw_address_byte_offset':k,'containing_instruction':containing,'window':block(a,b)})
# Tiny definite-length CBOR map reader, no executable code loaded.
m=code[ms:-2]
def read_cbor(pos):
 h=m[pos];pos+=1;major=h>>5;add=h&31
 if add<24:n=add
 else:
  size={24:1,25:2,26:4,27:8}[add];n=int.from_bytes(m[pos:pos+size],'big');pos+=size
 if major in (2,3):
  v=m[pos:pos+n];pos+=n
  return (v if major==2 else v.decode()),pos
 if major==5:
  out={}
  for _ in range(n):
   k,pos=read_cbor(pos);v,pos=read_cbor(pos);out[k]=v
  return out,pos
 if major==0:return n,pos
 raise ValueError((major,n))
cm,readend=read_cbor(0);assert readend==len(m)
def b58(b):
 alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';n=int.from_bytes(b,'big');s=''
 while n:n,r=divmod(n,58);s=alphabet[r]+s
 return alphabet[0]*(len(b)-len(b.lstrip(b'\0')))+s
metadata={'candidate_terminal_invalid_pc':separator,'opaque_pre_cbor_tail_raw_hex':code[code_end:ms].hex(),'opaque_pre_cbor_tail_length':ms-code_end,'cbor_start_pc':ms,'cbor_length_bytes':ml,'suffix_length_raw_hex':code[-2:].hex(),'cbor_raw_hex':m.hex(),'sha256_cbor_bytes':hashlib.sha256(m).hexdigest(),'fields':{k:v.hex() if isinstance(v,bytes) else v for k,v in cm.items()},'solc_semver_from_metadata':'.'.join(str(x) for x in cm.get('solc',b'')),'ipfs_multihash_base58':b58(cm['ipfs']) if 'ipfs' in cm else None,'no_ipfs_request_made':True}
summary={'source_file':str(SOURCE),'source_text_sha256':hashlib.sha256(raw).hexdigest(),'runtime_bytes':len(code),'runtime_sha256_decoded_bytes':hashlib.sha256(code).hexdigest(),'decoded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'linear static opcode and definite-length CBOR data decoding; no EVM execution/simulation','metadata':metadata,'dispatch_selectors':selectors,'f21_raw_occurrences':positions,'f21_instruction_windows':addr_windows,'caller_instruction_pcs':[i['pc'] for i in ins if i['name']=='CALLER'],'sload_instruction_pcs':[i['pc'] for i in ins if i['name']=='SLOAD'],'sstore_instruction_pcs':[i['pc'] for i in ins if i['name']=='SSTORE']}
(P/'static-decoding.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(P/'opcodes-static.json').write_text(json.dumps(ins,indent=2)+'\n')
(P/'runtime.decoded.hex.txt').write_text(code.hex()+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['f21_instruction_windows']},ensure_ascii=False,indent=2))
for w in addr_windows:
 print('F21_WINDOW',json.dumps({k:v for k,v in w.items() if k!='window'}))
 for i in w['window']['instructions']:print(i['pc_hex'],i['name'],i['immediate'] or '')
