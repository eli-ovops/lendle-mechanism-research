"""Own offline receipt/event identity parser. No asset-quantity addition/subtraction."""
from pathlib import Path
import json,hashlib,re,collections
BASE=Path(__file__).resolve().parents[2]
OLD=BASE/'lendle-september-receipts-complete-20261020/root'
REG=OLD/'all265-receipt-source-registry.json'
INTERP=OLD/'all265-source-event-interpretation.json'
SCOPE=OLD/'full-source-interpretation-scope.json'
REG_SHA='4a0c4442152f677fe51699d6a51d10f17222575d6b8cea919afd7a291747a753'
INTERP_SHA='58b548346627362d910e8040b34ad6a8c8a9b74c86a3661f5847d18d802a44d6'
SCOPE_SHA='404e8b4363ad3d0a798eddac130d29615a9f9344da974836aabe3ea0fc784e91'
TRANSFER='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
LIQ='0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286'
E='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2'
X='0x5483e9260d84b16ac5a32f2ceb333c762db74718'
F21='0xf21b5df58addd51c8f7984111c5831bdcf20e263'
POOL='0xcfa5ae7c2ce8fadc6426c1ff872ca45378fb7cf3'
sha=lambda b:hashlib.sha256(b).hexdigest()
def index(v):
 assert isinstance(v,str) and re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)',v)
 return int(v,16 if v.startswith('0x') else 10)
def addr(v):
 assert isinstance(v,str) and re.fullmatch(r'0x[0-9a-fA-F]{40}',v)
 return v.lower()
def topic_addr(v):
 assert isinstance(v,str) and re.fullmatch(r'0x0{24}[0-9a-fA-F]{40}',v)
 return '0x'+v[-40:].lower()
def eid(h,i):return '5000:'+h.lower()+':'+str(i)
def sse(b):
 text=b.decode();answers=[]
 if text.lstrip().startswith('{'):return json.loads(text)
 for block in re.split(r'\r?\n\r?\n',text):
  data=[q[5:].lstrip() for q in block.splitlines() if q.startswith('data:')]
  if data:
   z=json.loads('\n'.join(data))
   if isinstance(z,dict) and ('result'in z or 'error'in z):answers.append(z)
 assert len(answers)==1;return answers[0]
