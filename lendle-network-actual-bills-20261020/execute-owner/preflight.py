"""Own offline source identity/structure and visible-literal preflight; no fee arithmetic."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,re,datetime,collections,sys,resource
P=Path(__file__).resolve().parent
B=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence')
R=B/'lendle-september-receipts-complete-20261020/root'
REG=R/'all265-receipt-source-registry.json';BIND=R/'three-published-fee-literals-source-binding.json';PLAN=R/'next-historical-network-bills-plan.md'
META=B/'lendle-september-receipts-batch01-20261020/root/normal-input-native-sponsorship-prefix-check.json'
E='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2';X='0x5483e9260d84b16ac5a32f2ceb333c762db74718'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest={}
def source(p,expected=None):
 p=Path(p);b=p.read_bytes();h=sha(b)
 if expected is not None:assert h==expected,('SOURCE_HASH_CHANGED',str(p))
 manifest[str(p)]={'path':str(p),'bytes':len(b),'sha256':h};return b
def js(p,expected=None):return json.loads(source(p,expected))
def put(name,o):
 b=(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode();assert sum(x.stat().st_size for x in P.iterdir() if x.is_file())+len(b)<8388608
 (P/name).write_bytes(b)
def u(x):
 if isinstance(x,int) and not isinstance(x,bool):assert x>=0;return x
 assert isinstance(x,str) and re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)',x),('INVALID_UINT',type(x).__name__)
 y=int(x,16 if x.startswith('0x') else 10);assert y.bit_length()<=256;return y

def sse(b):
 t=b.decode();a=[]
 if t.lstrip().startswith('{'):return json.loads(t)
 for block in re.split(r'\r?\n\r?\n',t):
  d=[z[5:].lstrip() for z in block.splitlines() if z.startswith('data:')]
  if d:
   o=json.loads('\n'.join(d))
   if isinstance(o,dict) and ('result' in o or 'error' in o):a.append(o)
 assert len(a)==1;return a[0]
class Visible(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def fee_span(text,element):
 starts=[m for m in re.finditer(r'<span\b[^>]*>',text,re.I) if re.search(r'\bid\s*=\s*[\"\x27]'+re.escape(element)+r'[\"\x27]',m.group(),re.I)]
 assert len(starts)==1,('FEE_ELEMENT_COUNT',len(starts));m=starts[0];depth=1;end=None
 for t in re.finditer(r'</?span\b[^>]*>',text[m.end():],re.I):
  depth+=-1 if t.group().startswith('</') else 1
  if depth==0:end=m.end()+t.start();break
 assert end is not None
 inner=text[m.end():end];child=re.match(r'\s*(<span\b[^>]*>.*?</span>)',inner,re.I|re.S);assert child is not None
 actual_fee_child=child.group(1);v=Visible();v.feed(actual_fee_child);visible=' '.join(''.join(v.parts).split());v.close()
 return inner,visible,actual_fee_child

reg=js(REG,'4a0c4442152f677fe51699d6a51d10f17222575d6b8cea919afd7a291747a753')
binding=js(BIND,'153e9431803bb078b2dc8cfa5a44ace1145569dff12d2a2da404c833aa98511e')
source(PLAN,'753491d34aa1088ceb78d4904dc6cb0ea2040ce2b289dbe7ede49a636ebe6af3')
normal=js(reg['full_normal_source'],reg['full_normal_source_sha256']);wrappers=normal['records'];nm={z['row']['hash'].lower():z for z in wrappers}
assert len(nm)==len(wrappers)==265 and len(reg['entries'])==265 and len({x['hash'].lower() for x in reg['entries']})==265
assert {x['hash'].lower() for x in reg['entries']}==set(nm)
meta=js(META,'9fa17333c8a8a66187457b6edec0ac0570bfcc3bf10e545b5b9c44ab2916839f')
assert meta['normal_source_sha256']==reg['full_normal_source_sha256'] and meta['normal_input_count']==265 and meta['invalid_or_missing_input_count']==0 and meta['recognized_meta_prefix_count']==0
mm={z['hash'].lower():z for z in meta['rows']};assert set(mm)==set(nm)
records=[];blobs=[];types=collections.Counter();roles=collections.Counter();fees=['gasUsed','effectiveGasPrice','l1Fee','operatorFeeScalar','operatorFeeConstant'];fields=fees+['l1GasUsed','l1GasPrice','tokenRatio'];fieldcounts={f:collections.Counter() for f in fields}
for z in reg['entries']:
 h=z['hash'].lower();n=nm[h]['row'];req=js(z['request']);a=req['params']['arguments'];assert req['method']=='tools/call' and req['params']['name']=='get_transaction_receipt' and a=={'txhash':h,'chainid':'5000'}
 raw=source(z['source'],z['source_sha256']);parsed=js(z['parsed'],z['parsed_sha256']);assert sse(raw)==parsed
 outer=parsed['result'];d=outer['structuredContent']['data'];assert d['ok'] is True and not outer.get('isError');r=d['result'];assert isinstance(r,dict)
 assert r['transactionHash'].lower()==h and r['blockHash'].lower()==n['blockHash'].lower() and u(r['blockNumber'])==u(n['blockNumber']) and u(r['transactionIndex'])==u(n['transactionIndex'])
 assert r['from'].lower()==n['from'].lower() and u(r['status'])==u(n['txreceipt_status']) and u(r['status']) in (0,1)
 assert u(r['gasUsed'])==u(n['gasUsed']) and u(r['effectiveGasPrice'])==u(n['gasPrice']) and u(r['l1Fee'])==u(n['L1FeesPaid'])
 creation=n['to'] in ('',None)
 assert (r['to'] in ('',None,'0x') and str(r['contractAddress']).lower()==n['contractAddress'].lower()) if creation else r['to'].lower()==n['to'].lower()
 role='E_outgoing' if n['from'].lower()==E else 'E_incoming' if n['to'].lower()==E else 'UNASSOCIATED';assert role!='UNASSOCIATED';roles[role]+=1
 typ=u(r['type']);assert typ in (0,2);assert (typ==2 if role=='E_outgoing' else typ==0);types[r['type']]+=1;u(r['daFootprintGasScalar'])
 assert not any(f in r and r[f] is not None for f in ['depositNonce','depositReceiptVersion'])
 for f in fields:
  assert f in r and r[f] is not None,('MISSING_OR_NULL',h,f);u(r[f]);fieldcounts[f]['present_nonnull']+=1
 inp=n['input'];assert re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*',inp);mi=mm[h];assert mi['input_valid_hex'] and not mi['has_recognized_meta_prefix'] and sha(bytes.fromhex(inp[2:]))==mi['input_sha256']
 xlinked=(n.get('to') or '').lower()==X or (n.get('contractAddress') or '').lower()==X
 rec={'hash':h,'normal_source_page':nm[h]['source_page'],'normal_source_row_1based':nm[h]['source_row_1based'],'parsed_receipt_file':z['parsed'],'parsed_receipt_sha256':z['parsed_sha256'],'role':role,'type_verbatim':r['type'],'receipt_status_verbatim':r['status'],'creation':creation,'X_linked_address_predicate':xlinked,'required_fields_present_nonnull_and_uint_parseable':True,'native_meta_existing_input_sha_match':True,'identity_and_raw_quantity_representation_match':True};records.append(rec)
 blobs.append({'hash':h,'parsed_receipt_file':z['parsed'],'parsed_receipt_sha256':z['parsed_sha256'],'type_verbatim':r['type'],'daFootprintGasScalar':{'present':'daFootprintGasScalar'in r,'nonnull':r.get('daFootprintGasScalar') is not None,'json_type':type(r.get('daFootprintGasScalar')).__name__,'verbatim':r.get('daFootprintGasScalar')},'blobGasUsed':{'present':'blobGasUsed'in r,'json_type':type(r.get('blobGasUsed')).__name__,'verbatim':r.get('blobGasUsed'),'uint_parseable':u(r['blobGasUsed']) is not None if 'blobGasUsed'in r and r['blobGasUsed'] is not None else False,'is_zero_literal':u(r['blobGasUsed'])==0 if 'blobGasUsed'in r and r['blobGasUsed'] is not None else None},'blobGasPrice':{'present':'blobGasPrice'in r,'json_type':type(r.get('blobGasPrice')).__name__,'verbatim':r.get('blobGasPrice')}})
assert roles=={'E_outgoing':262,'E_incoming':3} and types=={'0x0':3,'0x2':262}
assert all(q['daFootprintGasScalar']['nonnull'] and not q['blobGasPrice']['present'] for q in blobs)
three=[]
for z in binding['records']:
 raw=source(z['source_html'],z['source_html_sha256']);inner,visible,child=fee_span(raw.decode(),z['source_element_id'])
 assert visible==z['source_visible_text'] and z['source_raw_fragment']==child
 match=re.fullmatch(r'([0-9]+\.[0-9]{1,18}) MNT',visible);assert match and match.group(1)==z['published_total_fee_literal_MNT']
 assert z['hash'].lower() in nm and z['source_url'].lower().endswith(z['hash'].lower()) and z['hash'].lower() in raw.decode().lower()
 assert next(q for q in records if q['hash']==z['hash'].lower())['role']=='E_outgoing'
 three.append({'case':z['case'],'hash':z['hash'],'source_html':z['source_html'],'source_html_sha256':z['source_html_sha256'],'source_url':z['source_url'],'source_element_id':z['source_element_id'],'source_exact_inner_html':inner,'actual_fee_child_span':child,'outer_usd_button_not_used':True,'visible_text':visible,'published_decimal_literal_MNT':match.group(1),'literal_only_no_integer_conversion_or_fee_calculation':True})
assert len(three)==3
put('three-fee-literal-preflight.json',{'checked_utc':utc(),'records':three,'all_exact_visible_literal_bindings_match':True,'money_calculated':False})
put('blob-field-structure-preflight.json',{'checked_utc':utc(),'purpose':'Actual serialized field evidence; no blob fee inference or new cost term','receipt_count':265,'type_counts':dict(types),'blobGasUsed_nonzero_literal_count':sum(q['blobGasUsed']['is_zero_literal'] is False for q in blobs),'blobGasPrice_present_count':sum(q['blobGasPrice']['present'] for q in blobs),'daFootprintGasScalar_nonnull_count':sum(q['daFootprintGasScalar']['nonnull'] for q in blobs),'serialized_semantics':'ROOT_METHOD_OWNER_CONFIRMED: nonnil DAFootprintGasScalar serialization may use blobGasUsed for DA footprint, not an extra blob charge. No extra fee item. Independent historical binary UNKNOWN.','records':blobs})
put('source-input-manifest.json',{'fixed_before_formal_execution_utc':utc(),'files':list(manifest.values()),'all_existing_public_originals_no_new_network':True})
put('preflight.json',{'status':'SOURCE_IDENTITY_LITERAL_AND_SHAPE_READY_FORMAL_EXECUTION_NOT_STARTED','checked_utc':utc(),'unique_registry_and_normal_hash_count':265,'role_counts':dict(roles),'type_counts':dict(types),'required_eight_fields':{f:dict(v) for f,v in fieldcounts.items()},'deposit_type_or_fields_found':False,'blob_type3_found':False,'blobGasUsed_nonzero_da_footprint_fixed_source_semantics_confirmed_by_root_method_owner':True,'native_meta_existing_fixed_source_check_bound':True,'native_meta_prefix_count':0,'three_fee_HTML_literal_bindings_match':True,'fee_arithmetic_or_amount_aggregation_executed':False,'GO_received':False,'ordinary_Arsia_branch_confirmation':'ROOT_METHOD_OWNER_CONFIRMED_FIXED_SOURCE_CONDITIONAL; all265 DAFootprintGasScalar nonnull; no fourth fee term; exact fixed3 HTML matching still required','historical_node_binary_and_independent_deployment_proof':'UNKNOWN; three bills alignment would only strengthen source consistency','payer_economic_reimbursements':'UNKNOWN; output limited network gross bill','records':records,'actual_model_effort':'UNKNOWN','peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)})
print(json.dumps({'status':'PREFLIGHT_READY_WAITING_ROOT_GO_NO_AMOUNT_EXECUTION','unique':265,'roles':dict(roles),'types':dict(types),'blobGasUsed_nonzero_count':sum(q['blobGasUsed']['is_zero_literal'] is False for q in blobs),'blobGasPrice_present_count':sum(q['blobGasPrice']['present'] for q in blobs),'three_literals':'MATCH','amount_arithmetic':False,'preflight_sha256':sha((P/'preflight.json').read_bytes())},ensure_ascii=False))