def load():
 manifest={}
 def raw(p,expected=None):
  p=Path(p);assert str(p).startswith(str(BASE)+'/') and p.suffix in ('.json','.sse')
  b=p.read_bytes();h=sha(b)
  if expected is not None:assert h==expected,('SOURCE_HASH_CHANGED',str(p))
  manifest[str(p)]={'path':str(p),'bytes':len(b),'sha256':h};return b
 def js(p,h=None):return json.loads(raw(p,h))
 reg=js(REG,REG_SHA);old=js(INTERP,INTERP_SHA);scope=js(SCOPE,SCOPE_SHA)
 assert scope['E']==E and scope['X']==X and scope['F21']==F21 and scope['known_pool']==POOL and scope['reference_Transfer_topic0']==TRANSFER
 normal=js(reg['full_normal_source'],reg['full_normal_source_sha256']);nm={q['row']['hash'].lower():q for q in normal['records']};om={q['hash'].lower():q for q in old['items']}
 assert len(reg['entries'])==len(nm)==len(om)==265 and {q['hash'].lower() for q in reg['entries']}==set(nm)==set(om)
 events=[];anomalies=[];receipts=[];seen={};blockseen={};liquidations={};roles=collections.Counter();all_logs=0
 for pos,entry in enumerate(reg['entries'],1):
  h=entry['hash'].lower();n=nm[h]['row'];request=js(entry['request']);assert request['method']=='tools/call' and request['params']['name']=='get_transaction_receipt' and request['params']['arguments']=={'txhash':h,'chainid':'5000'}
  body=raw(entry['source'],entry['source_sha256']);parsed=js(entry['parsed'],entry['parsed_sha256']);assert sse(body)==parsed
  d=parsed['result']['structuredContent']['data'];assert d['ok'] is True and not parsed['result'].get('isError');r=d['result'];assert isinstance(r,dict)
  assert r['transactionHash'].lower()==h and r['blockHash'].lower()==n['blockHash'].lower() and index(r['blockNumber'])==index(n['blockNumber']) and index(r['transactionIndex'])==index(n['transactionIndex'])
  assert addr(r['from'])==addr(n['from']) and index(r['status'])==index(n['txreceipt_status'])
  creation=n['to'] in ('',None)
  assert (r['to'] in ('',None,'0x') and addr(r['contractAddress'])==addr(n['contractAddress'])) if creation else addr(r['to'])==addr(n['to'])
  role='outgoing' if addr(n['from'])==E else 'incoming' if addr(n['to'])==E else 'UNASSOCIATED';assert role!='UNASSOCIATED';roles[role]+=1
  logs=r['logs'];assert isinstance(logs,list) and not (index(r['status'])==0 and logs)
  receipts.append({'registry_position_1based':pos,'hash':h,'role':role,'status_verbatim':r['status'],'blockHash':r['blockHash'],'blockNumber':r['blockNumber'],'transactionIndex':r['transactionIndex'],'parsed_file':entry['parsed'],'parsed_sha256':entry['parsed_sha256'],'source_file':entry['source'],'source_sha256':entry['source_sha256'],'log_count':len(logs)})
  for lp,l in enumerate(logs):
   all_logs+=1;idx=index(l['logIndex']);key=eid(h,idx)
   assert l['transactionHash'].lower()==h and l['blockHash'].lower()==r['blockHash'].lower() and index(l['blockNumber'])==index(r['blockNumber']) and index(l['transactionIndex'])==index(r['transactionIndex']) and l.get('removed') in (None,False)
   token=addr(l['address']);fingerprint=sha(json.dumps(l,sort_keys=True,separators=(',',':')).encode());assert key not in seen,('DUPLICATE_EVENT_ID',key);seen[key]=fingerprint
   bk=(r['blockHash'].lower(),idx);assert bk not in blockseen or blockseen[bk]==h;blockseen[bk]=h
   topics=l.get('topics');data=l.get('data');assert isinstance(topics,list) and isinstance(data,str)
   if topics and str(topics[0]).lower()==TRANSFER:
    try:
     assert len(topics)==3 and re.fullmatch(r'0x[0-9a-fA-F]{64}',data)
     frm=topic_addr(topics[1]);to=topic_addr(topics[2]);event={'event_id':key,'hash':h,'logIndex_verbatim':l['logIndex'],'logIndex_identity_decimal':idx,'token_contract':token,'from':frm,'to':to,'raw_value_hex':data.lower(),'zero_literal':set(data[2:])=={'0'},'registry_position_1based':pos,'original_receipt_log_position_0based':lp};events.append(event)
    except (AssertionError,TypeError,ValueError) as ex:anomalies.append({'event_id':key,'hash':h,'reason':'TRANSFER_TOPIC_UNSUPPORTED_OR_MALFORMED_STANDARD_ERC20_LAYOUT','raw_log':l,'error':type(ex).__name__})
   if token==POOL and topics and str(topics[0]).lower()==LIQ:
    try:
     assert len(topics)==4 and re.fullmatch(r'0x[0-9a-fA-F]{256}',data)
     collateral=topic_addr(topics[1]);L=topic_addr('0x'+data[2+128:2+192]);assert data[-64:] in ('0'*64,'0'*63+'1')
     liquidations.setdefault(h,[]).append({'event_id':key,'logIndex_identity_decimal':idx,'collateral_token':collateral,'liquidator':L,'amount_words_not_decoded':True})
    except (AssertionError,TypeError,ValueError) as ex:anomalies.append({'event_id':key,'hash':h,'reason':'KNOWN_POOL_LIQUIDATION_ADDRESS_LAYOUT_ANOMALY','raw_log':l,'error':type(ex).__name__})
 assert roles=={'outgoing':262,'incoming':3}
 em={q['event_id']:q for q in events};byhash=collections.defaultdict(list)
 for e in events:byhash[e['hash']].append(e)
 expected=[];cases=[];metadata={}
 for h,o in om.items():
  for t in o['Transfer_source_fields']:
   contract=addr(t['token'])
   for m in t.get('provider_metadata',[]):
    tup=(m.get('name'),m.get('symbol'),m.get('decimals_as_reported'));metadata.setdefault(contract,set()).add(tup)
  if not o['positive_Transfer_toE']:continue
  expected_here=[]
  for t in o['Transfer_source_fields']:
   if addr(t['to'])==E and t['nonzero']:
    k=eid(h,index(t['logIndex']));expected_here.append(k);expected.append(k);a=em.get(k)
    assert a and a['token_contract']==addr(t['token']) and a['from']==addr(t['from']) and a['to']==E and a['raw_value_hex']==t['raw_uint256_hex'].lower() and not a['zero_literal']
  ls=liquidations.get(h,[]);actual_L=sorted({q['liquidator'] for q in ls});assert actual_L==sorted(addr(q) for q in o['observed_liquidator_addresses']) and actual_L
  assert all(any(em[k]['token_contract']==l['collateral_token'] and em[k]['logIndex_identity_decimal']>l['logIndex_identity_decimal'] for l in ls) for k in expected_here)
  cases.append({'hash':h,'liquidations':ls,'actual_liquidators':actual_L,'expected_positive_E_event_ids':expected_here,'per_liquidator_standard_event_ids':{L:[q['event_id'] for q in byhash[h] if L in (q['from'],q['to'])] for L in actual_L},'E_payment_senders_are_observed_liquidators':all(em[k]['from'] in actual_L for k in expected_here)})
 actual=[q['event_id'] for q in events if q['to']==E and q['from']!=E and not q['zero_literal']]
 assert len(cases)==119 and len(expected)==len(set(expected))==119 and set(expected)==set(actual)
 md={t:[{'name':a,'symbol':b,'decimals_as_reported':c} for a,b,c in sorted(v,key=str)] for t,v in metadata.items()}
 return {'manifest':list(manifest.values()),'receipts':receipts,'events':events,'anomalies':anomalies,'cases119':cases,'metadata':md,'counts_only':{'receipt_count':265,'roles':dict(roles),'all_logs':all_logs,'standard_ERC20_Transfer_events':len(events),'unsupported_or_malformed_candidates':len(anomalies),'E_touch_event_count':sum(E in (q['from'],q['to']) for q in events),'F21_touch_event_count':sum(F21 in (q['from'],q['to']) for q in events),'E_self_transfer_event_count':sum(q['from']==E==q['to'] for q in events),'F21_self_transfer_event_count':sum(q['from']==F21==q['to'] for q in events),'positive_E_event_identity_match_count':len(actual),'fixed_cases_with_actual_liquidator_count':len(cases),'unique_actual_liquidator_addresses':len({L for c in cases for L in c['actual_liquidators']}),'provider_metadata_contract_count':len(md)},'quantity_addition_subtraction_or_precision_conversion':False}
